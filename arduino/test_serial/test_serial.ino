/*
 * Teste mínimo de comunicação serial para ESP32
 * NÃO usa motores - só testa serial
 * 
 * Suba este sketch e abra o Monitor Serial (115200 baud)
 * Deve aparecer "READY" e ecoar tudo que você digitar
 */

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("READY");
  Serial.println("TESTE_SERIAL_ESP32");
}

void loop() {
  // Ecoar qualquer dado recebido
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      Serial.print("ECHO:");
      Serial.println(line);
    }
  }
  
  // Enviar heartbeat a cada 2 segundos
  static unsigned long last_heartbeat = 0;
  if (millis() - last_heartbeat > 2000) {
    last_heartbeat = millis();
    Serial.println("HEARTBEAT");
  }
}
