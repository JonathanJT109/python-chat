import socket
import threading
from datetime import datetime
import random
from colorama import Fore, init, Back
import time

listen_port = 5555  # anything over 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", listen_port))
clients = {}

init()
colors = [
    Fore.BLUE,
    Fore.CYAN,
    Fore.GREEN,
    Fore.LIGHTBLACK_EX,
    Fore.LIGHTBLUE_EX,
    Fore.LIGHTCYAN_EX,
    Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX,
    Fore.LIGHTYELLOW_EX,
    Fore.MAGENTA,
    Fore.YELLOW,
]


class Client:
    def __init__(self, name, active_time, ban_counter, status, color):
        self.name = name
        self.active_time = active_time
        self.color = color
        self.status = status
        self.ban_counter = ban_counter


def listen_for_client():
    global s
    msg = "ping!"
    while True:
        del_list = []
        time.sleep(5)

        for client in clients.keys():
            s.sendto(msg.encode("UTF-8"), client)

        for addr in clients.keys():
            if clients[addr].active_time + 10 < time.time():
                del_list.append(addr)
                print(f"{addr}: {clients[addr].name} got removed!")

        for addr in del_list:
            del clients[addr]


thread = threading.Thread(target=listen_for_client).start()

while True:
    msg, addr = s.recvfrom(1024)
    msg = msg.decode("UTF-8")
    date_now = datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    if "user_name:" in msg:
        msg = msg.replace("user_name: ", "")
        client_color = random.choice(colors)
        new_client = Client(msg, time.time(), set(), "online", client_color)
        clients[addr] = new_client
        continue

    if "/msg" in msg:
        private_message = msg.split(" ")
        user_found = False
        for address in clients.keys():
            if clients[address].name == private_message[1]:
                msg = msg.replace(f"{private_message[0]} {private_message[1]} ", "")
                send_message = f"(PRIVATE) {clients[addr].color}[{date_now}] {clients[addr].name}: {msg}{Fore.RESET}"
                s.sendto(send_message.encode("UTF-8"), address)
                user_found = True
                break
        if not user_found:
            s.sendto("User has not been found".encode("UTF-8"), addr)
        continue
    elif "/ban" in msg:
        private_message = msg.split(" ")
        for address in clients.keys():
            if clients[address].name == private_message[1]:
                clients[address].ban_counter.add(addr)
                if len(clients[address].ban_counter) > 1:
                    s.sendto(
                        f"{Fore.RED}--YOU HAVE BEEN BANNED FROM THE CHAT--{Fore.RESET}".encode(
                            "UTF-8"
                        ),
                        address,
                    )
                    clients[address].status = "banned"
                break
        continue
    elif "/users" in msg:
        private_message = f"Number of users: {len(clients)}"
        s.sendto(private_message.encode("UTF-8"), addr)
        continue

    clients[addr].active_time = time.time()

    if msg == "active" or clients[addr].status == "banned":
        continue

    send_message = (
        f"{clients[addr].color}[{date_now}] {clients[addr].name}: {msg}{Fore.RESET}"
    )
    print(send_message)

    for c in clients.keys():
        if c == addr:
            continue
        s.sendto(send_message.encode("UTF-8"), c)
