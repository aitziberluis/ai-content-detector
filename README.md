# Detector de contenido generado por IA

Aplicación web que detecta si una **imagen** o un **texto** han sido generados
por inteligencia artificial. Interfaz con dos pestañas construida con
[Gradio](https://gradio.app), lista para ejecutar en local o desplegar gratis
en [Hugging Face Spaces](https://huggingface.co/spaces).

## Qué hace

| Pestaña | Entrada | Salida |
|---|---|---|
| Imagen | Una imagen (JPG, PNG...) — se analiza automáticamente al soltarla | Veredicto en palabras + probabilidades de **dos modelos independientes** (segunda opinión) |
| Texto | Un texto (mínimo 20 palabras) | Veredicto global + **análisis párrafo a párrafo** para detectar fragmentos de IA incrustados en texto humano |

Detalles de diseño:

- **Veredicto en palabras, no solo barras**: un 55% no es un veredicto. La app
  distingue entre "muy probablemente", "posiblemente" y "resultado dudoso"
  según umbrales de confianza.
- **Ensemble de segunda opinión**: la imagen pasa por dos detectores distintos;
  si discrepan mucho entre sí, la app lo avisa en lugar de esconderlo.
- **Ejemplos precargados**: una foto real, una imagen de Stable Diffusion y un
  "caso difícil" en el que los modelos discrepan, más dos textos de muestra,
  para probar la demo en cinco segundos.

## Instalación y uso

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
una imagen o un texto se descargarán los modelos (~1,5 GB); las siguientes
veces cargan de la caché local.

## Modelos

| Tarea | Modelo | Papel |
|---|---|---|
| Imagen | [`Organika/sdxl-detector`](https://huggingface.co/Organika/sdxl-detector) | Detector principal (Swin Transformer afinado para real vs. difusión) |
| Imagen | [`umm-maybe/AI-image-detector`](https://huggingface.co/umm-maybe/AI-image-detector) | Segunda opinión (detector independiente, entrenado con otros datos) |
| Texto | [`Hello-SimpleAI/chatgpt-detector-roberta`](https://huggingface.co/Hello-SimpleAI/chatgpt-detector-roberta) | RoBERTa afinado sobre el corpus HC3 (humano vs. ChatGPT) |

## Limitaciones honestas

- **Ningún detector es infalible.** Los resultados son probabilidades, no certezas.
- Los detectores de imagen pierden fiabilidad con imágenes muy comprimidas,
  recortadas o de generadores muy recientes que no vieron en entrenamiento
  (el problema de **generalización cross-generator**).
- El detector de texto está entrenado principalmente en **inglés** y con
  textos de tipo ChatGPT; textos cortos, muy editados o en otros idiomas
  reducen la precisión.
- Los párrafos de menos de ~15 palabras se analizan pero se marcan como poco
  fiables.

## Roadmap (fases)

- [x] **Fase 1** — App funcional de punta a punta con modelos preentrenados.
- [x] **Fase 1.5** — Mejoras de producto: veredictos en palabras, ensemble de
  segunda opinión para imagen, análisis de texto por párrafos, ejemplos
  precargados, análisis automático al soltar la imagen.
- [ ] **Fase 2** — Entrenar detector de imágenes propio: baseline ResNet-50 sobre
  píxeles + rama en dominio de frecuencia (transformada de Fourier), con tabla
  comparativa de resultados.
- [ ] **Fase 3** — Evaluación de generalización: entrenar con un generador y
  testear con otros (cross-generator), y robustez ante compresión JPEG,
  desenfoque y baja resolución.
- [ ] **Fase 4** — Explicabilidad: mapa de calor Grad-CAM que señale qué región
  de la imagen disparó la detección.
- [ ] **Fase 5** — Despliegue de la demo en Hugging Face Spaces.

## Estructura del proyecto

```
ai-content-detector/
├── app.py                     # Interfaz Gradio (2 pestañas)
├── detectors/
│   ├── image_detector.py      # Ensemble de 2 clasificadores imagen real vs. IA
│   └── text_detector.py       # Clasificador texto humano vs. IA + por párrafos
├── examples/                  # Imágenes de muestra para la demo
├── requirements.txt
└── README.md
```

## Despliegue en Hugging Face Spaces (gratis)

1. Crea una cuenta en [huggingface.co](https://huggingface.co) si no la tienes.
2. Crea un Space nuevo en [huggingface.co/new-space](https://huggingface.co/new-space):
   SDK **Gradio**, hardware **CPU basic** (gratis), visibilidad pública.
3. Sube estos archivos al Space (pestaña "Files" > "Add file"):
   `app.py`, `requirements.txt`, la carpeta `detectors/` y la carpeta `examples/`.
4. El Space construye e inicia la app automáticamente en un par de minutos.
   La URL resultante (`https://huggingface.co/spaces/<tu-usuario>/<nombre>`)
   es la que puedes poner en el CV.

Créditos de las imágenes de ejemplo (todas de Wikimedia Commons): la foto real
es la cascada Hopetoun Falls (CC BY-SA); las dos imágenes de IA fueron creadas
con Stable Diffusion — un paisaje con santuario sintoísta y el conocido
"astronauta a caballo" (dominio público como obras de IA). El "caso difícil"
del astronauta se incluye a propósito: los dos modelos discrepan sobre ella y
la app lo muestra honestamente en vez de esconderlo.

## Licencia

MIT
