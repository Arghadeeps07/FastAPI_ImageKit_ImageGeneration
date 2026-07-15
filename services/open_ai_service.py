import base64
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_image(prompt: str, style_prompt: str, headshot_url: str) -> bytes:
    """ """

    full_prompt = (
        "Using the attached reference photo, generate a new professional headshot of the same "
        "person. Preserve their exact facial identity, facial structure, skin tone, and hair "
        "(same person, recognizable as them) — only change the lighting, background, framing, "
        "and expression as described below. Head-and-shoulders crop, photorealistic, high detail, "
        "single subject, no text or watermarks, no distortion of facial features or anatomy.\n\n"
        f"{style_prompt}\n\n"
        f"Additional user request: {prompt}"
    )

    response = await client.responses.create(
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



