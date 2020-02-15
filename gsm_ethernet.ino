#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>
#include <SoftwareSerial.h>

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 0, 177);
IPAddress speakerIP(192,168,0,107);

unsigned int localPort = 5000;
unsigned int speakerPort = 7000;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
String datReq;
int packetSize;
EthernetUDP Udp;
EthernetClient client;

const int NTP_PACKET_SIZE = 48;
char timeServer[] = "time.nist.gov";

// Configure software serial port
SoftwareSerial SIM900(7, 8); 
//char incoming_char=0;
String inData;
String header;
char inchar;
int success;
unsigned long next;

void setup()
{
  
  Serial.begin(19200);
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  delay(1500);

  // Arduino communicates with SIM900 GSM shield at a baud rate of 19200
  // Make sure that corresponds to the baud rate of your module
  SIM900.begin(19200);
  // Give time to your GSM shield log on to network
//  Serial.begin(19200); 
  // Set module to send SMS data to serial out upon receipt 
//  SIM900.print("AT+CNMI=2,2,0,0,0\r");

  SIM900power();
  delay(10000); 
  Serial.println("apres l'init");
  // AT command to set SIM900 to SMS mode
  SIM900.print("AT+CMGF=1\r"); 
  delay(100); 
  SIM900.print("AT+CNMI=2,2,0,0,0\r");
  delay(100);

//  sendSMS();
  next = millis()+5000;

}

void loop()
{
//   Serial.println("Bonjour le monde");
  packetSize = Udp.parsePacket();
//  Serial.println("dans l'envoie de sms");
  if (packetSize > 0)
  {

    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
   
    String datReq(packetBuffer);

    if (datReq == "sms")
    {
      Serial.println("dans l'envoie de sms");
      Serial.println(Udp.remotePort());
      Serial.println(Udp.remoteIP());
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      success = Udp.print("SMS SEND");
      Udp.endPacket();

//      sendSMS();
      Serial.println("apres l'envoie de sms");
      return;
     
    }else if(datReq == "test"){
      Serial.println("dans l'envoie de sms");
      
      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      success = Udp.print("SMS SEND");
      Udp.endPacket();
    }
  }
    
  if(SIM900.available() >0) {
     String sms = "";
     sms = read_sms();
     sms.trim();
     Serial.println(sms);
     if(sms == "voleur"){
      
      Serial.println("envoie de socket");
//      Serial.println(Udp.remotePort());
//      Serial.println(Udp.remoteIP());
//      Udp.beginPacket(speakerIP, Udp.remotePort());
//      Udp.beginPacket(speakerIP, 56420);
//      success = Udp.print(sms);
//      Udp.endPacket();

          // if you get a connection, report back via serial:
        if (client.connect(speakerIP, 10002)) {
          Serial.println("connected to the speaker");
          
        } else {
          // if you didn't get a connection to the server:
          Serial.println("connection failed");
        }

      if (client.connected()) {
        success = client.print("voleur");
      }
      

      Serial.println(success ? "success" : "failed");
      
//      if(!client.connect(serverSonIP, sonPort)){
//        Serial.println("arduno don't able to be connect to son server");
//      }

//      client.print(sms);
//      do
//        {
//          success = Udp.beginPacket(serverSonIP,Udp.remotePort());
//          Serial.print("beginPacket: ");
//          Serial.println(success ? "success" : "failed");
//          //beginPacket fails if remote ethaddr is unknown. In this case an
//          //arp-request is send out first and beginPacket succeeds as soon
//          //the arp-response is received.
//        }
//      while (!success && ((signed long)(millis()-next))<0);
//      
//      if (success ){
//        Serial.println("connecte");
//        success = Udp.write("voleur");
//        success = Udp.print("voleur");
//
//        Serial.print("bytes written: ");
//        Serial.println(success);
//  
//        success = Udp.endPacket();        
//        Serial.print("endPacket: ");
//        Serial.println(success ? "success" : "failed");
//      }
       
     }else{
      
         // if you get a connection, report back via serial:
        if (client.connect(speakerIP, 10002)) {
          Serial.println("connected");
          
        } else {
          // if you didn't get a connection to the server:
          Serial.println("connection failed");
        }

        if (client.connected()) {
          success = client.print(sms);
        }
        
     }
  }

  memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE);
}

void SIM900power()
{
  digitalWrite(9, HIGH);
  delay(1000);
  digitalWrite(9, LOW);
  delay(7000);
}

void sendSMS() {
  // AT command to set SIM900 to SMS mode
  Serial.println("dans l'envoie de sms");
  SIM900.print("AT+CMGF=1\r"); 
  delay(100);

  // REPLACE THE X's WITH THE RECIPIENT'S MOBILE NUMBER
  // USE INTERNATIONAL FORMAT CODE FOR MOBILE NUMBERS
  SIM900.println("AT + CMGS = \"+237655157793\""); 
//  SIM900.println("AT + CMGS = \"+237699314978\""); //Pr Kouamou
//  SIM900.println("AT + CMGS = \"+237698319533\""); // cabrel
//  SIM900.println("AT+CMGS=\"+237696827643\""); // moi
//  SIM900.println("AT + CMGS = \"+237693117284\""); // pichou
  delay(100);
  
  // REPLACE WITH YOUR OWN SMS MESSAGE CONTENT
  SIM900.println("Nous avons detecter une personne chez vous"); 
  delay(100);

  // End AT command with a ^Z, ASCII code 26
  SIM900.println((char)26); 
  delay(100);
  SIM900.println();
  // Give module time to send SMS
  delay(5000); 
}

String read_sms()
{
 int x=0;   // sms character counter
 
 String sms = "";   //initialize
 
 unsigned long int prv_millis = millis();  //wait initialization

   
 while(1)
 {
 
 if(SIM900.available() >0)
 // if(Serial.available() >0)
 {
     char incoming_sms=SIM900.read();
    //char incoming_sms=Serial.read();
   
    sms += incoming_sms;  //add up all the characters as string

     prv_millis = millis();

     x++;  // increment sms character counter
 }

 unsigned long int new_millis = millis();
 
 if((x>0)&&((new_millis - prv_millis)>200))  //if a single letter has been received and no character been
                                                                 //received since last 200 msec, break
 break;
 }

     //Serial.print("received sms =");
     //Serial.println(sms);
     
     int m = 1 + sms.lastIndexOf('"');              

// find location of last ' " ' of sms format
// [  +CMGL: 1,"REC UNREAD","+XXXXXXXXXXXX",,"01/01/19,09:55:16+08"
//   Test message 1 ]


     int n = sms.length();                          // find the length of sms

    // Serial.print("actual sms =");
     //Serial.println(sms.substring(m,n));                // sms text lies between the two

     return(sms.substring(m,n));       //return the sms
}

