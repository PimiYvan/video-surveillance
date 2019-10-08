#include <Ethernet.h>
#include <EthernetUdp.h>
#include <SPI.h>

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 0, 177);

unsigned int localPort = 5000;
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];
String datReq;
int packetSize;
EthernetUDP Udp;

void setup()
{
  Serial.begin(230400);
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  delay(1500);
}

void loop()
{
 
  packetSize = Udp.parsePacket();

  if (packetSize > 0)
  {

    Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
   
    String datReq(packetBuffer);

    if (datReq == "red")
    {

      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.print("RED");
      Udp.endPacket();

      return;
     
    }

    else if (datReq == "green")
    {

      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.print("GREEN");
      Udp.endPacket();

      return;
     
    }

    else if (datReq == "blue")
    {

      Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
      Udp.print("BLUE");
      Udp.endPacket();

      return;
     
    }
   
  }

  memset(packetBuffer, 0, UDP_TX_PACKET_MAX_SIZE);

}
