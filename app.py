"""Detector de contenido generado por IA — imágenes y texto.

Interfaz Gradio con dos pestañas:
  - Imagen: suelta una imagen y se analiza automáticamente con dos modelos
    independientes que dan una "segunda opinión".
  - Texto: pega un texto y obtén un veredicto global más un análisis
    párrafo a párrafo.

Ejecutar en local:  python app.py
"""

import os

import gradio as gr
from PIL import Image

from detectors import ImageEnsemble, TextDetector

image_ensemble = ImageEnsemble()
text_detector = TextDetector()

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")


# ---------------------------------------------------------------------------
# Veredictos en palabras: una probabilidad del 55% no es un veredicto, y la
# interfaz debe reflejarlo. Los umbrales marcan cuándo hablamos con confianza.
# ---------------------------------------------------------------------------

def build_verdict(ai_prob: float, ai_phrase: str, human_phrase: str) -> str:
    pct = round(ai_prob * 100)
    if ai_prob >= 0.80:
        return f"**Muy probablemente {ai_phrase}** ({pct}% de probabilidad)"
    if ai_prob >= 0.60:
        return f"**Posiblemente {ai_phrase}** ({pct}%) — resultado no concluyente"
    if ai_prob >= 0.40:
        return f"**Resultado dudoso** ({pct}% IA / {100 - pct}% {human_phrase}) — no se puede afirmar nada con confianza"
    if ai_prob >= 0.20:
        return f"**Posiblemente {human_phrase}** ({100 - pct}%) — resultado no concluyente"
    return f"**Muy probablemente {human_phrase}** ({100 - pct}% de probabilidad)"


# ---------------------------------------------------------------------------
# Pestaña de imagen
# ---------------------------------------------------------------------------

def analyze_image(image: Image.Image | None):
    # El evento change también salta al borrar la imagen: limpiar resultados.
    if image is None:
        return "", None, ""

    result = image_ensemble.predict(image)
    ai_prob = result["ai_probability"]

    verdict = build_verdict(ai_prob, "generada por IA", "real")
    if result["disagreement"]:
        verdict += (
            "\n\nAtención: los dos modelos discrepan bastante entre sí. "
            "Tómate el resultado combinado con cautela."
        )

    label = {"Generada por IA": ai_prob, "Real (humana)": 1 - ai_prob}

    details_rows = "\n".join(
        f"| `{name}` | {round(prob * 100)}% |"
        for name, prob in result["per_model"].items()
    )
    details = (
        "**Desglose por modelo** (probabilidad de que sea IA):\n\n"
        "| Modelo | Prob. IA |\n|---|---|\n" + details_rows
    )
    return verdict, label, details


# ---------------------------------------------------------------------------
# Pestaña de texto
# ---------------------------------------------------------------------------

def analyze_text(text: str):
    if not text or not text.strip():
        raise gr.Error("Escribe o pega un texto primero.")

    try:
        ai_prob = text_detector.predict_ai_probability(text)
    except ValueError as e:
        raise gr.Error(str(e))

    verdict = build_verdict(ai_prob, "generado por IA", "humano")
    label = {"Generado por IA": ai_prob, "Humano": 1 - ai_prob}

    rows = []
    for i, p in enumerate(text_detector.predict_paragraphs(text), start=1):
        snippet = p["text"][:80] + ("..." if len(p["text"]) > 80 else "")
        pct = round(p["ai_probability"] * 100)
        fiable = "Si" if p["reliable"] else "No (muy corto)"
        rows.append([i, snippet, p["n_words"], f"{pct}%", fiable])

    return verdict, label, rows


# ---------------------------------------------------------------------------
# Ejemplos
# ---------------------------------------------------------------------------

# foto_real: fotografia de Wikimedia Commons; imagen_ia: generada con Stable
# Diffusion; imagen_ia_dificil: tambien IA, pero los dos modelos discrepan
# sobre ella — demuestra en vivo la funcion de "segunda opinion".
IMAGE_EXAMPLES = [
    [os.path.join(EXAMPLES_DIR, name)]
    for name in ("foto_real.jpg", "imagen_ia.png", "imagen_ia_dificil.png")
    if os.path.exists(os.path.join(EXAMPLES_DIR, name))
]

TEXT_EXAMPLE_HUMAN = (
    "Honestly I didn't expect much from this place, we only stopped because "
    "the kids were hungry and it was the first thing off the highway. The "
    "burgers took forever and mine came out cold in the middle.\n\n"
    "That said, the lady at the counter was super nice about it and swapped "
    "it without any fuss. Would I drive out of my way to come back? Probably "
    "not, but if you're stuck on the I-40 at lunchtime you could do worse."
)

TEXT_EXAMPLE_AI = (
    "There are several reasons why the sky appears blue during the day. "
    "The phenomenon is caused by a process called Rayleigh scattering, which "
    "occurs when sunlight enters the Earth's atmosphere and interacts with "
    "gas molecules. Because blue light has a shorter wavelength than other "
    "colors in the visible spectrum, it is scattered in all directions much "
    "more strongly than red or yellow light.\n\n"
    "It is also worth noting that the sky appears red or orange during "
    "sunrise and sunset. This happens because the sunlight has to travel "
    "through a much greater thickness of atmosphere, so most of the blue "
    "light is scattered away before it reaches your eyes, leaving the longer "
    "red wavelengths to dominate the sky's appearance.\n\n"
    "In summary, the color of the sky is determined by the way light "
    "interacts with the atmosphere. Rayleigh scattering explains both the "
    "blue color of the daytime sky and the warm colors we observe at dawn "
    "and dusk."
)

DISCLAIMER = (
    "Ningún detector es infalible: los resultados son probabilidades, no "
    "certezas. Imágenes comprimidas o recortadas y textos cortos o muy "
    "editados reducen la fiabilidad. El detector de texto funciona mejor en "
    "inglés."
)


# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------

with gr.Blocks(title="Detector de contenido IA", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Detector de contenido generado por IA")
    gr.Markdown(
        "Comprueba si una imagen o un texto han sido generados por "
        "inteligencia artificial. La imagen se analiza con dos modelos "
        "independientes; el texto, de forma global y párrafo a párrafo."
    )

    with gr.Tab("Imagen"):
        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(
                    type="pil",
                    label="Suelta una imagen (se analiza automáticamente)",
                )
                if IMAGE_EXAMPLES:
                    gr.Examples(
                        examples=IMAGE_EXAMPLES,
                        inputs=image_input,
                        label="Prueba con un ejemplo (real / IA / caso dificil)",
                    )
            with gr.Column(scale=1):
                image_verdict = gr.Markdown()
                image_label = gr.Label(num_top_classes=2, label="Probabilidades")
                image_details = gr.Markdown()
        image_input.change(
            analyze_image,
            inputs=image_input,
            outputs=[image_verdict, image_label, image_details],
        )

    with gr.Tab("Texto"):
        with gr.Row():
            with gr.Column(scale=1):
                text_input = gr.Textbox(
                    lines=12,
                    label="Pega un texto (mínimo 20 palabras, mejor en inglés)",
                    placeholder="Pega aquí el texto que quieres analizar...",
                )
                text_button = gr.Button("Analizar texto", variant="primary")
                gr.Examples(
                    examples=[[TEXT_EXAMPLE_HUMAN], [TEXT_EXAMPLE_AI]],
                    inputs=text_input,
                    label="Prueba con un ejemplo (reseña humana / texto tipo IA)",
                )
            with gr.Column(scale=1):
                text_verdict = gr.Markdown()
                text_label = gr.Label(num_top_classes=2, label="Probabilidades")
                text_paragraphs = gr.Dataframe(
                    headers=["#", "Párrafo", "Palabras", "Prob. IA", "Fiable"],
                    label="Análisis por párrafos",
                    interactive=False,
                    wrap=True,
                )
        text_button.click(
            analyze_text,
            inputs=text_input,
            outputs=[text_verdict, text_label, text_paragraphs],
        )

    gr.Markdown(f"---\n*{DISCLAIMER}*")

if __name__ == "__main__":
    demo.launch()
