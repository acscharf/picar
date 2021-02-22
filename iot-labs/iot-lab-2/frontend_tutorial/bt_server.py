import bluetooth
import picar_4wd as fc

hostMACAddress = "DC:A6:32:8C:F7:C9" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 0
backlog = 1
size = 1024
s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind((hostMACAddress, port))
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
            client.send(distance) # Echo back to client
except: 
    print("Closing socket")
    client.close()
    s.close()

