"""Detector de imágenes generadas por IA.

Usa dos modelos preentrenados de Hugging Face como "ensemble de segunda
opinión": cada uno da su probabilidad y se combinan en un veredicto. Si
discrepan mucho, eso también es información útil para el usuario.
Los modelos se descargan automáticamente la primera vez que se usan.
"""

from __future__ import annotations

from PIL import Image
from transformers import pipeline

# Etiquetas de ambos modelos: "artificial" (IA) y "human" (real).
PRIMARY_MODEL = "Organika/sdxl-detector"
SECOND_MODEL = "umm-maybe/AI-image-detector"

# Diferencia entre modelos a partir de la cual avisamos de discrepancia.
DISAGREEMENT_THRESHOLD = 0.35


def _ai_score(results: list[dict]) -> float:
    """Extrae la probabilidad de "generada por IA" de la salida del pipeline,
    tolerando distintos nombres de etiqueta entre modelos."""
    for r in results:
        if r["label"].lower() in ("artificial", "ai", "fake"):
            return r["score"]
    for r in results:
        if r["label"].lower() in ("human", "real"):
            return 1.0 - r["score"]
    return 0.0


class ImageDetector:
    def __init__(self, model_name: str = PRIMARY_MODEL):
        self.model_name = model_name
        self._pipeline = None

    @property
    def pipeline(self):
        # Carga perezosa: el modelo solo se descarga/carga al primer uso,
        # así la app arranca rápido aunque no se use esta pestaña.
        if self._pipeline is None:
            self._pipeline = pipeline("image-classification", model=self.model_name)
        return self._pipeline

    def predict_ai_probability(self, image: Image.Image) -> float:
        if image.mode != "RGB":
            image = image.convert("RGB")
        return _ai_score(self.pipeline(image))


class ImageEnsemble:
    """Ejecuta varios detectores sobre la misma imagen y combina resultados."""

    def __init__(self, model_names: tuple[str, ...] = (PRIMARY_MODEL, SECOND_MODEL)):
        self.detectors = [ImageDetector(name) for name in model_names]

    def predict(self, image: Image.Image) -> dict:
        """Devuelve la probabilidad combinada, la de cada modelo y si discrepan.

        {
            "ai_probability": float,          # media de los modelos
            "per_model": {nombre: float},     # probabilidad IA de cada uno
            "disagreement": bool,             # True si difieren mucho
        }
        """
        per_model = {
            d.model_name: round(d.predict_ai_probability(image), 4)
            for d in self.detectors
        }
        scores = list(per_model.values())
        spread = max(scores) - min(scores)
        return {
            "ai_probability": round(sum(scores) / len(scores), 4),
            "per_model": per_model,
            "disagreement": spread >= DISAGREEMENT_THRESHOLD,
        }
