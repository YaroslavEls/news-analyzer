import os
import joblib
from dotenv import load_dotenv
load_dotenv()


def load_model():
    return joblib.load(os.getenv('MODEL_FILE'))
