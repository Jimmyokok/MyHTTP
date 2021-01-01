import socket

HOST = '127.0.0.1'
PORT = 65432

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(b'DELETE /user/u18307130017/a.txt MyHTTP\r\nLength:20\r\nid:5\r\n\r\n')
data = s.recv(1024)
if not data:
    s.close()
print("Received data:",data)
s.close()