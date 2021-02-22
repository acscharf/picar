import bluetooth
import threading
import picar_4wd as fc
import time

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
        while 1:   
            print("server recv from: ", clientInfo)
            data = client.recv(size)
            if data:
                print(data)
                distance = fc.get_distance_at(int(data))
                client.send(str(distance)) # Echo back to client
    except: 
        print("Closing socket")
        client.close()
        s.close()

def start_client():
    time.sleep(10)
    print("car client starting")
    ubuntuMACAddress = "00:1A:7D:DA:71:15" #
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((ubuntuMACAddress, port))
    while 1:
        text = "yolo"
        sock.send(text)
        time.sleep(1.5)

    sock.close()

sth = threading.Thread(target=start_server)
cth = threading.Thread(target=start_client)

sth.start()
cth.start()

cth.join()
sth.join()

print("Success, terminating")
