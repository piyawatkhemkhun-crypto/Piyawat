import os

class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "game_recommendation_secret_key_secure_v7"
    )