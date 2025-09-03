"""
Example usage of the extended LMArenaBeta provider
"""

import asyncio

from examples.tests.ExtendedChatCompletion import ExtendedChatCompletion
from g4f.providers.response import JsonConversation

async def main():
    # Example 1: Using the extended class directly
    messages = [
        {
            "role":"system",
            "content":"use indonesian in casual"
        },
        {
            "role": "user", 
            "content": "What is the capital of france?"
        },
        {
            "role":"assistant",
            "content":"Ibukota Prancis adalah Paris."

        },
        {
            "role": "user", 
            "content": "What is the best place on there ?"
        }
    ]
    # messages = [{"role": "user", "content": "How are you"}]
    
    print("Using extended LMArenaBeta providers:")
    # try:
    response = []
    conversation = JsonConversation(id="7334f730-7a87-11f0-bf6d-056a2bfe5df2")
    async for chunk in ExtendedChatCompletion.create_async(
        model= "gpt-4.1-2025-04-14",
        messages= messages,
        provider= "LMArenaBeta",
        stream=True,
        conversation=conversation
    ):
        if isinstance(chunk, str):
            response.append(chunk)
            print(chunk, end="", flush=True)
    print("\n" + "="*50)

    # except Exception as e:
    #     print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())