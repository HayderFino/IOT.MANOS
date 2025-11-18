# IOT.MANOS

Proyecto: control por gestos (MediaPipe) y comunicación serial con Arduino.

Descripción
Proyecto que detecta el número de dedos levantados usando MediaPipe y OpenCV (script `manos.py`) y envía el conteo por puerto serial a un Arduino con el sketch `arduino_maestro.ino`. El Arduino ejecuta acciones según el número de dedos y puede devolver lecturas de sensores (ultrasónico, DHT11, PIR, servo) en un formato serial sencillo.

Requisitos rápidos
- Python 3.8+ (se probó con 3.11)
- Cámara USB o integrada
- Arduino u otro dispositivo con puerto serial
- Paquetes Python: ver `requirements.txt`

Instalación (entorno Python)
1) Crear y activar un entorno virtual (opcional estandar):

		python3 -m venv venv
		source venv/bin/activate

2) Instalar dependencias desde `requirements.txt`:

		pip install -r requirements.txt

Nota: el repositorio incluye un entorno virtual `pi/` creado por el autor; si prefieres puedes usarlo activando `pi/bin/activate`.

Permisos para el puerto serie (Linux)
- Dar permisos temporales (hasta reiniciar):

		sudo chmod 666 /dev/ttyUSB0

- O permanentemente, agregar usuario al grupo `dialout`:

		sudo usermod -a -G dialout $USER

	Después cierra sesión o reinicia para que los cambios surtan efecto.

Uso
- Ejecutar el script principal `manos.py`:

		python3 manos.py --port /dev/ttyUSB0 --baud 9600

- Opciones importantes:
	- `--port`: puerto serial (ej: `/dev/ttyUSB0` o `COM4`)
	- `--baud`: velocidad de baudios (por defecto 9600)

- Comportamiento: el script captura video, detecta la mano y cuenta dedos. Envía por serial el dígito con el número de dedos (0..5). El Arduino responde con líneas que contienen lecturas o confirmaciones y el script muestra esa información en la interfaz.

Protocolo serial (resumen)
- Mensajes enviados desde Python -> Arduino: un solo carácter `'0'`..`'5'` según dedos detectados.
- Respuestas Arduino -> Python: líneas de texto con campos separados por comas. Ejemplos:
	- Distancia: `D:25.4` (cm)
	- Temperatura/Humedad: `T:23.5,H:45.2`
	- PIR: `P:1` (1 activo, 0 inactivo)
	- Servo: `S:90` (ángulo)

El script `manos.py` interpreta estas respuestas y muestra los valores sobre la imagen.

Descripción del sketch `arduino_maestro.ino`
- Lee comandos seriales (`'0'`..`'5'`) y ejecuta acciones:
	- `0`: apagar actuadores
	- `1`: medir ultrasonido y enviar `D:...`
	- `2`: leer DHT11 y enviar `T:...,H:...`
	- `3`: leer PIR y enviar `P:...`
	- `4`: barrido de servo y enviar `S:...` con ángulos
	- `5`: activar buzzer y enviar `B:1`

- Además, el sketch puede enviar mensajes de estado y tiene un LED indicador para actividad serial.

Ejemplo rápido de pruebas sin hardware Arduino
- Si no tienes Arduino, puedes probar la detección de dedos y la interfaz gráfica comentando o simulando la parte serial en `manos.py` (si el puerto no se abre, el programa imprime un error y terminará). Otra opción: usar un emulador de puerto serial (socat, com0com, etc.) para simular un dispositivo.

Archivo clave: `manos.py` (resumen)
- Usa OpenCV para capturar video y MediaPipe (`mp.solutions.hands`) para detectar landmarks.
- Cuenta dedos comparando posiciones de landmarks (TIP vs PIP para cada dedo; pulgar comparando eje X).
- Envia el valor `str(total_dedos)` por serial solo si cambia respecto al último comando.
- Dibuja una interfaz con información de sensores que actualiza según las respuestas seriales.

Añadido: `requirements.txt`
- Se proporciona un archivo `requirements.txt` con las dependencias mínimas del proyecto (ver en el repositorio).

Problemas comunes y soluciones
- Error camara: revisa que otra aplicación no la esté usando; prueba con `cv2.VideoCapture(0)` u otro índice.
- Error al abrir puerto serial: revisa permisos o cambia el puerto. Prueba con `ls /dev/tty*` antes y después de conectar el Arduino.
- MediaPipe requiere versiones compatibles de Python y paquetes; si ves errores de compilación, usa la versión de Python 3.11 o el entorno `pi/` incluido.

Contribuciones y licencia
- Proyecto de ejemplo; si vas a usarlo en producción considera añadir manejo de errores, reconexión serial y tests automatizados.

---

Hecho por el autor como ejemplo de integración entre visión por computadora y control por gestos con actuadores vía Arduino.


