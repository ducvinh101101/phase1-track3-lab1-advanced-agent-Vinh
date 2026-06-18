import json
from pathlib import Path
import typer
from rich import print
from src.reflexion_lab.agents import ReActAgent, ReflexionAgent
from src.reflexion_lab.reporting import build_report, save_report
from src.reflexion_lab.utils import load_dataset, save_jsonl

app = typer.Typer(add_completion=False)

@app.command()
def main(dataset: str = "data/hotpot_mini.json", out_dir: str = "outputs/sample_run", reflexion_attempts: int = 3) -> None:
    examples = load_dataset(dataset)
    react = ReActAgent()
    reflexion = ReflexionAgent(max_attempts=reflexion_attempts)
    
    total = len(examples)
    print(f"[bold green]Loaded {total} examples from {dataset}.[/bold green]\n")
    
    print("[bold blue]>>> Phase 1: Running ReAct Agent[/bold blue]")
    react_records = []
    for idx, example in enumerate(examples, 1):
        print(f"  [{idx}/{total}] QID: {example.qid} | Difficulty: {example.difficulty} | ReAct running...")
        record = react.run(example)
        correct_color = "green" if record.is_correct else "red"
        print(f"    -> Answer: '{record.predicted_answer}' | Correct: [{correct_color}]{record.is_correct}[/{correct_color}] | Latency: {record.latency_ms}ms")
        react_records.append(record)
        
    print("\n[bold blue]>>> Phase 2: Running Reflexion Agent[/bold blue]")
    reflexion_records = []
    for idx, example in enumerate(examples, 1):
        print(f"  [{idx}/{total}] QID: {example.qid} | Difficulty: {example.difficulty} | Reflexion running...")
        record = reflexion.run(example)
        correct_color = "green" if record.is_correct else "red"
        print(f"    -> Answer: '{record.predicted_answer}' | Correct: [{correct_color}]{record.is_correct}[/{correct_color}] | Attempts: {record.attempts} | Latency: {record.latency_ms}ms")
        reflexion_records.append(record)
        
    all_records = react_records + reflexion_records
    out_path = Path(out_dir)
    save_jsonl(out_path / "react_runs.jsonl", react_records)
    save_jsonl(out_path / "reflexion_runs.jsonl", reflexion_records)
    
    report = build_report(all_records, dataset_name=Path(dataset).name, mode="llm")
    json_path, md_path = save_report(report, out_path)
    print(f"\n[bold green]Saved[/bold green] {json_path}")
    print(f"[bold green]Saved[/bold green] {md_path}")
    print(json.dumps(report.summary, indent=2))

if __name__ == "__main__":
    app()
