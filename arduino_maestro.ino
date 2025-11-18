//Etiqueta puertos
#define ledPin1 8  // Pin del primer LED, #1
#define ledPin2 9  // Pin del segundo LED, #2
#define ledPin3 10  // Pin del tercer LED, #3
#define ledPin4 11  // Pin del cuarto LED, #4
#define ledPin5 12  // Pin del quinto LED, #5
#define led 13 // Indicador de comunicación serial
///Funcion de configuración /////////////////////
void setup() {
  
  Serial.begin(9600); // Comunicación serial
  /// Salidas
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  pinMode(ledPin4, OUTPUT);
  pinMode(ledPin5, OUTPUT);
  pinMode(led, OUTPUT);

  // Apagar todos los LEDs al inicio
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, LOW);
  digitalWrite(ledPin3, LOW);
  digitalWrite(ledPin4, LOW);
  digitalWrite(ledPin5, LOW);
  digitalWrite(led, LOW);
}
/////////////////////////////////////////////////
void loop() {
  // comunicacion derial activa u espera que el dato sea mayor a 0
  if (Serial.available() > 0) 
  { 
    char data = Serial.read(); // Leer el dato recibido por el puerto serial
    digitalWrite(led, HIGH); // Encender indicador
  // Opciones
  switch (data) {
    // Cada led equivale a un numero en especifico según el caso
      case '0':
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, LOW);
        digitalWrite(ledPin4, LOW);
        digitalWrite(ledPin5, LOW);
        break;
      case '1':
        digitalWrite(ledPin1, HIGH);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, LOW);
        digitalWrite(ledPin4, LOW);
        digitalWrite(ledPin5, LOW);
        break;
      case '2':
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, HIGH);
        digitalWrite(ledPin3, LOW);
        digitalWrite(ledPin4, LOW);
        digitalWrite(ledPin5, LOW);
        break;
      case '3':
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, HIGH);
        digitalWrite(ledPin4, LOW);
        digitalWrite(ledPin5, LOW);
        break;
      case '4':
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, LOW);
        digitalWrite(ledPin4, HIGH);
        digitalWrite(ledPin5, LOW);
        break;
      case '5':
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, LOW);
        digitalWrite(ledPin4, LOW);
        digitalWrite(ledPin5, HIGH);
        break;    
  }
 }
}
