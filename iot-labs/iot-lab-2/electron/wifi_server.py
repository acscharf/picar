import socket
import picar_4wd as fc
import time
from picar_4wd.utils import pi_read
import json

HOST = "192.168.0.156" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    try:
        while 1:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            if data != b"":
                command = data.decode(encoding='UTF-8')
                if command:
                    if command == 'w':
                        fc.forward(power_val)
                        client.send("Moving forward")
                    elif command == 'a':
                        fc.turn_left(power_val)
                        client.send("Turning left")
                    elif command == 's':
                        fc.backward(power_val)
                        client.send("Moving back")
                    elif command == 'd':
                        fc.turn_right(power_val)
                        client.send("Turning right")
                    elif command == 'stop':
                        fc.stop()
                        client.send("Stopping")
                    else:
                        print("Unrecognized command")
                        print(data)
                        print(type(data))
    except: 
        print("Closing socket")
        client.close()
        s.close()    