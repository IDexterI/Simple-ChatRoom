import rpyc.utils.server as rpycs
import rpyc
import pymysql
import socket
import threading

online_users = []
user_sockets = {}

def listen_to_user(client_socket, username):
    while True:
        data = client_socket.recv(1024)
        data = data.decode()
        data = "msg:"+username+":"+data
        data = data.encode()
        for cs in user_sockets.values():
            cs.send(data)

def send_online_users_to_all():
    data = "user:"+str(online_users)
    data = data.encode()
    for connection in user_sockets.values():
        connection.send(data)

def start_server():
    server_socket = socket.socket()
    server_socket.bind(("localhost", 12346))
    server_socket.listen(5)
    while True:
        connection, address = server_socket.accept()
        user_sockets[online_users[-1]] = connection
        send_online_users_to_all()
        threading.Thread(target=listen_to_user, args=(connection, online_users[-1])).start()


class MyService(rpyc.Service):

    def exposed_register(self, username, password1, password2, email):
        sql = "INSERT into user values(%s,%s,%s)"
        if password2 != password1:
            return False
        try:
            self.check_connection()
            self.cursor.execute(sql, (username, password1, email))
            self.connection.commit()
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def exposed_login(self, username, password):
        sql = "SELECT * from user where username=%s and password=%s"
        try:
            self.check_connection()
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchall()
            if len(result) > 0:
                online_users.append(username)
                return True
            else:
                return False
        except:
            return False

    def check_connection(self):
            self.connection = pymysql.connect(host="localhost", user="chat", password="chat", db="chat")
            self.cursor = self.connection.cursor()


if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    rpcServer = rpycs.ThreadedServer(MyService, port=12345)
    rpcServer.start()