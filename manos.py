# Crear entorno virtual
# python -m venv venv
# Activar entorno virtual
# Windows: python -m venv venv; .\venv\Scripts\activate
# Requerimientos: pip install -r requirements.txt

# === Instalación de librerías necesarias antes de ejecutar ===
# pip install mediapipe==0.10.21     # Para detección y tracking de manos
# pip install pyserial==3.5         # Para comunicación serial con Arduino
# pip install opencv-python==4.7.0.72  # Para capturar y procesar video

import cv2              # OpenCV: procesamiento de imágenes y video
import mediapipe as mp  # MediaPipe: detección y seguimiento de manos
import serial           # PySerial: comunicación con dispositivos vía puerto serial
import time             # Librería estándar para pausas temporales

# === Configuración de MediaPipe ===
mp_drawing = mp.solutions.drawing_utils   # Utilidad para dibujar landmarks
mp_hands = mp.solutions.hands             # Solución de detección de manos


def inicializar_mediapipe():
    """
    Inicializa el modelo de MediaPipe Hands para detección y tracking de manos.

    Returns:
        objeto Hands configurado para detectar una sola mano
    """
    return mp_hands.Hands(
        static_image_mode=False,   # Detección en modo video (no solo imágenes estáticas)
        max_num_hands=1,           # Solo detectar 1 mano
        min_detection_confidence=0.5,  # Umbral de confianza para detectar la mano
        min_tracking_confidence=0.5    # Umbral de confianza para el seguimiento
    )


def inicializar_serial(puerto='COM4', baud_rate=9600):
    """
    Abre la conexión serial con el puerto especificado.

    Args:
        puerto (str): Nombre del puerto COM (ej: 'COM4' en Windows).
        baud_rate (int): Velocidad de transmisión en baudios.

    Returns:
        objeto Serial si la conexión fue exitosa.
    """
    try:
        # Abre el puerto serial
        serial_port = serial.Serial(port=puerto, baudrate=baud_rate, timeout=1)
        time.sleep(1)  # Espera breve para estabilizar la conexión

        if serial_port.is_open:
            print(f'✅ Conexión serial establecida en {puerto} a {baud_rate} bps.')
        return serial_port
    except Exception as e:
        # Si no se pudo abrir el puerto, muestra error y termina programa
        print(f'❌ Error al abrir la conexión serial: {e}')
        exit()


def inicializar_camara():
    """
    Inicializa la cámara para captura de video.

    Returns:
        objeto VideoCapture si la cámara fue abierta correctamente.
    """
    cap = cv2.VideoCapture(0)  # Índice 0 = cámara por defecto
    if not cap.isOpened():
        print("❌ Error: no se pudo acceder a la cámara.")
        exit()
    return cap


def contar_dedos(hand_landmarks):
    """
    Determina cuántos dedos están levantados en la mano detectada.

    Args:
        hand_landmarks: Coordenadas normalizadas de los puntos clave de la mano.

    Returns:
        int: número total de dedos levantados (0 a 5).
    """
    total_dedos = 0

    # Dedo índice
    if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < \
       hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y:
        total_dedos += 1

    # Dedo medio
    if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < \
       hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y:
        total_dedos += 1

    # Dedo anular
    if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < \
       hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y:
        total_dedos += 1

    # Dedo meñique
    if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < \
       hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y:
        total_dedos += 1

    # Pulgar (configurado para mano derecha; invertir condición si es izquierda)
    if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x > \
       hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        total_dedos += 1

    return total_dedos


def enviar_serial(serial_port, datos, ultimo_valor):
    """
    Envía datos por el puerto serial solo si hubo un cambio.

    Args:
        serial_port: objeto Serial abierto.
        datos (str): número de dedos levantados en formato string.
        ultimo_valor (str): último valor enviado, para evitar duplicados.

    Returns:
        str: valor actualizado del último dato enviado.
    """
    if datos != ultimo_valor:  # Enviar solo si hay un cambio
        serial_port.write(datos.encode())  # Codificar a bytes y enviar
        print(f"📡 Enviado: {datos}")
        return datos
    return ultimo_valor


def dibujar_interfaz(frame, hand_landmarks, total_dedos):
    """
    Dibuja la mano detectada y muestra el conteo de dedos en pantalla.

    Args:
        frame: imagen del video en la que se dibujará.
        hand_landmarks: coordenadas de la mano detectada.
        total_dedos (int): número de dedos levantados.
    """
    # Dibujar los puntos y conexiones de la mano
    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Dibujar un rectángulo de fondo para el texto
    cv2.rectangle(frame, (5, 5), (260, 60), (0, 0, 0), -1)

    # Mostrar el número de dedos levantados
    cv2.putText(frame, f"Dedos: {total_dedos}", (20, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


def main():
    """
    Función principal que controla el flujo del programa:
    - Inicializa cámara, puerto serial y modelo de MediaPipe.
    - Procesa cada frame de la cámara.
    - Detecta cuántos dedos están levantados.
    - Dibuja en la pantalla y envía el resultado por serial.
    """
    # Inicializaciones
    hands = inicializar_mediapipe()
    serial_port = inicializar_serial()
    cap = inicializar_camara()
    ultimo_valor = None  # Guarda el último número enviado

    while True:
        # Captura un frame de la cámara
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al leer el frame de la cámara.")
            break

        # Convertir BGR (OpenCV) a RGB (MediaPipe)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar la imagen con MediaPipe
        results = hands.process(frame_rgb)

        total_dedos = 0
        # Si detecta manos, procesarlas
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Contar dedos
                total_dedos = contar_dedos(hand_landmarks)
                # Dibujar interfaz en pantalla
                dibujar_interfaz(frame, hand_landmarks, total_dedos)

        # Enviar número de dedos por serial (si cambió)
        ultimo_valor = enviar_serial(serial_port, str(total_dedos), ultimo_valor)

        # Mostrar la imagen en una ventana
        cv2.imshow('Hand Detection', frame)

        # Si el usuario presiona 'q', salir del bucle
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    # === Liberar recursos ===
    cap.release()              # Cierra cámara
    cv2.destroyAllWindows()    # Cierra ventanas de OpenCV
    serial_port.close()        # Cierra conexión serial
    print("🔚 Programa finalizado y puerto serial cerrado.")


# === Punto de entrada del programa ===
if __name__ == "__main__":
    main()
