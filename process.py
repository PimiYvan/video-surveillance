import sys
import pickle
import zlib
import struct
#import StringIO
import json
from tempfile import TemporaryFile
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO, BytesIO ## for Python 3
    

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import threading

from socket import *
#packages nécessaire pour la gestion des emails
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ntpath
import pyautogui
import asyncio
import os
from multiprocessing import Process, Value
import _thread

def detection(isRunning):
    print("dans la detection ")
    CLASSES = ["arriere-plan", "avion", "velo", "oiseau", "bateau",
           "bouteille", "autobus", "voiture", "chat", "chaise", "vache", "table",
           "chien", "cheval", "moto", "personne", "plante en pot", "mouton",
           "sofa", "train", "moniteur" ]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    #chargement du fichier depuis le répertoire
    print("chargement du fichier ")
    net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")

    #initialiser la camera du pi, attendre 2 s pour la mise au point
    #initialiser le compteur FPS
    print("demarage de la raspberry pi")
    vs = VideoStream(usePiCamera=True, resolution=(1600, 1200)).start()
    time.sleep(2.0)
    fps = FPS().start()
    print("apres le demarage")

    
    #isRunning = True
    website = "192.168.0.102"
    website_port = 8089
    address = (website, website_port)
    web_socket = socket(AF_INET, SOCK_STREAM)

    try:
        web_socket.connect(address)
        connected = True
        print("connected to the server")
    except:
        print("dont connected to the server")
        connected = False
        connection_server = False
        
    #web_socket.settimeout(0.1)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    img_counter = 0

    while True:
        while not bool(isRunning.value) is True:
            pass
        #print("dans le running")
        frame = vs.read()
        frame = imutils.resize(frame, width=800)
        if(connected):
            result, frame2 = cv2.imencode('.jpg', frame, encode_param)
            
            data = pickle.dumps(frame2, 0)
            size = len(data)
            
            #print("{}: {}".format(img_counter, size))
            try:
                web_socket.sendall(struct.pack(">L", size)+data)        
            except:
                connected = False
            
        
        img_counter += 1
        # récuperation des dimensions et transformation
        (h,w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        #determiner la détection et la prédiction
        net.setInput(blob)
        detections = net.forward()
        print("detection")
        # boucle de détection
        
        for i in np.arange(0, detections.shape[2]):
            #calcul de la probabilité minimale
            #en fonction de la prédiction
            confidence = detections[0, 0, i, 2]
            # supprimer les détections faibles
            # inférieures a la probabilité minimale
            if confidence > 0.5:
                
                idx = int(detections[0, 0, i, 1 ])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                # creation du contour autour de l'objet détecte
                # insertion de la prédiction de l'objet détecté
                label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                print(label)
                #print(i)
                cv2.rectangle(frame, (startX, startY), (endX, endY), COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                #enregistrement de l'image détecter
                cv2.imwrite("detection"+CLASSES[idx]+".png", frame)
                
                if CLASSES[idx] == "personne" : 
                # envoie de mail avec l'image de la piece jointe
                    email = 'ynjomkam@gmail.com'
                    password = 'D@isy2015'
                    #send_to_email = 'georges.kouamou@gmail.com'
                    send_to_email = 'ypimi.polytechvalor@gmail.com'
                    subject = 'detection'
                    message = 'detection'
                    file_location = 'detection'+CLASSES[idx]+'.png'
                    msg = MIMEMultipart()
                    msg['From'] = email
                    msg['To'] = send_to_email
                    msg['Subject'] = subject
                    body = message
                    msg.attach(MIMEText(body, 'plain'))
                    filename = ntpath.basename(file_location)
                    attachement = open(file_location, 'rb')
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((attachement).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "attachment; filename=%s"%filename)
                    msg.attach(part)
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email, password)
                    text = msg.as_string()
                    
                    server.sendmail(email, send_to_email, text)
                    server.quit()
                    print("on a detecter une personne")
                    
                    #time.sleep(7)
                    #data = "sms"
                    #client_socket.sendto(data.encode(), address_sms)

                    #try:
                       
                    #    rec_data, addr = client_socket.recvfrom(2048)
                    #    print(rec_data)

                    #except:

                     #   print("except red")
                     #   pass
        #cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        #la touche q permet d'interrompre la boucle principale
        if key == ord("q"):
            break
        
        fps.update()
        
    fps.stop()
    print("[INFO] elapsed time {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS {:.2f}".format(fps.fps()))           
    cv2.destroyAllWindows()
    vs.stop()

def control(isRunning):
     # Create a TCP/IP socket
    sock = socket(AF_INET, SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('192.168.0.107', 10002)
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
     
    try: 
        while True:
            # Wait for a connection
            print('waiting for a connection...')
            connection, client_address = sock.accept()
            print('connection from %s:%d' % client_address)
            try:
                while True:
                    # Receive the data one byte at a time
                    data = connection.recv(2048)
                    #sys.stdout.write(data)
                    print(data)
                    if data == b'voleur':
                        # Send back in uppercase
                        #connection.sendall(data.upper())
                        os.system('espeak -a 200 -v mb-fr1 -s 200 "Veuillez Sortir de cette maison avant l\'arriver de la police" --stdout | aplay')
                    elif data == b'end':
                        print("the end of camera")
                        isRunning.value = False
                    elif data == b'start':
                        print("the beginning of camera")
                        isRunning.value = True
                    else:
                        print('no more data, closing connection.')
                        break
            finally:
                # Clean up the connection
                connection.close()
    except KeyboardInterrupt:
        print('exiting.')
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        
if __name__ == '__main__':
    #detection()
    isRunning = Value('i', 1)
        
    p2 = Process(target=control, args=(isRunning, ))
    p1 = Process(target=detection, args=(isRunning, ))
    
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()

