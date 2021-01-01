import socket
import os
import MySQLdb as mysql
from threading import Thread
from queue import Queue

db = mysql.connect("localhost","root","root","student",charset="utf8")
cursor = db.cursor()

HOST = '127.0.0.1'
PORT = 65432

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(8)

class ThreadPoolManger():

    def __init__(self, thread_num):
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        for i in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.start()

    def add_job(self, func, *args):
        self.work_queue.put((func, args))

class ThreadManger(Thread):
    
    def __init__(self, work_queue):
        Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        while True:
            target, args = self.work_queue.get()
            target(*args)
            self.work_queue.task_done()

def write_file(path, content):
    file = open(path, 'wb+')
    filedata = content
    file.write(filedata)
    file.close()
    return

def file_reader(path):
    file = open(path, 'rb')
    result = b''
    while True:
        filedata = file.read(1024)
        if not filedata:
            break
        result += filedata
    file.close()
    return result

def send_file(path, pairs, content, responses):
    file_content = b''
    try:
        file_content = file_reader("./img/%s" %(path))
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    if not file_content:
        status_handler(400, "File empty or not exist.", responses)
        return
    status_handler(200, file_content, responses)
    return

def receive_file(path, pairs, content, responses):
    try:
        write_file("img/%s" %(path), content)
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    status_handler(200,'', responses)
    return
    
def response_creator(responses):
    response_head = "MyHTTP"
    response_head += ';' + responses["status"]
    response_head += ';' + responses["text"] + '\r\n'
    response_body = b''
    content = b''
    for key in responses.keys():
        if key == "status" or key == "text":
            continue
        elif key == "content":
            try:
                content = responses['content'].encode()
            except Exception:
                content = responses['content']
        else:
            response_body += (key + ':' + responses[key] + '\r\n').encode()
    response_body += '\r\n'.encode()
    response_body += content
    length = len(response_body)
    response_head += "Length:" + str(length) + '\r\n'
    return response_head.encode() + response_body

def status_handler(status, content, responses):

    responses['status'] = str(status)
    if status == 400:
        responses['text'] = 'Bad request'
    elif status == 417:
        responses['text'] = 'Expectation Failed'
    elif status == 200:
        responses['text'] = 'OK'
    elif status == 201:
        responses['text'] = 'Created'
    elif status == 202:
        responses['text'] = 'Accepted'
    if content != '':
        responses['content'] = content
    return

def add_student(path, pairs, content, responses):
    if "photo_path" in pairs.keys():
        sql = "INSERT INTO student (id, name, photo_path) VALUES ('%s', '%s', '%s');" %(pairs["id"],pairs["name"],pairs["photo_path"])
    else:
        sql = "INSERT INTO student (id, name) VALUES ('%s', '%s');" %(pairs["id"],pairs["name"])
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    status_handler(200, '', responses)
    return
    
def delete_student(path, pairs, content, responses):
    sql = "SELECT photo_path FROM student WHERE id = '%s';" %(pairs["id"])
    try:
        cursor.execute(sql)
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    row = cursor.fetchone()
    photo_path = str(row[0])
    sql = "DELETE FROM student WHERE id = '%s'" %(pairs["id"])
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    try:
        os.remove("img/%s" %(photo_path))
    except Exception:
        status_handler(200, '', responses)
        return
    status_handler(200, '', responses)
    return

def modify_student(path, pairs, content, responses):
    if "photo_path" in pairs.keys():
        sql = "UPDATE student SET name = '%s', photo_path = '%s' WHERE id = '%s';" %(pairs["name"],pairs["photo_path"],pairs["id"])
    else:
        sql = "UPDATE student SET name = '%s' WHERE id = '%s';" %(pairs["name"],pairs["id"])
    try:
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    status_handler(200, '', responses)
    return

def check_student(path, pairs, content, responses):
    sql = "SELECT * FROM student WHERE id = '%s';" %(pairs["id"])
    try:
        cursor.execute(sql)
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    row = cursor.fetchone()
    responses['id'] = str(row[1])
    responses['name'] = str(row[0])
    responses['photo_path'] = str(row[2])
    status_handler(200, '', responses)
    return

def check_all_student(path, pairs, content, responses):
    sql = "SELECT * FROM student;"
    try:
        cursor.execute(sql)
    except Exception as e:
        status_handler(400, str(e), responses)
        return
    rows = cursor.fetchall()
    content = ""
    for row in rows:
        stuid = str(row[0])
        name = str(row[1])
        photo_path = str(row[2])
        string = stuid + ' ' + name + ' ' + photo_path
        content += string +'\r\n'
    status_handler(200, content, responses)
    return

def extract_head(head_text):
    head_texts = head_text.split(' ')
    op = head_texts[0]
    path = head_texts[1]
    prot = head_texts[2]
    return [op, path, prot]

def handle_request(connection):
    response = b''
    while True:
        data = connection.recv(1024)
        response += data
        if not data or len(data) < 1024:
            break

        # 分割报文

    [head_content, body_content] = response.split('\r\n\r\n'.encode())
    head_content = head_content.decode()
    heads = head_content.split('\r\n')

        # Head
            # op --- operation
            # path --- path of file
            # prot --- protocol
            # Other fields are presented in "key:value" form

    head = heads[0]
    head_texts =  extract_head(head)
    op = head_texts[0]
    path = head_texts[1]
    prot = head_texts[2]

    pairs = {}
    for i in range(1, len(heads)):
        pair_str = heads[i]
        pair = pair_str.split(':')
        pairs[pair[0]] = pair[1]

        # 处理请求

    responses = {}
    if prot != "MyHTTP":
        status_handler(417, 'Wrong protocol', responses)
    elif op == "ADD":
        add_student(path, pairs, body_content, responses)
    elif op == "DELETE":
        delete_student(path, pairs, body_content, responses)
    elif op == "CHECK":
        check_student(path, pairs, body_content, responses)
    elif op == "MODIFY":
        modify_student(path, pairs, body_content, responses)
    elif op == "ALL":
        check_all_student(path, pairs, body_content, responses)
    elif op == "IMGGET":
        send_file(path, pairs, body_content, responses)
    elif op == "IMGPOST":
        receive_file(path, pairs, body_content, responses)
    else:
        status_handler(417, 'Not supported', responses)
    response = response_creator(responses)
    connection.send(response)
    connection.close()


def server_listen():
    thread_pool = ThreadPoolManger(4)
    while True:  # 循环轮询socket状态，等待访问
        conn, addr = s.accept()
        thread_pool.add_job(handle_request, *(conn, ))
    s.close()

        

server_listen()