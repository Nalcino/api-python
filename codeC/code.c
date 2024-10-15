#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);  // Criar uma instância do leitor RFID

void setup() {
  Serial.begin(9600);    // Inicializar comunicação serial
  SPI.begin();           // Inicializar SPI
  rfid.PCD_Init();       // Inicializar o MFRC522
}

void loop() {
  // Verificar se um novo cartão está presente
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }
  
  // Verificar se o cartão pode ser lido
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Obter o UID do cartão
  String uidString = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    uidString += String(rfid.uid.uidByte[i], HEX);
    if (i < rfid.uid.size - 1) {
      uidString += ":";  // Usando ":" como separador
    }
  }
  
  Serial.print("UID do cartão: ");
  Serial.println(uidString);
  
  // Enviar o UID para a API pela porta serial
  Serial.println(uidString);

  // Parar a leitura de mais cartões
  rfid.PICC_HaltA();
}
