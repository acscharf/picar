import bluetooth
import threading
import picar_4wd as fc
import time

power_val = 10

def start_server():
    print("car server starting")
    myMACAddress = "DC:A6:32:8C:F7:C9" #This bluetooth adapter
    port = 0
    backlog = 1
    size = 1024
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind((myMACAddress, port))
    s.listen(backlog)
    print("listening on port ", port)
    try:
        client, clientInfo = s.accept()
        print("Car server was connected")
        while 1:   
            print("Car server received data")
            data = client.recv(size)
            if data:
                if data == 'w':
                    fc.forward(power_val)
                    client.send("Moving forward")
                elif data == 'a':
                    fc.turn_left(power_val)
                    client.send("Turning left")
                elif data == 's':
                    fc.backward(power_val)
                    client.send("Moving back")
                elif data == 'd':
                    fc.turn_right(power_val)
                    client.send("Turning right")
                elif data == 'stop':
                    fc.stop()
                    client.send("Turning right")
                else:
                    print("Unrecognized command")
                    print(data)
                    
    except: 
        print("Closing socket")
        client.close()
        s.close()

def start_client():
    time.sleep(10)
    print("car client starting")
    ubuntuMACAddress = "DC:A6:32:93:2D:CC" #
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((ubuntuMACAddress, port))
    while 1:
        print("sending yolo")
        text = "yolo"
        sock.send(text)
        time.sleep(10)

    sock.close()

sth = threading.Thread(target=start_server)
cth = threading.Thread(target=start_client)

sth.start()
cth.start()

cth.join()
sth.join()

print("Success, terminating")
