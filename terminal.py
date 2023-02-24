import socket
import sys
import time
import threading

from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager

send_cond = False
recv_cond = False

send_msg = ''
recv_msg = ''

PHONE_IP = socket.gethostbyname(socket.gethostname())
PORT_NUMBER = 5005
SIZE = 1024


def sender():
    global send_msg, send_cond
    while True:
        try:
            while send_cond:
                send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                send_socket.connect((PHONE_IP, PORT_NUMBER))
                print('connect')
                while True:
                    if send_msg != '':
                        send_socket.send(bytes(send_msg, 'utf-8'))
                        send_msg = ''
        except:
            time.sleep(0.5)


thread_1 = threading.Thread(target=sender)


def receiver():
    global recv_msg, recv_cond

    while recv_cond:
        try:
            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            recv_socket.bind((PHONE_IP, PORT_NUMBER))
            recv_socket.listen(10)
            print('binded')
            while True:
                listen_socket, address = recv_socket.accept()
                while True:
                    raw_msg = listen_socket.recv(1024)
                    recv_msg = raw_msg.decode('utf-8')
        except:
            time.sleep(0.5)
            print('binding...')


thread_2 = threading.Thread(target=receiver)


class WindowManager(MDScreenManager):
    pass


class WelcomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def initiate(self):
        global send_cond
        send_cond = True
        self.manager.current = 'mainscreen'
        Clock.schedule_interval(self.manager.ids.mainscreen.listen, 0.5)


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def listen(self, *args):
        global recv_msg
        if recv_msg != '':
            print(recv_msg)
            recv_msg = ''

    def send(self):
        global send_msg
        send_msg = 'Terminal' + self.ids.msg.text

    def handle(self, conn, addr):
        while True:
            data = conn.recv(SIZE)
            if not data:
                break
            print(f"Received message from {addr[0]}: {data.decode()}")
            self.ids.label.text = data.decode()
        conn.close()


class TerminalApp(MDApp):
    def build(self):
        return Builder.load_file('terminal.kv')


if __name__ == "__main__":
    thread_1.start()
    thread_2.start()
    threading.Thread(target=TerminalApp().run())
    send_cond = False
    recv_cond = False
