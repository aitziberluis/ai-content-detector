"""Detector de contenido generado por IA — imágenes y texto.

Interfaz Gradio con dos pestañas:
  - Imagen: sube una imagen y obtén la probabilidad de que sea generada por IA.
  - Texto: pega un texto y obtén la probabilidad de que lo haya escrito una IA.

Ejecutar en local:  python app.py
"""

import gradio as gr
from PIL import Image

from detectors import ImageDetector, TextDetector

image_detector = ImageDetector()
text_detector = TextDetector()


def analyze_image(image: Image.Image | None):
    if image is None:
        raise gr.Error("Sube una imagen primero.")
    return image_detector.predict(image)


def analyze_text(text: str):
    if not text or not text.strip():
        raise gr.Error("Escribe o pega un texto primero.")
    try:
        return text_detector.predict(text)
    except ValueError as e:
        raise gr.Error(str(e))


DISCLAIMER = (
    "⚠️ Ningún detector es infalible: los resultados son probabilidades, "
    "no certezas. Imágenes comprimidas/recortadas y textos cortos o muy "
    "editados reducen la fiabilidad. El detector de texto funciona mejor "
    "en inglés."
)

with gr.Blocks(title="Detector de contenido IA") as demo:
    gr.Markdown("# 🕵️ Detector de contenido generado por IA")
    gr.Markdown(
        "Comprueba si una **imagen** o un **texto** han sido generados por "
        "inteligencia artificial."
    )

    with gr.Tab("🖼️ Imagen"):
        with gr.Row():
            with gr.Column():
                image_input = gr.Image(type="pil", label="Sube una imagen")
                image_button = gr.Button("Analizar imagen", variant="primary")
            image_output = gr.Label(num_top_classes=2, label="Resultado")
        image_button.click(analyze_image, inputs=image_input, outputs=image_output)

    with gr.Tab("📝 Texto"):
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    lines=10,
                    label="Pega un texto (mínimo ~20 palabras, mejor en inglés)",
                    placeholder="Pega aquí el texto que quieres analizar...",
                )
                text_button = gr.Button("Analizar texto", variant="primary")
            text_output = gr.Label(num_top_classes=2, label="Resultado")
        text_button.click(analyze_text, inputs=text_input, outputs=text_output)

    gr.Markdown(DISCLAIMER)

if __name__ == "__main__":
    demo.launch()
