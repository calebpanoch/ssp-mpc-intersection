name1 = "Caleb"
name2 = "Caleb"

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import time
import socket
#import struct
import threading
from Crypto.Util import number
from ssp import *
import random

maxChar = int("27"*10)

host = 'localhost'
port = 50001

MAX_STRING_LENGTH = 20
maxChar = int("27"*MAX_STRING_LENGTH)*2

bytes = int(maxChar.bit_length() / 8) + 1

print(f"Bytes = {bytes}")

root = Tk()

root.grid_columnconfigure(0, weight=1)

frm = ttk.Frame(root, padding=10)
frm.grid()

root.geometry("300x300")

playerNum = '1'
result = None

# Check if another instance is running
lock_file = "app.lock"
if os.path.exists(lock_file):
    print("Another instance is already running!")
    playerNum = '2'
else:

    with open(lock_file, 'w') as f:
        f.write('App is running')

    def on_close():
        if os.path.exists(lock_file):
            os.remove(lock_file)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)


root.title("SSP Player "+playerNum)

names_matched = []
def mpc_addition(name_input,client_socket):
    print(name_input, len(name_input))
    ename = 0
    try:
        ename = encode_name(name_input)
        
        if ename > maxChar:
            raise Exception("Name is too long")
    except Exception as e:
        print(f"Error {e}")
        status.config(text="Invalid name, please enter a new one.")
        return
    print(name_input,ename)
    
    status.config(text="Great, sending share to player "+str((int(playerNum)%2)+1))
    

#    ownShare = 0
#    otherShare = 0
    largePrime = 0
#    receivedShare = 0
#    ownMPCshare = 0
    
    if playerNum == '1':
    
        
        coeff = random.randint(200,maxChar)
        print(f"Coeff: {coeff}")
        
        f1_share_1 = ename + coeff * 1
        f1_share_2 = ename + coeff * 2
        
        #RECIEVE SHARE FROM PLAYER 2
        
        largePrime = int.from_bytes(client_socket.recv(bytes), byteorder='big')
        f2_share_1 = int.from_bytes(client_socket.recv(bytes), byteorder='big')
        print(f"1. Received largePrime, f2_share_1: {largePrime}, {f2_share_1}")
        
        f1_share_1 = f1_share_1%largePrime
        f1_share_2 = f1_share_2%largePrime
        
        print(f"f1_share_1, f1_share_2: {f1_share_1}, {f1_share_2}")

        
        ownMPCshare = (f1_share_1 + f2_share_1)%largePrime
        
        # SEND PRIME & SHARE TO PLAYER 2
        print(f"2 Sending f1_share_2 and p2 MPC share: {f1_share_2}, {ownMPCshare} to player 2")

        client_socket.sendall(f1_share_2.to_bytes(bytes, byteorder='big'))
        client_socket.sendall(ownMPCshare.to_bytes(bytes, byteorder='big'))

        
        data = client_socket.recv(bytes)
        otherMPCshare = int.from_bytes(data, byteorder='big')
        print("3 Received P2 MPC share: ", otherMPCshare)
        
        # Compute modular inverse
        inv_1_minus_2 = pow(1 - 2, -1, largePrime)  # (1 - 2) ^ -1 mod p
        inv_2_minus_1 = pow(2 - 1, -1, largePrime)  # (2 - 1) ^ -1 mod p

        l1 = ((0 - 2) * inv_1_minus_2) % largePrime
        l2 = ((0 - 1) * inv_2_minus_1) % largePrime

        Lagrange_Result = (l1*ownMPCshare + l2*otherMPCshare)%largePrime 
        
        print(f"Lagrange Result: {Lagrange_Result}")
    else:
        target = maxChar
        largePrime = number.getPrime(maxChar.bit_length() + 1)
        while largePrime <= maxChar:
            largePrime = number.getPrime(largePrime.bit_length() + 1)
        print(f"LARGE PRIME: {largePrime}")
        #largePrime = 8283616591

        
        coeff = random.randint(200,maxChar)
        print(f"Coeff: {coeff}")
        
        f2_share_1 = (ename + coeff * 1)%largePrime
        f2_share_2 = (ename + coeff * 2)%largePrime
        print(f"f2_share_1, f2_share_2: {f2_share_1}, {f2_share_2}")
        
        print(f"1 Sending largePrime, f2_share_1: {largePrime}, {f2_share_1}")
        
        client_socket.sendall(largePrime.to_bytes(bytes, byteorder='big'))
        client_socket.sendall(f2_share_1.to_bytes(bytes, byteorder='big'))
        
        # Recieve share from player 1
        f1_share_2 = int.from_bytes(client_socket.recv(bytes), byteorder='big')
        otherMPCshare = int.from_bytes(client_socket.recv(bytes), byteorder='big')
        
        print(f"2 Received f1_share_2, P1 MPC share: {f1_share_2}, {otherMPCshare}")
        
        ownMPCshare = (f1_share_2 + f2_share_2)%largePrime
        
        print(f"3 Sending P2 MPC share: {ownMPCshare}")
        client_socket.sendall(ownMPCshare.to_bytes(bytes, byteorder='big'))
        
        # Compute modular inverse
        inv_1_minus_2 = pow(1 - 2, -1, largePrime)  # (1 - 2) ^ -1 mod p
        inv_2_minus_1 = pow(2 - 1, -1, largePrime)  # (2 - 1) ^ -1 mod p

        l1 = ((0 - 2) * inv_1_minus_2) % largePrime
        l2 = ((0 - 1) * inv_2_minus_1) % largePrime

        Lagrange_Result = (l1*otherMPCshare + l2*ownMPCshare)%largePrime

        print(f"Lagrange Result: {Lagrange_Result}")
        
    if Lagrange_Result == ename*2:
        status.config(text="Name matches with other player!")
        names_matched.append(name_input)
    else:
        status.config(text="Name does not match with other player.")
    
def upload_file():
    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    global result
    if file_path:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                result = content.split(',')
                result = [item.strip() for item in result]
            if result != None:
                label.config(text=f"Read Selected File: {file_path}")
                print(result)
            else:
                label.config(text=f"Selected Is Empty: {file_path}")
        except Exception as e:
            return f"Error reading file: {e}"
            label.config(text=f"Selected File: {file_path}")
    else:
        label.config(text="No file selected")
    
    


upload_button = ttk.Button(root, text="Upload File", command=upload_file)
upload_button.grid(column = 0, row = 2)

label = ttk.Label(root, text="No file selected")
label.grid(column = 0, row = 3)
    
def read_input():
    method = None
    if result:
        print("Choosing file method")
        method = result
    else:
        INPUT = inputtxt.get("1.0", "end-1c")
        INPUT = INPUT.split(',')
        method = [item.strip() for item in INPUT] 
    
    if method:
        if playerNum == '1':
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((host, port))
            server_socket.listen(1)
        
            #RECIEVE LIST LENGTH OF PLAYER 2
            client_socket, addr = server_socket.accept()
            
            p2_list_length = int.from_bytes(client_socket.recv(4), byteorder='big')
            
            client_socket.sendall(len(method).to_bytes(4, byteorder='big'))
            
            print(f"P2 LIST LENGTH RECEIVED: {p2_list_length}")
            
            for name in method:
                for i in range(p2_list_length):
                    mpc_addition(name,client_socket)
            
            client_socket.close()
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
            client_socket.settimeout(2)
            while True:
                try:
                    client_socket.connect((host, port))
                    break
                except Exception as e:
                    print("Still trying to connect")
                time.sleep(2)        
            client_socket.sendall(len(method).to_bytes(4, byteorder='big'))
            
            p1_list_length = int.from_bytes(client_socket.recv(4), byteorder='big')
            
            print(f"P1 LIST LENGTH RECEIVED: {p1_list_length}")
            
                        
            for i in range(p1_list_length):
                for name in method:
                    mpc_addition(name,client_socket)
            
            client_socket.close()
        print(f"List of names that matched: {names_matched}")
    
def run_input_thread():
    thread = threading.Thread(target=read_input)
    thread.daemon = True
    thread.start()
    

status = ttk.Label(frm, text="Hello Player "+playerNum+". Enter Secret:")
status.grid(column = 0, row = 0)

inputtxt = Text(frm, height=10, width=25, bg="light yellow")
inputtxt.grid(column = 0, row = 1)

ttk.Button(frm, text="Send Secret", command=run_input_thread).grid(column = 0, row = 2, pady=10)






root.mainloop()