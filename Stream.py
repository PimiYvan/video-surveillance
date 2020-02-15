
import threading
import socket
import struct
from io import StringIO, BytesIO
import json
import numpy as np
import cv2
import pickle
import zlib

class Streamer (threading.Thread):
    def __init__(self, hostname, port):
        threading.Thread.__init__(self)

        self.hostname = hostname
        self.port = port
        self.connected = False
        self.jpeg = None

    def run(self):
        self.isRunning = True

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created')

        s.bind((self.hostname, self.port))
        print('Socket bind complete')

        data = b""
        payload_size = struct.calcsize("L")

        s.listen(10)
        print('Socket now listening')

        while self.isRunning:
            conn, addr = s.accept()
            # print("oui nous avons accepter")
            payload_size = struct.calcsize(">L")

            while True:
                data = conn.recv(46080)
                # print(data)

                while len(data) < payload_size:
                    # print("Recv: {}".format(len(data)))
                    data += conn.recv(4096)

                if data:
                    # packed_msg_size = data[:payload_size]
                    # data = data[payload_size:]
                    # msg_size = struct.unpack("L", packed_msg_size)[0]
                    # print(data)
                    # frame = pickle.loads(data)

                    # while len(data) < 46080:
                    #     data += conn.recv(10000)

                    # print(frame)
                    # memfile = StringIO.StringIO()
                    # memfile.write(json.loads(frame_data).encode('latin-1'))
                    # memfile.seek(0)
                    # frame = numpy.load(memfile)

                    # frame = BytesIO(data)
                    # frame = np.load(frame)
                    # print(frame)

                    # frame = np.fromstring(data, dtype=np.uint8)

                    print("Done Recv: {}".format(len(data)))
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack(">L", packed_msg_size)[0]
                    # print("msg_size: {}".format(msg_size))
                    while len(data) < msg_size:
                        data += conn.recv(4096)
                    frame_data = data[:msg_size]
                    # data = data[msg_size:]

                    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    # cv2.imshow('ImageWindow', frame)
                    # print(frame)
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    cv2.imwrite("test.jpg", frame)
                    self.jpeg = jpeg

                    self.connected = True

                else:
                    conn.close()
                    self.connected = False
                    break

        self.connected = False

    def stop(self):
        self.isRunning = False

    def client_connected(self):
        return self.connected

    def get_jpeg(self):
        return self.jpeg.tobytes()
