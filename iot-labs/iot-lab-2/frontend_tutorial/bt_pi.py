import bluetooth
import threading
import time
import sys
import tty
import termios
import asyncio
import json

diagnostic = {}

## from sunfounder library
def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)

def start_server():
    print("ubuntu server starting")
    myMACAddress = "DC:A6:32:93:2D:CC" #This bluetooth adapter
    port = 0
    backlog = 1
    size = 1024
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind((myMACAddress, port))
    s.listen(backlog)
    print("listening on port ", port)
    #try:
    client, clientInfo = s.accept()
    print("Pi server received connection")
    while 1:   
        print("Going here")
        data = client.recv(size)
        print("Printing data")
        print(data)
        text = data.decode(encoding='UTF-8')
        print("Printing text")
        print(text)
        diagnostic_test = json.loads(text)
        print("Printing diagnostic")
        print(diagnostic_test)

    '''       
    except: 
        print("Closing socket")
        client.close()
        s.close()
    '''

def start_client():
    time.sleep(10)
    print("Pi client starting")
    carMACAddress = "DC:A6:32:8C:F7:C9" # The address of Raspberry PI Bluetooth adapter on the server.
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((carMACAddress, port))
    print("Pi client started. Press keys to move:")
    while 1:
        key=readkey()
        if key == 'p':
            print(diagnostic)
        elif key == 'q':
            print("quitting")
            break
        else:
            if key=='w':
                sock.send(key)
            elif key=='a':
                sock.send(key)
            elif key=='s':
                sock.send(key)
            elif key=='d':
                sock.send(key)
            else:
                sock.send('stop')

            data = sock.recv(1024)
            print("from server: ", data)

    sock.close()

sth = threading.Thread(target=start_server)
cth = threading.Thread(target=start_client)

sth.start()
cth.start()

cth.join()
sth.join()

print("Success, terminating")
