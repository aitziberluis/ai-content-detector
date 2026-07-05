"""Detector de texto generado por IA.

Usa un RoBERTa afinado por el equipo Hello-SimpleAI (proyecto HC3) para
distinguir texto humano de texto generado por modelos tipo ChatGPT.
Funciona mejor con textos en inglés de al menos ~50 palabras.

Además del veredicto global, puede analizar el texto párrafo a párrafo,
para detectar el caso realista de "texto humano con párrafos de IA
incrustados".
"""

from __future__ import annotations

import re

from transformers import pipeline

# Etiquetas del modelo: "Human" y "ChatGPT".
DEFAULT_MODEL = "Hello-SimpleAI/chatgpt-detector-roberta"

MIN_WORDS = 20
# Un párrafo más corto que esto se analiza igualmente, pero se marca
# como poco fiable en vez de descartarse.
MIN_PARAGRAPH_WORDS = 15


def _ai_score(results: list[dict]) -> float:
    for r in results:
        if r["label"].lower() in ("chatgpt", "ai", "fake"):
            return r["score"]
    for r in results:
        if r["label"].lower() in ("human", "real"):
            return 1.0 - r["score"]
    return 0.0


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

    def predict_ai_probability(self, text: str) -> float:
        """Probabilidad de que el texto completo sea generado por IA.

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
        return _ai_score(self.pipeline(text, top_k=None))

    def predict_paragraphs(self, text: str) -> list[dict]:
        """Analiza el texto párrafo a párrafo.

        Devuelve una lista de dicts:
        {
            "text": str,            # el párrafo
            "n_words": int,
            "ai_probability": float,
            "reliable": bool,       # False si el párrafo es muy corto
        }
        """
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        results = []
        for p in paragraphs:
            n_words = len(p.split())
            results.append(
                {
                    "text": p,
                    "n_words": n_words,
                    "ai_probability": round(_ai_score(self.pipeline(p, top_k=None)), 4),
                    "reliable": n_words >= MIN_PARAGRAPH_WORDS,
                }
            )
        return results
