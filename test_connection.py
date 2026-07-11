from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL:", DATABASE_URL)
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful. Result:", result.fetchone())
except Exception as e:
    print("Error occurred while testing database connection:", e)