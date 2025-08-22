from dotenv import load_dotenv
import os

env_file = ".env.prod" if os.getenv("FLASK_ENV") == "production" else ".env.local"
load_dotenv(env_file)

db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'dbname': os.getenv('DB_NAME'),
    'sslmode': 'require'
}
