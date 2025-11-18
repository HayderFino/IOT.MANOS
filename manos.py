# === Instalación de librerías necesarias antes de ejecutar ===
# pip install mediapipe==0.10.21
# pip install pyserial==3.5
# pip install opencv-python==4.7.0.72

import cv2
import mediapipe as mp
import serial
import time

# === Configuración de MediaPipe ===
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Estados de los sensores
estado_sensores = {
    'distancia': '--',
    'temperatura': '--',
    'humedad': '--',
    'pir': '--',
    'servo': '--'
}

def inicializar_mediapipe():
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
#cambiar si usas windows a com
def inicializar_serial(puerto='/dev/ttyUSB0', baud_rate=9600):
    try:
        serial_port = serial.Serial(port=puerto, baudrate=baud_rate, timeout=1)
        time.sleep(2)
        if serial_port.is_open:
            print(f'✅ Conexión serial establecida en {puerto}')
        return serial_port
    except Exception as e:
        print(f'❌ Error al abrir la conexión serial: {e}')
        exit()

def inicializar_camara():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: no se pudo acceder a la cámara.")
        exit()
    return cap

def contar_dedos(hand_landmarks):
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

    # Pulgar
    if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x > \
       hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        total_dedos += 1

    return total_dedos

def procesar_respuesta_arduino(respuesta):
    """
    Procesa la respuesta del Arduino con datos de sensores
    Formato esperado: "D:25.4,T:23.5,H:45.2,P:1,S:90"
    """
    if respuesta and ':' in respuesta:
        try:
            datos = respuesta.strip().split(',')
            for dato in datos:
                if 'D:' in dato:  # Distancia
                    estado_sensores['distancia'] = dato.split(':')[1] + " cm"
                elif 'T:' in dato:  # Temperatura
                    estado_sensores['temperatura'] = dato.split(':')[1] + " °C"
                elif 'H:' in dato:  # Humedad
                    estado_sensores['humedad'] = dato.split(':')[1] + " %"
                elif 'P:' in dato:  # PIR
                    estado = "ACTIVO" if dato.split(':')[1] == '1' else "INACTIVO"
                    estado_sensores['pir'] = estado
                elif 'S:' in dato:  # Servo
                    estado_sensores['servo'] = dato.split(':')[1] + " °"
        except:
            pass

def enviar_comando(serial_port, comando, ultimo_comando):
    """
    Envía comando por serial solo si hubo cambio
    """
    if comando != ultimo_comando:
        serial_port.write(comando.encode())
        print(f"📡 Enviado: {comando}")
        
        # Leer respuesta del Arduino
        time.sleep(0.1)
        if serial_port.in_waiting > 0:
            respuesta = serial_port.readline().decode().strip()
            procesar_respuesta_arduino(respuesta)
            print(f"📥 Recibido: {respuesta}")
        
        return comando
    return ultimo_comando

def dibujar_interfaz(frame, hand_landmarks, total_dedos):
    """
    Dibuja la interfaz completa con información de sensores
    """
    # Dibujar landmarks de la mano
    if hand_landmarks:
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Fondo para información
    cv2.rectangle(frame, (5, 5), (400, 180), (0, 0, 0), -1)
    
    # Texto principal
    cv2.putText(frame, f"Dedos: {total_dedos}", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Información de sensores según dedos levantados
    y_offset = 60
    if total_dedos == 1:
        cv2.putText(frame, "SENSOR: ULTRASONICO", (20, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        cv2.putText(frame, f"Distancia: {estado_sensores['distancia']}", (20, y_offset+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    elif total_dedos == 2:
        cv2.putText(frame, "SENSOR: DHT11", (20, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        cv2.putText(frame, f"Temp: {estado_sensores['temperatura']}", (20, y_offset+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"Hum: {estado_sensores['humedad']}", (20, y_offset+45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    elif total_dedos == 3:
        cv2.putText(frame, "SENSOR: PIR", (20, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        cv2.putText(frame, f"Movimiento: {estado_sensores['pir']}", (20, y_offset+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    elif total_dedos == 4:
        cv2.putText(frame, "ACTUADOR: SERVO", (20, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        cv2.putText(frame, f"Angulo: {estado_sensores['servo']}", (20, y_offset+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    elif total_dedos == 5:
        cv2.putText(frame, "ACTUADOR: BUZZER", (20, y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        cv2.putText(frame, "BUZZER ACTIVADO", (20, y_offset+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

def main():
    hands = inicializar_mediapipe()
    serial_port = inicializar_serial()
    cap = inicializar_camara()
    ultimo_comando = None

    print("\n🎯 CONTROLES POR GESTOS:")
    print("1 dedo  - Sensor ultrasónico")
    print("2 dedos - Sensor DHT11 (Temp/Hum)")
    print("3 dedos - Sensor PIR")
    print("4 dedos - Servo motor") 
    print("5 dedos - Buzzer")
    print("0 dedos - Apagar todo")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error al leer el frame de la cámara.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        total_dedos = 0
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                total_dedos = contar_dedos(hand_landmarks)
                dibujar_interfaz(frame, hand_landmarks, total_dedos)

        # Enviar comando según número de dedos
        comando = str(total_dedos)
        ultimo_comando = enviar_comando(serial_port, comando, ultimo_comando)

        cv2.imshow('Control por Gestos - Sensores', frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    serial_port.close()
    print("🔚 Programa finalizado.")

if __name__ == "__main__":
    main()