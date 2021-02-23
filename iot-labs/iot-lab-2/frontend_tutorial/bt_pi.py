import bluetooth
import threading
import time

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
    try:
        client, clientInfo = s.accept()
        print("Accepted connection from", clientInfo)
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
    print("ubuntu client starting")
    carMACAddress = "DC:A6:32:8C:F7:C9" # The address of Raspberry PI Bluetooth adapter on the server.
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((carMACAddress, port))
    while 1:
        time.sleep(30)
        text = input("Enter your message: ") # Note change to the old (Python 2) raw_input
        if text == "quit":
            break
        sock.send(text)

        data = sock.recv(1024)
        print("from server: ", data)

    sock.close()

start_server()

#sth = threading.Thread(target=start_server)
#cth = threading.Thread(target=start_client)

#sth.start()
#cth.start()

#cth.join()
#sth.join()

print("Success, terminating")
