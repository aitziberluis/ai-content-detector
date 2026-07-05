# Detector de contenido generado por IA

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Gradio](https://img.shields.io/badge/Gradio-4.x-orange)
![License](https://img.shields.io/badge/Licencia-MIT-green)

Aplicación web que estima si una **imagen** o un **texto** han sido generados
por inteligencia artificial. Construida con [Gradio](https://gradio.app) y
modelos de Hugging Face, pensada para ejecutarse en local o desplegarse gratis
en Hugging Face Spaces.

## Qué hace

**Pestaña Imagen** — suelta una imagen y se analiza automáticamente con
**dos detectores independientes** que actúan como primera y segunda opinión.
Se muestra el veredicto combinado, el desglose por modelo y un aviso explícito
cuando los modelos discrepan entre sí.

**Pestaña Texto** — pega un texto (mínimo 20 palabras) y obtienes un veredicto
global más un **análisis párrafo a párrafo**, útil para el caso realista de un
texto humano con fragmentos de IA incrustados.

## Decisiones de diseño

- **Veredictos en palabras, no solo porcentajes.** Un 55% no es un veredicto:
  la app distingue entre "muy probablemente" (>80%), "posiblemente,
  no concluyente" (60-80%) y "resultado dudoso" (40-60%).
- **La discrepancia es información.** Si los dos detectores de imagen no se
  ponen de acuerdo, la app lo dice en lugar de esconderlo tras una media.
  Uno de los ejemplos precargados (el astronauta de Stable Diffusion) está
  elegido a propósito porque los modelos discrepan sobre él.
- **Rechazar antes que inventar.** Los textos de menos de 20 palabras se
  rechazan y los párrafos muy cortos se marcan como poco fiables, porque
  ningún detector puede decir nada serio con tan poco contexto.

## Instalación y uso

```bash
git clone https://github.com/aitziberluis/ai-content-detector.git
cd ai-content-detector

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Abre `http://127.0.0.1:7860` en el navegador. La primera vez que analices
una imagen o un texto se descargarán los modelos (~1,5 GB); después cargan
de la caché local.

## Modelos

| Tarea | Modelo | Papel |
|---|---|---|
| Imagen | [`Organika/sdxl-detector`](https://huggingface.co/Organika/sdxl-detector) | Detector principal (Swin Transformer, real vs. difusión) |
| Imagen | [`umm-maybe/AI-image-detector`](https://huggingface.co/umm-maybe/AI-image-detector) | Segunda opinión, entrenado con otros datos |
| Texto | [`Hello-SimpleAI/chatgpt-detector-roberta`](https://huggingface.co/Hello-SimpleAI/chatgpt-detector-roberta) | RoBERTa afinado sobre el corpus HC3 (humano vs. ChatGPT) |

## Limitaciones

- Los resultados son **probabilidades, no certezas**; ningún detector es infalible.
- Los detectores de imagen pierden fiabilidad con imágenes muy comprimidas,
  recortadas o de generadores que no vieron en entrenamiento (el problema de
  **generalización cross-generator** — es la debilidad número uno de todos los
  detectores actuales).
- El detector de texto está entrenado principalmente en **inglés**; textos
  cortos, muy editados o en otros idiomas reducen la precisión.

## Roadmap

- [x] App funcional de punta a punta con modelos preentrenados
- [x] Veredictos con umbrales de confianza, ensemble de segunda opinión y
  análisis por párrafos
- [ ] Despliegue de la demo en Hugging Face Spaces
- [ ] Detector de imágenes propio: baseline ResNet-50 + rama en dominio de
  frecuencia (transformada de Fourier), con tabla comparativa
- [ ] Evaluación cross-generator y robustez ante compresión JPEG, desenfoque
  y baja resolución
- [ ] Explicabilidad con Grad-CAM: qué región de la imagen disparó la detección

## Estructura

```
ai-content-detector/
├── app.py                     # Interfaz Gradio (2 pestañas)
├── detectors/
│   ├── image_detector.py      # Ensemble de 2 clasificadores imagen real vs. IA
│   └── text_detector.py       # Clasificador de texto global + por párrafos
├── examples/                  # Imágenes de muestra para la demo
└── requirements.txt
```

## Créditos

Las imágenes de ejemplo proceden de Wikimedia Commons:

- `foto_real.jpg` — cascada Hopetoun Falls (Australia), fotografía real, licencia CC BY-SA
- `imagen_ia.png` — paisaje con santuario sintoísta, generado con Stable Diffusion
- `imagen_ia_dificil.png` — el conocido "astronauta a caballo", generado con Stable Diffusion

## Licencia

MIT — puedes usar este código libremente citando la fuente.
