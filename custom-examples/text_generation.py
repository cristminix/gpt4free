from g4f.client import Client

client = Client()
response = client.chat.completions.create(
    model="mixtral-8x22b-instruct-v0.1",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
    web_search=False
)
print(response.choices[0].message.content)