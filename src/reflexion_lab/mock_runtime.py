from __future__ import annotations
import re
import json
import time
from openai import OpenAI
from .schemas import QAExample, JudgeResult, ReflectionEntry
from .utils import normalize_answer
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM

FIRST_ATTEMPT_WRONG = {"hp2": "London", "hp4": "Atlantic Ocean", "hp6": "Red Sea", "hp8": "Andes"}
FAILURE_MODE_BY_QID = {"hp2": "incomplete_multi_hop", "hp4": "wrong_final_answer", "hp6": "entity_drift", "hp8": "entity_drift"}

# Initialize OpenAI client pointing to the target endpoint
client = OpenAI(
    api_key="",
    base_url="https://swore-explode-thievish.ngrok-free.dev/v1"
)
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

# Global Tracker for Token estimation and Latency measurement
class LLMCallTracker:
    def __init__(self) -> None:
        self.tokens = 0
        self.latency_ms = 0
    def reset(self) -> None:
        self.tokens = 0
        self.latency_ms = 0

tracker = LLMCallTracker()

def extract_fields_via_regex(text: str) -> dict:
    data = {}
    
    # 1. Extract score
    score_match = re.search(r'"score"\s*:\s*(\d)', text)
    if score_match:
        data["score"] = int(score_match.group(1))
    else:
        data["score"] = 0
        
    # 2. Extract reason
    reason_match = re.search(r'"reason"\s*:\s*"(.*?)"\s*(?:,|\n|\})', text, re.DOTALL)
    if reason_match:
        data["reason"] = reason_match.group(1).replace('"', "'")
    else:
        reason_match_greedy = re.search(r'"reason"\s*:\s*"(.*)"', text)
        if reason_match_greedy:
            content = reason_match_greedy.group(1)
            for stop_word in ['"missing_evidence"', '"spurious_claims"', '"next_strategy"']:
                if stop_word in content:
                    content = content.split(stop_word)[0].strip().rstrip(',').rstrip('"')
            data["reason"] = content.replace('"', "'")
        else:
            data["reason"] = "Failed to parse reason."

    # 3. Extract missing_evidence
    me_match = re.search(r'"missing_evidence"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if me_match:
        items_str = me_match.group(1)
        items = re.findall(r'"(.*?)"', items_str)
        if not items and items_str.strip():
            items = [x.strip().strip('"').strip("'") for x in items_str.split(',')]
        data["missing_evidence"] = [item.replace('"', "'") for item in items if item.strip()]
    else:
        data["missing_evidence"] = []

    # 4. Extract spurious_claims
    sc_match = re.search(r'"spurious_claims"\s*:\s*\[(.*?)\]', text, re.DOTALL)
    if sc_match:
        items_str = sc_match.group(1)
        items = re.findall(r'"(.*?)"', items_str)
        if not items and items_str.strip():
            items = [x.strip().strip('"').strip("'") for x in items_str.split(',')]
        data["spurious_claims"] = [item.replace('"', "'") for item in items if item.strip()]
    else:
        data["spurious_claims"] = []

    # 5. Extract failure_reason, lesson, next_strategy
    for field in ["failure_reason", "lesson", "next_strategy"]:
        match = re.search(rf'"{field}"\s*:\s*"(.*?)"\s*(?:,|\n|\}})', text, re.DOTALL)
        if match:
            data[field] = match.group(1).replace('"', "'")
        else:
            match_greedy = re.search(rf'"{field}"\s*:\s*"(.*)"', text)
            if match_greedy:
                content = match_greedy.group(1)
                for stop_word in ['"lesson"', '"next_strategy"', '"attempt_id"']:
                    if stop_word in content:
                        content = content.split(stop_word)[0].strip().rstrip(',').rstrip('"')
                data[field] = content.replace('"', "'")
            else:
                data[field] = f"Failed to parse {field}."
                
    # 6. Extract attempt_id
    aid_match = re.search(r'"attempt_id"\s*:\s*(\d+)', text)
    if aid_match:
        data["attempt_id"] = int(aid_match.group(1))
    else:
        data["attempt_id"] = 1

    return data

def parse_json_response(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        clean_text = match.group(0)
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            return extract_fields_via_regex(clean_text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return extract_fields_via_regex(text)

def filter_context(question: str, context: list[dict], max_chars: int = 2000) -> list[dict]:
    # Stopwords in English to exclude from keyword overlap calculation
    stopwords = {"what", "which", "who", "where", "when", "how", "why", "the", "a", "an", "of", "in", "on", "at", "to", "for", "with", "by", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "from", "up", "down", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "and", "or", "but", "if", "then", "else", "than", "as", "until", "while"}
    
    # Extract query words
    q_words = set(re.findall(r"\w+", question.lower())) - stopwords
    
    ranked_chunks = []
    for chunk in context:
        title_words = set(re.findall(r"\w+", chunk.title.lower())) - stopwords
        text_words = set(re.findall(r"\w+", chunk.text.lower())) - stopwords
        
        # Calculate overlap score
        score = len(q_words.intersection(text_words))
        # Give a large boost if query words match title words
        score += len(q_words.intersection(title_words)) * 3
        
        ranked_chunks.append((score, chunk))
        
    # Sort by score in descending order
    ranked_chunks.sort(key=lambda x: x[0], reverse=True)
    
    selected_chunks = []
    current_chars = 0
    # Always keep at least 2 chunks for multi-hop QA, up to max_chars limit
    for score, chunk in ranked_chunks:
        chunk_len = len(chunk.title) + len(chunk.text)
        if current_chars + chunk_len <= max_chars or len(selected_chunks) < 2:
            selected_chunks.append(chunk)
            current_chars += chunk_len
            if current_chars > max_chars and len(selected_chunks) >= 2:
                break
        else:
            break
            
    return selected_chunks

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> str:
    # Filter context to keep the top relevant chunks and reduce input size
    filtered_context = filter_context(example.question, example.context)
    
    context_str = ""
    for chunk in filtered_context:
        context_str += f"Title: {chunk.title}\nText: {chunk.text}\n---\n"
    
    ref_mem_str = ""
    if reflection_memory:
        ref_mem_str = "\nReflection Memory (Lessons from previous failed attempts):\n"
        for idx, mem in enumerate(reflection_memory, 1):
            ref_mem_str += f"{idx}. {mem}\n"
            
    prompt = f"Context:\n{context_str}\nQuestion: {example.question}\n{ref_mem_str}\nAnswer the question directly and concisely."
    
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": ACTOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=300
    )
    latency = int((time.perf_counter() - t0) * 1000)
    tokens = response.usage.total_tokens
    
    tracker.tokens += tokens
    tracker.latency_ms += latency
    
    return response.choices[0].message.content.strip()

def evaluator(example: QAExample, answer: str) -> JudgeResult:
    prompt = (
        f"Question: {example.question}\n"
        f"Gold Answer: {example.gold_answer}\n"
        f"Predicted Answer: {answer}\n"
    )
    
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": EVALUATOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=400,
        response_format={"type": "json_object"}
    )
    latency = int((time.perf_counter() - t0) * 1000)
    tokens = response.usage.total_tokens
    
    tracker.tokens += tokens
    tracker.latency_ms += latency
    
    raw_content = response.choices[0].message.content.strip()
    data = parse_json_response(raw_content)
    
    return JudgeResult(
        score=int(data.get("score", 0)),
        reason=str(data.get("reason", "No reason provided.")),
        missing_evidence=data.get("missing_evidence", []),
        spurious_claims=data.get("spurious_claims", [])
    )

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> ReflectionEntry:
    prompt = (
        f"Question: {example.question}\n"
        f"Failed Attempt ID: {attempt_id}\n"
        f"Evaluator Feedback:\n"
        f"- Reason: {judge.reason}\n"
        f"- Missing Evidence: {judge.missing_evidence}\n"
        f"- Spurious Claims: {judge.spurious_claims}\n"
    )
    
    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": REFLECTOR_SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=400,
        response_format={"type": "json_object"}
    )
    latency = int((time.perf_counter() - t0) * 1000)
    tokens = response.usage.total_tokens
    
    tracker.tokens += tokens
    tracker.latency_ms += latency
    
    raw_content = response.choices[0].message.content.strip()
    data = parse_json_response(raw_content)
    
    return ReflectionEntry(
        attempt_id=attempt_id,
        failure_reason=str(data.get("failure_reason", judge.reason)),
        lesson=str(data.get("lesson", "No lesson provided.")),
        next_strategy=str(data.get("next_strategy", "Try another reasoning path."))
    )
