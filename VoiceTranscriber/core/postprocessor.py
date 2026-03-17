import json
import httpx


# Provider configurations with base URLs and default models
PROVIDER_CONFIGS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "models": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"],
    },
    "xAI": {
        "base_url": "https://api.x.ai/v1",
        "models": ["grok-3", "grok-3-mini", "grok-2"],
    },
    "Groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "Ollama": {
        "base_url": "http://localhost:11434/v1",
        "models": ["llama3.2", "mistral", "gemma2", "phi3"],
    },
    "Custom": {
        "base_url": "",
        "models": [],
    },
}

DEFAULT_PROMPT = (
    "Du bist ein Textoptimierer. Korrigiere Grammatik, Rechtschreibung und Zeichensetzung. "
    "Entferne Fuellwoerter und Wiederholungen. Behalte den Inhalt und Stil bei. "
    "Antworte NUR mit dem korrigierten Text, ohne Erklaerungen."
)


class PostProcessor:
    """LLM-based post-processing of transcribed text."""

    def __init__(self):
        self.client = None
        self.provider_type = None
        self.model = None
        self.prompt = DEFAULT_PROMPT

    def configure(self, provider_type, api_key, base_url=None, model=None, prompt=None):
        from openai import OpenAI

        config = PROVIDER_CONFIGS.get(provider_type, PROVIDER_CONFIGS["Custom"])
        url = base_url or config["base_url"]
        self.model = model or (config["models"][0] if config["models"] else "")
        self.provider_type = provider_type
        if prompt:
            self.prompt = prompt

        self.client = OpenAI(
            api_key=api_key or "not-needed",
            base_url=url,
            timeout=30.0,
        )

    def process(self, text):
        """Post-process text through configured LLM. Returns processed text."""
        if not self.client or not text.strip():
            return text

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Fehler: {e}]\n\n{text}"

    def test_connection(self):
        """Test if the provider connection works. Returns (success, message)."""
        if not self.client:
            return False, "Kein Provider konfiguriert"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Antworte mit OK"}],
                max_tokens=10,
            )
            return True, f"Verbindung OK - Modell: {self.model}"
        except Exception as e:
            return False, str(e)
