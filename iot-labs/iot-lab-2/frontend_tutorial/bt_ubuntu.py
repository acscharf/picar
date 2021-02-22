import bluetooth
import threading
import time

def start_server():
    print("ubuntu server starting")
    myMACAddress = "00:1A:7D:DA:71:15" #This bluetooth adapter
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
    except: 
        print("Closing socket")
        client.close()
        s.close()

def start_client():
    time.sleep(10)
    print("ubuntu client starting")
    carMACAddress = "DC:A6:32:8C:F7:C9" # The address of Raspberry PI Bluetooth adapter on the server.
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((carMACAddress, port))
    while 1:
        text = input("Enter your message: ") # Note change to the old (Python 2) raw_input
        if text == "quit":
            break
        sock.send(text)

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
