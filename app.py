import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import pygame
import numpy as np
import urllib.request
import os
import math
import sys
from aether_core import Simulacion 

def dedo_extendido(puntos_referencia, id_punta, id_pip):
    muneca = puntos_referencia[0]
    punta = puntos_referencia[id_punta]
    pip = puntos_referencia[id_pip] 
    dist_punta = math.hypot(punta.x - muneca.x, punta.y - muneca.y)
    dist_pip = math.hypot(pip.x - muneca.x, pip.y - muneca.y)
    return dist_punta > dist_pip

def main():
    # Inicializar pygame
    pygame.init()
    ANCHO, ALTO = 1280, 720
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("AetherSim: Simulador de Partículas por Gestos")
    reloj = pygame.time.Clock()

    # Descargar el modelo de detección
    ruta_modelo = 'hand_landmarker.task'
    if not os.path.exists(ruta_modelo):
        print("Descargando el modelo hand_landmarker.task...")
        url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
        urllib.request.urlretrieve(url, ruta_modelo)
    
    # Inicializar el reconocedor de gestos
    opciones_base = mp_python.BaseOptions(model_asset_path=ruta_modelo)
    opciones = vision.HandLandmarkerOptions(
        base_options=opciones_base,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6
    )
    manos = vision.HandLandmarker.create_from_options(opciones)

    # Inicializar la cámara
    captura = cv2.VideoCapture(0)
    if not captura.isOpened():
        print("Error: No se pudo abrir la cámara.")
        sys.exit()

    # Crear simulación en Rust
    numero_particulas = 15000
    simulacion = Simulacion(numero_particulas, ANCHO, ALTO)

    ejecutando = True

    
    foco_x_suavizado, foco_y_suavizado = -100.0, -100.0

    while ejecutando:
        dt = reloj.tick(60) / 1000.0 # clamp en milisegundos
        if dt > 0.1: dt = 0.1 # máximo de tiempo delta
        tiempo_ms = int(pygame.time.get_ticks())

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_q or evento.key == pygame.K_ESCAPE:
                    ejecutando = False

        # frame de la camara
        exito, cuadro = captura.read()
        if not exito:
            continue

        # Efecto espejo
        cuadro = cv2.flip(cuadro, 1)
        
        
        img_rgb = cv2.cvtColor(cuadro, cv2.COLOR_BGR2RGB)
        mp_imagen = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        resultado = manos.detect_for_video(mp_imagen, tiempo_ms)

        foco_x, foco_y = foco_x_suavizado, foco_y_suavizado
        
        fuerza_actual = 0.0
        friccion_actual = 0.99
        color_objetivo = (0, 200, 255) # Color de las particulas

        if len(resultado.hand_landmarks) > 0:
            for puntos_mano in resultado.hand_landmarks:

                ext_indice = dedo_extendido(puntos_mano, 8, 6)
                ext_medio = dedo_extendido(puntos_mano, 12, 10)
                ext_anular = dedo_extendido(puntos_mano, 16, 14)
                ext_menique = dedo_extendido(puntos_mano, 20, 18)

                punta_indice = puntos_mano[8]
                centro_palma = puntos_mano[9]

                if ext_indice and ext_medio and not ext_anular and not ext_menique:
                    #Signo de Amor y Paz -> Campo de fuerza repelente (Verde)
                    foco_x = punta_indice.x * ANCHO
                    foco_y = punta_indice.y * ALTO
                    fuerza_actual = -40000.0
                    friccion_actual = 0.90
                    color_objetivo = (50, 255, 50)
                elif ext_indice and not ext_medio and not ext_anular and ext_menique:
                    #Símbolo de Rock -> Explosión súbita (Naranja)
                    foco_x = centro_palma.x * ANCHO
                    foco_y = centro_palma.y * ALTO
                    fuerza_actual = -200000.0
                    friccion_actual = 0.99
                    color_objetivo = (255, 100, 0)
                elif not ext_indice and not ext_medio and not ext_anular and ext_menique:
                    #Solo el meñique -> Congelar el tiempo (Morado)
                    foco_x = centro_palma.x * ANCHO
                    foco_y = centro_palma.y * ALTO
                    fuerza_actual = 0.0
                    friccion_actual = 0.0 # Fricción 0 detiene por completo el movimiento
                    color_objetivo = (200, 0, 255)
                elif ext_indice and not ext_medio and not ext_anular and not ext_menique:
                    #Un solo dedo -> Aparecer/Lanzar partículas (Cyan)
                    foco_x = punta_indice.x * ANCHO
                    foco_y = punta_indice.y * ALTO
                    simulacion.agregar_particulas(150, foco_x, foco_y)
                    fuerza_actual = 2000.0
                    friccion_actual = 0.95
                    color_objetivo = (0, 200, 255)
                elif not ext_indice and not ext_medio and not ext_anular and not ext_menique:
                    #Puño cerrado -> Gravedad intensa que arrastra las partículas (Rojo)
                    foco_x = centro_palma.x * ANCHO
                    foco_y = centro_palma.y * ALTO
                    fuerza_actual = 40000.0
                    friccion_actual = 0.65
                    color_objetivo = (255, 50, 50)
                else:
                    #Mano Abierta o normal -> Efecto de gravedad suave (Blanco)
                    foco_x = centro_palma.x * ANCHO
                    foco_y = centro_palma.y * ALTO
                    fuerza_actual = 1500.0
                    friccion_actual = 0.98
                    color_objetivo = (200, 200, 200)

       
        foco_x_suavizado += (foco_x - foco_x_suavizado) * 0.2
        foco_y_suavizado += (foco_y - foco_y_suavizado) * 0.2

        simulacion.paso(dt, foco_x_suavizado, foco_y_suavizado, fuerza_actual, friccion_actual)

        posiciones_planas = simulacion.obtener_posiciones()
        cantidad_actual = len(posiciones_planas) // 2
        
        if cantidad_actual == 0:
            pantalla.fill((10, 10, 15))
            pygame.display.flip()
            continue

        posiciones = posiciones_planas.reshape((cantidad_actual, 2))

        pantalla.fill((10, 10, 15))
        
        # Limitar pantalla
        coords_x = np.clip(posiciones[:, 0].astype(int), 0, ANCHO - 1)
        coords_y = np.clip(posiciones[:, 1].astype(int), 0, ALTO - 1)

        
        if foco_x >= 0 and foco_y >= 0:
            pygame.draw.circle(pantalla, color_objetivo, (int(foco_x), int(foco_y)), 15, 2)

        arreglo_pixeles = pygame.surfarray.pixels3d(pantalla)
        
        
        color_r = np.full(cantidad_actual, color_objetivo[0], dtype=np.uint8)
        color_g = np.full(cantidad_actual, color_objetivo[1], dtype=np.uint8)
        color_b = np.full(cantidad_actual, color_objetivo[2], dtype=np.uint8)

        # Dibujar los píxeles
        arreglo_pixeles[coords_x, coords_y, 0] = color_r
        arreglo_pixeles[coords_x, coords_y, 1] = color_g
        arreglo_pixeles[coords_x, coords_y, 2] = color_b
        
      
        del arreglo_pixeles

        # Actualizar pantalla
        pygame.display.flip()


    captura.release()
    pygame.quit()

if __name__ == "__main__":
    main()
