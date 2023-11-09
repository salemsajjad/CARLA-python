import socket
import sys
import cv2
import pickle
import numpy as np
import struct ## new
import zlib
import collections
import time
import base64

class fpsmeter:

    def __init__(self):
        self.q = collections.deque(maxlen=100)#type: typing.Deque

    def addtick(self):
        self.q.append(time.time())

    def FPS(self):
        fps = 0
        if len(self.q) > 2:
            t1 = self.q[0]
            t2 = self.q[-1]
            fps = 1.0 * (len(self.q) - 1) / (t2 - t1)
        return fps


HOST='192.168.0.24'
PORT=17200

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
print('Socket created')

s.bind((HOST,PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn,addr=s.accept()

data = b""
payload_size = struct.calcsize(">L")

width = 1280
height = 720
dim = (width, height)

print(f"payload_size: {payload_size}")
fpsm = fpsmeter()
while True:
    while len(data) < payload_size:
        # print("Recv: {}".format(len(data)))
        data += conn.recv(4096)

    # print("Done Recv: {}".format(len(data)))
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    # print("msg_size: {}".format(msg_size))
    while len(data) < msg_size:
        data += conn.recv(2764800)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    # frame = np.frombuffer(base64.b64decode(frame_data), dtype=np.uint8)
    frame = cv2.imdecode(frame,cv2.CV_32F)
    # frame = cv2.cvtColor(frame , cv2.COLOR_RGB2BGR)
    frame = cv2.resize(frame, dim) #interpolation = cv2.INTER_AREA
    fpsm.addtick()
    print("FPS: ",fpsm.FPS())
    cv2.imshow('CARLA_Image',frame)
    cv2.waitKey(1)