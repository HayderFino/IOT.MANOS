# IOT.MANOS

Proyecto para detección de dedos con MediaPipe y envío de conteo por puerto serial (Arduino / otro dispositivo).

Requisitos rápidos
- Python 3.8+
- Cámara conectada
- Puerto serial disponible (ej: /dev/ttyUSB0 en Linux, COM4 en Windows)

Instalación
1. Crear y activar un entorno virtual:

	python3 -m venv venv
	source venv/bin/activate  # Linux/macOS

2. Instalar dependencias:

	pip install -r requirements.txt

Ejecución
- Ejecutar el script indicando opcionalmente el puerto serial:

	python3 manos.py --port /dev/ttyUSB0 --baud 9600

Si no se especifica, el script usará la variable de entorno SERIAL_PORT o el puerto por defecto (COM4 en Windows, /dev/ttyUSB0 en Linux).

Notas
- Si no puede abrir el puerto serial, el programa seguirá ejecutándose pero no enviará datos por serial.
- Para probar sin hardware serial, omite --port y define SERIAL_PORT si quieres cambiar el valor por defecto.

Licencia
- Repositorio de ejemplo, use según necesidad.
# IOT.MANOS