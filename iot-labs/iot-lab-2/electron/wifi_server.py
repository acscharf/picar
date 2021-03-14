import socket
import picar_4wd as fc
import time
from picar_4wd.utils import pi_read
import json
import threading
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server


HOST = "192.168.0.156" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)
power_val = 10

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def start_video_server():
    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        global output
        camera.rotation = 270
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()

def start_car_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        #try:
        while 1:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            if data != b"":
                command = data.decode(encoding='UTF-8')
                if command:
                    if command == 'w':
                        fc.forward(power_val)
                    elif command == 'a':
                        fc.turn_left(power_val)
                        print("Turning left")
                    elif command == 's':
                        fc.backward(power_val)
                        print("Moving back")
                    elif command == 'd':
                        fc.turn_right(power_val)
                        print("Turning right")
                    elif command == 'stop':
                        fc.stop()
                        print("Stopping")
                    elif command == 'data_update':
                        print("sending piread")
                        text = pi_read()
                        json_msg = json.dumps(text)
                        client.send(json_msg.encode('utf-8'))
                    else:
                        print("Unrecognized command")
                        print(data)
                        print(type(data))
        '''
        except: 
            print("Closing socket")
            client.close()
            s.close()
            '''    

sth = threading.Thread(target=start_video_server)
cth = threading.Thread(target=start_car_server)

sth.start()
cth.start()

cth.join()
sth.join()

print("Success, terminating")