"""Detector de texto generado por IA.

Usa un RoBERTa afinado por el equipo Hello-SimpleAI (proyecto HC3) para
distinguir texto humano de texto generado por modelos tipo ChatGPT.
Funciona mejor con textos en inglés de al menos ~50 palabras.
"""

from __future__ import annotations

from transformers import pipeline

# Etiquetas del modelo: "Human" y "ChatGPT".
DEFAULT_MODEL = "Hello-SimpleAI/chatgpt-detector-roberta"

MIN_WORDS = 20


class TextDetector:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._pipeline = None

    @property
    def pipeline(self):
        # Carga perezosa, igual que en ImageDetector.
        if self._pipeline is None:
            self._pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                truncation=True,
                max_length=512,
            )
        return self._pipeline

    def predict(self, text: str) -> dict[str, float]:
        """Devuelve {"Generado por IA": prob, "Humano": prob}.

        Lanza ValueError si el texto es demasiado corto para dar una
        predicción con alguna garantía.
        """
        text = text.strip()
        n_words = len(text.split())
        if n_words < MIN_WORDS:
            raise ValueError(
                f"El texto tiene {n_words} palabras; se necesitan al menos "
                f"{MIN_WORDS} para una predicción fiable."
            )

        results = self.pipeline(text, top_k=None)
        scores = {r["label"].lower(): r["score"] for r in results}

        ai_score = scores.get("chatgpt", 0.0)
        human_score = scores.get("human", 1.0 - ai_score)

        return {
            "Generado por IA": round(ai_score, 4),
            "Humano": round(human_score, 4),
        }
