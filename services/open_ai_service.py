import base64
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_image(prompt: str, style_prompt: str, headshot_url: str) -> bytes:
    """ """

    full_prompt = (
        f"{style_prompt}\n\n"
        f"User request: {prompt}\n\n"
        "IMPORTANT: The image should be a headshot of the person in the provided headshot_url. "

    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": full_prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": headshot_url
                    }

                ]

            }
        ],
        tools=[
            {
            "type": "image_generation",
            "model": "gpt-image-1",
            "size": "1024x1024",
            "quality": "low",
            "output_format": "png",

            },
        ]
    )

    for item in response.output:
        if item.type == "image_generation_call" and item.result :
            return base64.b64decode(item.result)
        
    raise RuntimeError("No image generated in the response.")



