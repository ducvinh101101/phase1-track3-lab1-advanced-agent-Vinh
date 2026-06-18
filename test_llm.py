from openai import OpenAI

client = OpenAI(
    api_key="",
    base_url="https://swore-explode-thievish.ngrok-free.dev/v1"
)

print(client.models.list())

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-3B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "Xin chào, hãy giới thiệu bản thân."
        }
    ],
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)