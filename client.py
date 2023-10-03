import socket
import threading
import time

SERVER_PORT = 5555
SERVER_HOST = "127.0.0.1"

sock_ready = False
status = True
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def listen_thread():
    global s
    global sock_ready
    global status
    while not sock_ready:
        time.sleep(0.1)
    while status:
        (msg, addr) = s.recvfrom(1024)
        msg = msg.decode("UTF-8")

        if msg == "ping!":
            s.sendto("active".encode("UTF-8"), (SERVER_HOST, SERVER_PORT))
        else:
            print(msg)


welcome_message = """
Welcome to the Chat Room!
Please enter your name and a message to enter.
If you want to send a private message use "/msg" followed by the name and the message.

                    "/msg John Hello, how are you?"
                    
If you want to ban someone from texting in the chat room use "/ban" followed by the name.
You will need at least one more person to agree with your action. The user can still view
public conversations but is not able to type.

If you want to exit use the "/exit" command.
"""

print(welcome_message)

while True:
    name = input("Enter you name: ")
    if len(name) > 0:
        break

s.sendto(f"user_name: {name}".encode("UTF-8"), (SERVER_HOST, SERVER_PORT))

thread = threading.Thread(target=listen_thread).start()

print("-" * 20)
print("Start Typing")
print("-" * 20)
while True:
    user_input = input()
    if user_input == "/exit":
        print("You left the chat!")
        status = False
        break

    message = user_input

    s.sendto(message.encode("UTF-8"), (SERVER_HOST, SERVER_PORT))
    sock_ready = True
