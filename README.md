# AetherSim 🌌

**AetherSim** es un simulador de partículas altamente optimizado e interactivo, controlado íntegramente mediante gestos de la mano.

Al combinar la brutal velocidad de cálculo de **Rust** con la flexibilidad y el ecosistema de IA de **Python**, el proyecto es capaz de simular las físicas y el renderizado visual de cientos de miles de partículas de manera asíncrona a 60 Fotogramas por Segundo.

---

## 🏗️ Arquitectura Técnica

El proyecto está diseñado bajo una arquitectura de lenguajes híbridos, usando FFI (Foreign Function Interfaces) para la transferencia de datos a coste cero.

### Backend de Físicas (Rust)
* **Librería Core (`aether_core`)**: Construida con PyO3. Posee un objeto de simulación estado persistente (`Simulacion`).
* **Matemáticas**: Calcula en cada _tick_ un modelo gravitacional para las partículas, evaluando la tracción, repulsión, fricción (`drag`) y el sistema de colisiones con los bordes de la pantalla.
* **Integración de Memoria**: Devuelve punteros de memoria transformados en `numpy::PyArray1` para evitar la sobrecarga de copias al enviar las coordenadas de regreso a Python.

### Frontend y Visión Artificial (Python)
* **Reconocimiento Óptico (MediaPipe)**: Implementa el modelo pre-entrenado `hand_landmarker.task` en su modo `RunningMode.VIDEO` (que brinda rastreo temporal).
* **Heurísticas Lógicas**: A través de análisis euclidiano entre las falanges y nudillos (puntos de articulación intermedios / PIP), Python infiere en tiempo real los gestos del usuario.
* **Renderizado con PyGame**: Dado que trazar decenas de miles de elipses de forma individual es inviable para la CPU en Python, se utilizó `pygame.surfarray` para inyectar directamente la matriz vectorial de píxeles (`numpy array`) calculada por Rust sobre la pantalla.

---

## ✋ Sistema de Gestos y Respuestas

El modelo aplica filtros de Interpolación Lineal (Lerp) para asegurar que el centro de la gravedad (la mano del usuario) se mueva de forma natural. 

Las físicas son dinámicas dependiendo del gesto detectado:



| Gesto | Efecto en la Física | Variables (Foco / Fricción) |
| --- | --- | --- |
| **Mano Abierta**  | Gravedad natural, órbita y atracción leve. | 1500.0 / 0.98 |
| **Puño Cerrado** | "Agujero Negro" compacto. Arrastra la materia. | 40000.0 / 0.65 |
| **1 Dedo(Índice)** | Aspersor. Dispara 150 partículas nuevas/frame. | 2000.0 / 0.95 |
| **Amor y Paz(✌️)** | Campo de fuerza repelente. Aleja la materia. | -40000.0 / 0.90 |
| **Rock(🤘)** | Hiper-explosión de dispersión inmediata. | -200000.0 / 0.99 |
| **Promesa(Meñique)** | Congelación temporal absoluta. | 0.0 / 0.00 |
---

## ⚙️ Instrucciones de Desarrollo / Compilación

### Requisitos Previos
* **Python** >= 3.8
* **Rust / Cargo** configurado localmente.

### Entorno Virtual y Dependencias
Dado que usamos librerías pesadas y enlaces nativos (PyO3), es recomendado el uso de `.venv`.
```bash
# Crear entorno y activarlo
python -m venv .venv
.\.venv\Scripts\activate

# Instalar requisitos de Python
pip install maturin mediapipe opencv-python pygame numpy
```

### Compilar el Motor de Físicas
El entorno de Python usa un paquete de desarrollo llamado `maturin` que invoca internamente a `Cargo` para construir la librería en C/Rust y empaquetarla transparentemente.
```bash
# Si usas Python 3.13, debes invocar esta bandera de retrocompatibilidad antes de compilar
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Construir librería Rust e instalarla temporalmente
maturin develop --release
```

### Ejecución
```bash
python app.py
```
*(Nota: El modelo de Machine Learning `hand_landmarker.task` de Google se descargará de manera automática en el primer arranque del programa).*
