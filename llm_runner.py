# llm_runner.py

from config import ACTIVE_MODEL, MODEL_PATHS, GEMINI_API_KEY, GEMINI_MODEL
from ctransformers import AutoModelForCausalLM
import google.generativeai as genai  # ✅ correct import


class LocalLLM:
    def __init__(self):
        if ACTIVE_MODEL.lower() == "gemini":
            # Setup Gemini API client
            self.use_gemini = True
            genai.configure(api_key=GEMINI_API_KEY)
            print(f"[llm] Using Gemini model {GEMINI_MODEL}")
        else:
            # Use local GGUF model
            self.use_gemini = False
            model_type = "llama"  # Phi & Mistral are llama arch
            model_path = MODEL_PATHS[ACTIVE_MODEL]
            print(f"[llm] Loading {ACTIVE_MODEL} from {model_path} (type={model_type})")
            self.llm = AutoModelForCausalLM.from_pretrained(
                model_path, model_type=model_type, gpu_layers=0
            )

    def ask(self, prompt: str) -> str:
        if self.use_gemini:
            # Call Gemini API
            resp = genai.GenerativeModel(GEMINI_MODEL).generate_content(prompt)
            return resp.text
        else:
            # Existing local LLM
            return self.llm(prompt, max_new_tokens=256, stream=False)
