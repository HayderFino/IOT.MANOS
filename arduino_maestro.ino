#include <Servo.h>
#include <DHT.h>

// ===== DEFINICIÓN DE PINES =====
#define TRIG_PIN 2      // Pin Trigger del sensor ultrasónico
#define ECHO_PIN 3      // Pin Echo del sensor ultrasónico  
#define PIR_PIN 4       // Pin del sensor PIR
#define BUZZER_PIN 5    // Pin del buzzer
#define SERVO_PIN 6     // Pin del servo motor
#define DHT_PIN 7       // Pin del sensor DHT11
#define LED_INDICADOR 13 // LED indicador de comunicación serial

// ===== CONFIGURACIÓN DHT11 =====
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// ===== VARIABLES GLOBALES =====
Servo miServo;
int ultimoComando = -1;
bool servoMovimientoCompleto = true;
int anguloServo = 0;
bool buzzerActivo = false;
unsigned long lastBuzzerTime = 0;
const unsigned long buzzerDuration = 1000; // 1 segundo para el buzzer

void setup() {
  Serial.begin(9600);
  
  // ===== CONFIGURACIÓN DE PINES =====
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_INDICADOR, OUTPUT);
  
  // ===== INICIALIZACIÓN DE SENSORES Y ACTUADORES =====
  dht.begin();           // Inicializar sensor DHT11
  miServo.attach(SERVO_PIN); // Conectar servo
  miServo.write(0);      // Posición inicial del servo
  
  // ===== ESTADO INICIAL =====
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(LED_INDICADOR, LOW);
  digitalWrite(TRIG_PIN, LOW);
  
  Serial.println("🔄 Sistema de sensores por gestos INICIADO");
  Serial.println("📋 Comandos: 0=Apagar, 1=Ultrasónico, 2=DHT11, 3=PIR, 4=Servo, 5=Buzzer");
  delay(1000);
}

void loop() {
  // ===== LECTURA DE COMANDOS SERIAL =====
  if (Serial.available() > 0) {
    char comando = Serial.read();
    digitalWrite(LED_INDICADOR, HIGH);
    
    if (comando >= '0' && comando <= '5') {
      int numDedos = comando - '0';
      
      if (numDedos != ultimoComando) {
        ejecutarComando(numDedos);
        ultimoComando = numDedos;
      }
    }
    delay(50);
    digitalWrite(LED_INDICADOR, LOW);
  }
  
  // ===== CONTROL DE BUZZER TEMPORIZADO =====
  if (buzzerActivo && (millis() - lastBuzzerTime >= buzzerDuration)) {
    digitalWrite(BUZZER_PIN, LOW);
    buzzerActivo = false;
  }
  
  // ===== LECTURA CONTINUA DE SENSORES SEGÚN COMANDO ACTIVO =====
  if (millis() % 1000 == 0) { // Actualizar cada segundo aproximadamente
    if (ultimoComando >= 1 && ultimoComando <= 3) {
      ejecutarComando(ultimoComando); // Re-ejecutar para actualizar datos
    }
  }
  
  delay(100); // Pequeña pausa para estabilidad
}

void ejecutarComando(int numDedos) {
  switch (numDedos) {
    case 0:
      // ===== APAGAR TODO =====
      apagarTodo();
      Serial.println("S:0"); // Confirmación
      break;
      
    case 1:
      // ===== SENSOR ULTRASÓNICO =====
      medirYEnviarDistancia();
      break;
      
    case 2:
      // ===== SENSOR DHT11 (TEMPERATURA Y HUMEDAD) =====
      leerYEnviarDHT11();
      break;
      
    case 3:
      // ===== SENSOR PIR (MOVIMIENTO) =====
      leerYEnviarPIR();
      break;
      
    case 4:
      // ===== SERVO MOTOR =====
      moverServo();
      break;
      
    case 5:
      // ===== BUZZER =====
      activarBuzzer();
      break;
  }
}

void apagarTodo() {
  digitalWrite(BUZZER_PIN, LOW);
  buzzerActivo = false;
  miServo.write(0);
  anguloServo = 0;
}

void medirYEnviarDistancia() {
  float distancia = medirDistancia();
  
  // Validar lectura
  if (distancia > 0 && distancia < 400) {
    Serial.print("D:");
    Serial.print(distancia);
    Serial.println();
  } else {
    Serial.println("D:ERROR");
  }
}

float medirDistancia() {
  // Limpiar el trigger
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Enviar pulso de 10 microsegundos
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Medir tiempo de respuesta
  long duracion = pulseIn(ECHO_PIN, HIGH, 30000); // Timeout de 30ms
  
  // Calcular distancia (cm)
  if (duracion > 0) {
    float distancia = duracion * 0.034 / 2;
    return distancia;
  }
  
  return -1; // Error en la medición
}

void leerYEnviarDHT11() {
  // Leer temperatura y humedad
  float temperatura = dht.readTemperature();
  float humedad = dht.readHumidity();
  
  // Verificar si la lectura es válida
  if (isnan(temperatura) || isnan(humedad)) {
    Serial.println("T:ERROR,H:ERROR");
    return;
  }
  
  // Enviar datos
  Serial.print("T:");
  Serial.print(temperatura, 1); // 1 decimal
  Serial.print(",H:");
  Serial.print(humedad, 1); // 1 decimal
  Serial.println();
}

void leerYEnviarPIR() {
  int movimiento = digitalRead(PIR_PIN);
  
  Serial.print("P:");
  Serial.print(movimiento);
  Serial.println();
}

void moverServo() {
  // Realizar barrido completo de 0 a 180 grados
  for (int pos = 0; pos <= 180; pos += 5) {
    miServo.write(pos);
    anguloServo = pos;
    Serial.print("S:");
    Serial.print(pos);
    Serial.println();
    delay(30);
  }
  
  // Regresar a 0 grados
  for (int pos = 180; pos >= 0; pos -= 5) {
    miServo.write(pos);
    anguloServo = pos;
    Serial.print("S:");
    Serial.print(pos);
    Serial.println();
    delay(30);
  }
}

void activarBuzzer() {
  digitalWrite(BUZZER_PIN, HIGH);
  buzzerActivo = true;
  lastBuzzerTime = millis();
  
  Serial.println("B:1"); // Buzzer activado
}

// ===== FUNCIÓN DE DEBUG (OPCIONAL) =====
void debugSensores() {
  Serial.println("=== DEBUG SENSORES ===");
  
  // Ultrasónico
  float dist = medirDistancia();
  Serial.print("Ultrasónico: ");
  Serial.print(dist);
  Serial.println(" cm");
  
  // DHT11
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  Serial.print("DHT11 - Temp: ");
  Serial.print(temp);
  Serial.print("°C, Hum: ");
  Serial.print(hum);
  Serial.println("%");
  
  // PIR
  int pir = digitalRead(PIR_PIN);
  Serial.print("PIR: ");
  Serial.println(pir ? "DETECTADO" : "SIN MOVIMIENTO");
  
  // Servo
  Serial.print("Servo: ");
  Serial.print(anguloServo);
  Serial.println("°");
  
  Serial.println("=====================");
}