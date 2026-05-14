import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")
database_url = os.getenv("DATABASE_URL")

print(f"API Key loaded: {api_key is not None}")
