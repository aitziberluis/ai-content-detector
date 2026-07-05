# 🕵️ Detector de contenido generado por IA

Aplicación web que detecta si una **imagen** o un **texto** han sido generados
por inteligencia artificial. Interfaz con dos pestañas construida con
[Gradio](https://gradio.app), lista para ejecutar en local o desplegar gratis
en [Hugging Face Spaces](https://huggingface.co/spaces).

## ✨ Qué hace

| Pestaña | Entrada | Salida |
|---|---|---|
| 🖼️ Imagen | Una imagen (JPG, PNG…) | Probabilidad de que sea generada por IA vs. real |
| 📝 Texto | Un texto (≥ 20 palabras) | Probabilidad de que lo haya escrito una IA vs. un humano |

## 🚀 Instalación y uso

```bash
git clone https://github.com/<tu-usuario>/ai-content-detector.git
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
una imagen o un texto se descargarán los modelos (~1 GB); las siguientes
veces cargan de la caché local.

## 🧠 Modelos

| Tarea | Modelo | Arquitectura |
|---|---|---|
| Imagen | [`Organika/sdxl-detector`](https://huggingface.co/Organika/sdxl-detector) | Swin Transformer afinado para real vs. generada por difusión |
| Texto | [`Hello-SimpleAI/chatgpt-detector-roberta`](https://huggingface.co/Hello-SimpleAI/chatgpt-detector-roberta) | RoBERTa afinado sobre el corpus HC3 (humano vs. ChatGPT) |

## ⚠️ Limitaciones honestas

- **Ningún detector es infalible.** Los resultados son probabilidades, no certezas.
- El detector de imágenes pierde fiabilidad con imágenes muy comprimidas,
  recortadas o de generadores muy recientes que el modelo no vio en
  entrenamiento (el problema de **generalización cross-generator**).
- El detector de texto está entrenado principalmente en **inglés** y con
  textos de tipo ChatGPT; textos cortos, muy editados o en otros idiomas
  reducen la precisión.

## 🗺️ Roadmap (fases)

- [x] **Fase 1** — App funcional de punta a punta con modelos preentrenados (este repo).
- [ ] **Fase 2** — Entrenar detector de imágenes propio: baseline ResNet-50 sobre
  píxeles + rama en dominio de frecuencia (transformada de Fourier), con tabla
  comparativa de resultados.
- [ ] **Fase 3** — Evaluación de generalización: entrenar con un generador y
  testear con otros (cross-generator), y robustez ante compresión JPEG,
  desenfoque y baja resolución.
- [ ] **Fase 4** — Explicabilidad: mapa de calor Grad-CAM que señale qué región
  de la imagen disparó la detección.
- [ ] **Fase 5** — Despliegue de la demo en Hugging Face Spaces.

## 📦 Estructura del proyecto

```
ai-content-detector/
├── app.py                     # Interfaz Gradio (2 pestañas)
├── detectors/
│   ├── image_detector.py      # Clasificador imagen real vs. IA
│   └── text_detector.py       # Clasificador texto humano vs. IA
├── requirements.txt
└── README.md
```

## ☁️ Despliegue en Hugging Face Spaces (gratis)

1. Crea un Space nuevo en [huggingface.co/new-space](https://huggingface.co/new-space)
   con SDK **Gradio**.
2. Sube `app.py`, `requirements.txt` y la carpeta `detectors/`.
3. El Space construye e inicia la app automáticamente.

## 📄 Licencia

MIT
