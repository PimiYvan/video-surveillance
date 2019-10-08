/*********
  Complete project details at https://randomnerdtutorials.com  
*********/

#include <SoftwareSerial.h>

// Configure software serial port
SoftwareSerial SIM900(7, 8); 
char incoming_char=0;

void setup() {
  // Arduino communicates with SIM900 GSM shield at a baud rate of 19200
  // Make sure that corresponds to the baud rate of your module
  SIM900.begin(19200);
  // Give time to your GSM shield log on to network
  Serial.begin(19200); 

  delay(20000);   
  // Send the SMS
  sendSMS();
  // Set module to send SMS data to serial out upon receipt 
  SIM900.print("AT+CNMI=2,2,0,0,0\r");
  delay(100);

}

void loop() { 
//  Serial.println("Bonjour le monde");
//  SIM900.println("Voici mon telephone 237696827643");
   // Send the SMS
//  sendSMS();
  if(SIM900.available() >0) {
      //Get the character from the cellular serial port
      incoming_char=SIM900.read(); 
      //Print the incoming character to the terminal
      Serial.print(incoming_char); 
      delay(100);
      sendSMS();
   }
}

void sendSMS() {
  // AT command to set SIM900 to SMS mode
  SIM900.print("AT+CMGF=1\r"); 
  delay(100);

  // REPLACE THE X's WITH THE RECIPIENT'S MOBILE NUMBER
  // USE INTERNATIONAL FORMAT CODE FOR MOBILE NUMBERS
//  SIM900.println("AT + CMGS = \"+237655157793\""); 
  SIM900.println("AT + CMGS = \"+237696827643\""); 
  delay(100);
  
  // REPLACE WITH YOUR OWN SMS MESSAGE CONTENT
  SIM900.println("Message example from Arduino Uno."); 
  delay(100);

  // End AT command with a ^Z, ASCII code 26
  SIM900.println((char)26); 
  delay(100);
  SIM900.println();
  // Give module time to send SMS
  delay(5000); 
}

