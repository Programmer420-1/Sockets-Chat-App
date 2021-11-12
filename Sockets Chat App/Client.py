import socket
import threading
import subprocess
import time
import re

HEADER = 2048
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
kick = False



def send(msg):
    global kick
    if kick == False:
        try:
            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)
        except:
            pass

def send_mac(FORMAT):
    address = []
    prompt = subprocess.Popen("ipconfig /all",shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    output = prompt.stdout.read() + prompt.stderr.read()
    output = str(output,FORMAT)
    pattern = r"^Physical Address. . . . . . . . . :(.+)-(.+)-(.+)-(.+)-(.+)-(.+)$"
    for lines in re.split("   |\n|\r",output):
        if re.match(pattern,lines):
            lines = lines.split(": ")[-1]
            address.append(lines)
    unique = "-".join(address)
    return unique
    
def receive():
    while True:
        try:
            response = client.recv(2048).decode(FORMAT)
            if response == "!kill":
                break
            
            if response == "!kick":
                global kick 
                kick = True
                break
            
            if response == "!ban":
                package = send_mac(FORMAT)
                send(package)
                continue
        
        except:
            pass
        print(response,end = "")

def ClientBootup():
    global kick
    # start receiving data
    thread = threading.Thread(target = receive)
    thread.daemon = True
    thread.start()

    # send mac to check
    send(send_mac(FORMAT))
    if kick == True:
        print("\nThe window will be closed in 5 seconds...")
        time.sleep(5)
        return

    # send username
    message = input("Enter Username >>> ")
    send(message)
    try:
        while True:

            #check kick stat
            if kick == True:
                print("\nThe window will be closed in 5 seconds...")
                time.sleep(5)
                
                break
            
            message = input("")
            send(message)
            if message == DISCONNECT_MESSAGE:
                print("Exiting...")
                break
    except:
        print("You may be kicked or some error occured")
        print("The window will be closed in 5 seconds...")
        time.sleep(5)

        
    
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[Client] Enter the IP and the port number of the host server")
print("Host IP : ")
SERVER = str(input(""))
print("Port : ")
PORT = int(input(""))
ADDR = (SERVER, PORT)
print("[Client] Connection establishing...")
try:
    client.connect(ADDR)
    print(f"[Client] Connection to the host is established")
    ClientBootup()
except:
    print("Connection Failed. Press any key to exit")
    input("")

    
