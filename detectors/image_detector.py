"""Detector de imágenes generadas por IA.

Usa un modelo preentrenado de Hugging Face (Swin Transformer afinado para
distinguir imágenes reales de imágenes generadas por modelos de difusión).
El modelo se descarga automáticamente la primera vez que se usa.
"""

from __future__ import annotations

from PIL import Image
from transformers import pipeline

# Swin-base afinado sobre imágenes reales vs. generadas (SDXL y similares).
# Etiquetas del modelo: "artificial" (IA) y "human" (real).
DEFAULT_MODEL = "Organika/sdxl-detector"


class ImageDetector:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._pipeline = None

    @property
    def pipeline(self):
        # Carga perezosa: el modelo solo se descarga/carga al primer uso,
        # así la app arranca rápido aunque no se use esta pestaña.
        if self._pipeline is None:
            self._pipeline = pipeline("image-classification", model=self.model_name)
        return self._pipeline

    def predict(self, image: Image.Image) -> dict[str, float]:
        """Devuelve {"Generada por IA": prob, "Real (humana)": prob}."""
        if image.mode != "RGB":
            image = image.convert("RGB")

        results = self.pipeline(image)
        scores = {r["label"].lower(): r["score"] for r in results}

        ai_score = scores.get("artificial", 0.0)
        human_score = scores.get("human", 1.0 - ai_score)

        return {
            "Generada por IA": round(ai_score, 4),
            "Real (humana)": round(human_score, 4),
        }
