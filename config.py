import os
from dotenv import load_dotenv

# Solo carga el archivo .env si estás en entorno local
if os.getenv("FLASK_ENV") != "production":
    load_dotenv(".env.local")

db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'dbname': os.getenv('DB_NAME'),
    'sslmode': 'require'
}
