from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.uic import loadUi
import sys
import rpyc
import socket
import threading



socket_connection = None


def start_listening():
    while True:
        data = socket_connection.recv(1024)
        data = data.decode()
        type = data[:5]
        msg = data[4:]
        if type == "user:":
            msg = eval(msg)
            chat.userListView.clear()
            chat.userListView.addItems(msg)
        else:
            chat.chatView.append("\n"+msg)


def show_register_panel():
    register.show()


def send():
    msg = chat.messageLineEdit.text()
    msg = msg.encode()
    socket_connection.send(msg)


def registeration():
    global email
    username = register.usernameLineEdit.text()
    password1 = register.password1LineEdit.text()
    password2 = register.password2LineEdit.text()
    email = register.emailLineEdit.text()
    result = service.register(username, password1, password2, email)
    print(result)


def client_socket():
    global socket_connection
    socket_connection = socket.socket()
    socket_connection.connect(("localhost", 12346))
    threading.Thread(target=start_listening).start()


def login_action():
    username = login.usernameLineEdit.text()
    password = login.passwordLineEdit.text()
    result = service.login(username, password)
    if result:
        chat.show()
        client_socket()
    else:
        print("error")


def show_verification_panel():
    verification.show()


def email_verification():
    entered_email = register.emailLineEdit.text()
    result = service.register(entered_email)
    print(result)

def verification_code_check():
    verification_code = verification.codelineEdit.text()
    result = service.register(verification_code)
    print(result)


if __name__ == '__main__':
    service = rpyc.connect(host="127.0.0.1", port=12345).root
    app = QApplication(sys.argv)

    login = loadUi("../ui/login.ui")
    register = loadUi("../ui/register.ui")
    chat = loadUi("../ui/chat.ui")
    verification = loadUi("../ui/verification_code.ui")

    login.registerButton.clicked.connect(show_register_panel)
    login.loginButton.clicked.connect(login_action)

    #register.registerButton.clicked.connect(registeration)
    register.registerButton.clicked.connect(show_verification_panel)
    #verification.verification_button.clicked.connect(email_verification)
    verification.registerButton.clicked.connect(verification_code_check)
    chat.sendButton.clicked.connect(send)

    login.show()


    app.exec()
