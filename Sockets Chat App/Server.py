import socket
import threading
import time
import re
import os
## SERVER SCRIPT

HEADER = 2048
DISCONNECT_MESSAGE = "!DISCONNECT"
FORMAT = "utf-8"
all_connected = []
all_address = []
all_username = []
all_message = []
blacklist = []
users = {
    "USERNAME" : all_username, 
    "ADDRESS" : all_address
}
help = {
    " Commands" : "  Functions",
    "/list connection" : " -> Display active connections to server",
    "/list connection details" : " -> Display all IP addresses and their respective username",
    "/kick [username] [True|False]" : " -> Kick or ban a specific user",
    "/pm [username] [message]" : " -> Private message to specific user",
    "/toall [message]" : " -> Public message to all users",
    "/viewchat" : " -> View the conversation between users",
    "/blacklist" : " -> Display all blacklisted mac addresses",
    "/blacklist remove [all|IndexNumber]" : " -> Remove all or specific user from the blacklist",
    "/kill [seconds]" : " -> Shut down the server in x seconds",
    "/help" : " -> Display all commands and their functions",
    "cls" : "-> Clear terminal screen",
    "echo" : "-> Repeat after user input on terminal"
}



def bootup():

    # set up interactive terminal
    interactive = threading.Thread(target = interactBlock)
    interactive.daemon = True
    interactive.start()

    server.listen()
    print(f"[SERVER] Server listening on <{SERVER}:{PORT}> ....")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target = handleClient, args= (conn,addr))
            thread.daemon = True
            thread.start()
        except socket.error as e:
            print("Accept request failed : "+ str(e))

def handleClient(conn, addr):
    # receive mac address from client
    mac_length = conn.recv(HEADER).decode(FORMAT)
    mac = conn.recv(int(mac_length)).decode(FORMAT)

    # check blacklisted or not
    if mac in blacklist:
        guard = f"\n[SERVER] You are banned from this server. For more enquiries, please contact the admin\n"
        conn.send(guard.encode(FORMAT))
        conn.send("!kick".encode(FORMAT))
    
    else:
        username_length = conn.recv(HEADER).decode(FORMAT)
        username = conn.recv(int(username_length)).decode(FORMAT)

        # record client details
        all_connected.append(conn)
        all_address.append(addr)
        all_username.append(username)

        print(f"[SERVER] New Connection {addr[0]}:{str(addr[1])} -> {username}",end ="\n>>> ")
        conn.send("----------- Start Messaging Below -----------\n".encode(FORMAT))
        connected = True
        
        while connected:
            try:
                msg_length = conn.recv(HEADER).decode(FORMAT)

                if int(msg_length) > 0:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    rmsg = f"[{username}] >>> {msg} \n"

                    if msg == "!DISCONNECT":
                        rmsg = f"[SERVER] {username} Disconnected... \n"
                        ## remove user records
                        all_address.remove(addr)
                        all_connected.remove(conn)
                        all_username.remove(username)
                        ## loop breaking
                        connected = False
                    
                    ## save the message to server
                    all_message.append(rmsg)

                    ## compute length of message
                    # broadcast_length = str(len(rmsg.encode(FORMAT))) 
                    for client in all_connected:
                        if client != conn:
                            client.send(rmsg.encode(FORMAT))

                else:
                    # do nothing if empty message is sent from clients
                    continue
        
            except:
                break
    
    # close client connection
    # conn.send("!kill".encode(FORMAT))          
    # conn.close()

    if mac not in blacklist:
        print(f"[SERVER] {addr[0]}:{str(addr[1])} -> {username} Disconnected", end="\n>>> ")       

def interactBlock():
    while True:
        cmd = input(">>> ")
        
        # display total number of connections
        if cmd == "/list connection":
            print(f"[SERVER|ACTIVE CONNECTIONS] {len(all_connected)}")
        
        # display IP and Username of each connection
        elif cmd == "/list connection details":
            print("\n{:<22} {:}".format("Address"," Username"))
            for i in range(len(all_address)):
                print("{:<22}-> {:}".format(all_address[i][0]+":"+str(all_address[i][1]),all_username[i]))
            print("",end = "\n\n")
        
        # kick or ban a user
        elif cmd[:5] == "/kick":
            try:
                pattern = r"^/kick (.+) (True|False|true|false|t|f|T|F)$"
                # check command syntax
                if  not (re.match(pattern,cmd)):
                    print("[Server] Argument is not legally filled")
                
                else:
                    cmd = cmd.split(" ")
                    ban = cmd[-1]
                    cmd.pop()
                    cmd = " ".join(cmd)
                    target = cmd[6:]
                    
                    # check existence of the user
                    if target not in all_username:
                        print(f"[SERVER] No such user called {target}")
                    
                    else:
                        ind = all_username.index(target)
                        target_conn = all_connected[ind]
                        print(f"[SERVER] Will Kick {all_address[ind][0]}:{all_address[ind][1]} -> {all_username[ind]}")
                        reason = input("Reason >>> ")
                        response = f"[SERVER] You are kicked Reason: {reason}\n"
                        broad_response = f"[SERVER] {target} is kicked Reason: {reason}\n"
                        
                        # send ban command and get mac address
                        if ban.lower() == "true" or ban.lower() == "t":
                            target_conn.send("!ban".encode(FORMAT))
                            mac = target_conn.recv(HEADER).decode(FORMAT)
                            blacklist.append(mac)
                            
                        # send kick command
                        target_conn.send(response.encode(FORMAT))
                        time.sleep(1)
                        target_conn.send("!kick".encode(FORMAT))

                        # close the connection
                        target_conn.close()
                        all_address.remove(all_address[ind])
                        all_connected.remove(target_conn)
                        all_username.remove(target)
                        print(f"[SERVER] {target} has been kicked")
                        
                        ## message is not sent immediately
                        # save message to server
                        all_message.append(broad_response)
                        for client in all_connected:
                            client.send(broad_response.encode(FORMAT))
            
            except Exception as e:
                print("[SERVER] An unknown error occured\n"+e)
        
        elif cmd[:3] == "/pm":
            try:
                username = cmd[4:]
                if username in all_username:
                    msg = " ".join(cmd.split(" ")[2:])
                    package = f"[SERVER|ADMIN] >>> {msg} (DO NOT REPLY)\n"
                    saved = f"[SERVER|ADMIN] >>> {username} : {msg} (DO NOT REPLY)\n"
                    
                    # save message to server
                    all_message.append(saved)
                    
                    target_conn = all_connected[all_username.index(username)]
                    target_conn.send(package.encode(FORMAT))

                    print("[SERVER] Message is sent successfully")
                
                else:
                    print(f"[SERVER] No such user called {username}")
            
            except:
                print("[SERVER] No such user is found in the database")
        
        elif cmd[:6] == "/toall":
            try: 
                msg = cmd[7:]
                package = f"[SERVER|ADMIN] >>> {msg}\n"
                
                # save message to server
                all_message.append(package)
                
                for client in all_connected:
                    client.send(package.encode(FORMAT))
                print("[Server] Message is sent successfully")
            
            except Exception as e:
                print("[SERVER] Unknown error occured!\n"+e)

        elif cmd == "/viewchat":
            print("-------------- Message History --------------\n")
            for message in all_message:
                print(message)
            print("\n---------------------------------------------",end="\n\n")

        elif cmd[:5] == "/kill":
            try:
                sec = int(cmd[6:])
                print(f"[SERVER] Server will shutdown in {sec} seconds, are you sure? y/N >>> ", end = "")
                res = input("")
                
                if res.upper() == "Y":
                    broadcast = " [SERVER] Server will shutdown in {sec} seconds \n"
                    all_message.append(broadcast)
                    
                    for client in all_connected:
                        client.send(broadcast.encode(FORMAT))
                    time.sleep(sec)
                    broadcast = "[SERVER] Server shutting down..."
                    print(broadcast)
                    
                    for client in all_connected:
                        client.close()
                    all_message.append(broadcast)
                    print("[SERVER] Clearing stored user information...")
                    all_connected.clear()
                    all_address.clear()
                    all_username.clear()
                    print("[SERVER] Done clearing user information...")
                    res = input("[SERVER] Press any key to exit...")
                    os._exit(0)
                
                elif res.upper() == "N" or res == "":
                    print("[SERVER] Shut down procedure aborted")
                
                else:
                    print("[SERVER] Unknown Command Inputted")
            
            except Exception as e:
                print("[Server] An unknown error occured\n"+str(e))

        elif cmd == "/blacklist":
            print(f"Number of blacklisted device : {str(len(blacklist))}")
            print("List of mac addresses of the devices")
            i = 1
            for mac in blacklist:
                print(f"{str(i)}. {mac}")
                i += 1
            print("",end="\n\n") 

        elif cmd[:17] == "/blacklist remove":
            if len(blacklist) > 0:
                cmd = cmd.split(" ")
                
                # case where no user is specified
                if len(cmd) == 2:
                    print("[SERVER] User to remove from blacklist is unspecified")
                
                # case where all is inputted
                elif cmd[-1] == "all":
                    print("[SERVER] This action will clear all data in blacklist. Are you sure? y/N",end = "\n>>> ")
                    res = input("")
                    while True:
                        if res.upper() == "Y":
                            print("[SERVER] Clearing blacklist...")
                            blacklist.clear()
                            print("[SERVER] Done.")
                            break
                        elif res.upper() == "N" or res == "":
                            print("[SERVER] Action aborted.")
                            break
                        else:
                            pass
                        res = input(">>> ")
                            
                else:
                    try:
                        ind = int(cmd[-1])
                        if ind > len(blacklist) or ind < 1:
                            print("[SERVER] Invalid index inputted")
                        else:
                            blacklist.pop(ind)
                            print("[SERVER] User specified is removed from blacklist.")
                    except ValueError:
                        print("[SERVER] The index entered must be a number")
                    except not ValueError:
                        print("[SERVER] Unknown Command Inputted")
            else:
                print("[SERVER] The blacklist is empty...")

        elif cmd == "/help":
            print()
            for k,v in help.items():
                print("{:<38}{:}".format(k,v))
            print("",end = "\n\n")
        
        elif cmd == "cls":
            os.system("cls")

        elif cmd[:4] == "echo":
            print(cmd[5:])
        
        elif cmd == "":
            continue

        else:
            print("[SERVER] Unknown Command Inputted")

#main
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print("[Client] Enter the IP and the port number of the host server")
    print("Host IP : ")
    SERVER = str(input(""))
    print("Port : ")
    PORT = int(input(""))
    ADDR = (SERVER, PORT)
    server.bind(ADDR)
    print("[SERVER] Server is starting...")
    bootup()
except:
    print("Server setup failed. Press any key to exit")
    input("")