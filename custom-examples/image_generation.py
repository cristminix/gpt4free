from g4f.client import Client

client = Client()
response = client.images.generate(
    model="flux",
    prompt="Cewek hijab tobrut, anime style, cute, beautiful, wearing a hijab, smiling, detailed eyes, vibrant colors",
    response_format="url"
)

print(f"Generated image URL: {response.data[0].url}")