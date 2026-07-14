import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IMAGEKIT_API_PUBLIC_KEY = os.getenv("IMAGEKIT_API_PUBLIC_KEY")
IMAGEKIT_API_PRIVATE_KEY = os.getenv("IMAGEKIT_API_PRIVATE_KEY")
IMAGEKIT_API_URL_ENDPOINT = os.getenv("IMAGEKIT_API_URL_ENDPOINT")


DATABASE_URL = "sqlite:///./thumbnailbuilder.db"