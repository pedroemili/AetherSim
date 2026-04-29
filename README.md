# Simulador de Partículas Controladas por Gestos

Este proyecto es un simulador de partículas interactivo que utiliza:
- **Rust** (compilado a WebAssembly) para la simulación de partículas de alto rendimiento
- **Python** con MediaPipe para el reconocimiento de gestos de manos
- **HTML/CSS/JavaScript** para la interfaz web

## Estructura del Proyecto

```
/workspace
├── rust_particles/          # Código Rust para simulación de partículas
│   ├── Cargo.toml           # Configuración del proyecto Rust
│   └── src/
│       └── lib.rs           # Lógica de simulación de partículas
├── python_gestures/         # Código Python para detección de gestos
│   ├── gesture_server.py    # Servidor Flask para detección de gestos
│   └── requirements.txt     # Dependencias de Python
└── web/                     # Interfaz web
    └── index.html           # Página principal del simulador
```

## Requisitos Previos

### Para Rust/WebAssembly:
1. Instalar Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. Instalar wasm-pack: `cargo install wasm-pack`
3. Compilar para WebAssembly:
   ```bash
   cd rust_particles
   wasm-pack build --target web
   ```

### Para Python:
1. Instalar dependencias:
   ```bash
   cd python_gestures
   pip install -r requirements.txt
   ```

## Cómo Ejecutar

### Paso 1: Iniciar el servidor de gestos (Python)
```bash
cd /workspace/python_gestures
python gesture_server.py
```

### Paso 2: Abrir la página web
Abre `/workspace/web/index.html` en tu navegador. Puedes usar un servidor HTTP local:
```bash
cd /workspace/web
python -m http.server 8080
```
Luego navega a `http://localhost:8080`

## Funcionalidades de Gestos

1. **Mano abierta**: Repele las partículas
2. **Puño cerrado**: Atrae las partículas
3. **Mano semi-abierta**: Mueve las partículas
4. **Click en el canvas**: Añade partículas en esa posición

## Controles en la Interfaz

- **Iniciar Cámara**: Activa la detección de gestos
- **Detener Cámara**: Desactiva la detección de gestos
- **Añadir Partículas**: Agrega más partículas al centro
- **Slider de cantidad**: Ajusta el número inicial de partículas

## Tecnologías Utilizadas

- **Rust**: Lenguaje de programación sistémico de alto rendimiento
- **wasm-bindgen**: Para interoperabilidad entre Rust y JavaScript
- **WebAssembly**: Para ejecutar código Rust en el navegador
- **Python**: Para procesamiento de visión por computadora
- **MediaPipe**: Para detección de manos y gestos
- **OpenCV**: Para procesamiento de imágenes
- **Flask**: Servidor web para API de gestos
- **HTML5 Canvas**: Para renderizado de partículas

## Notas Importantes

1. Necesitas una cámara web funcional para la detección de gestos
2. El servidor Python debe estar ejecutándose para que funcione la detección de gestos
3. La compilación de Rust a WebAssembly genera archivos en `rust_particles/pkg/`
4. El proyecto funciona sin el servidor Python, pero solo con interacción por mouse
