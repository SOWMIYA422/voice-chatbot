# config.py

# Vosk config
VOSK_MODEL_PATH = (
    r"C:\Users\lenovo\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
)
SAMPLE_RATE = 16000

# LLM config
ACTIVE_MODEL = "gemini"  # change here to use gemini

MODEL_PATHS = {
    "phi": r"C:\Users\lenovo\Downloads\Phi-3-mini-4k-instruct-q4.gguf",
    "mistral": r"D:\jd_generator1\mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    # maybe also keep gemini, but it's API-based
}

# Gemini API config
GEMINI_API_KEY = "AIzaSyCN8n0bEesKmM0OxJBIq4aE1nYEsZPXYj8"
GEMINI_MODEL = "gemini-2.5-flash"  # or whichever gemini model you can access
