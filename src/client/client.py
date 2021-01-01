from flask import Flask, render_template, request, redirect, url_for, request
import socket
import os, base64
import random
app = Flask(__name__)

sample_request = b'ADD NULL MyHTTP\r\nLength:0\r\nid:10000\r\nname:adef\r\nphoto_path:a.jpg\r\n\r\n'

HOST = '127.0.0.1'
PORT = 65432

@app.route('/Add',methods=['POST'])
def addstudent():
    filedata = request.files.get('file')
    filename = str(random.randint(1000000000,9999999999)) +'.' + filedata.filename.split('.')[1]
    filedata.save("static/img/%s" %(filename))
    send_file(filename)
    # 数据库增加学生
    request_str = create_request('ADD', '', {'id':request.form['id'], 'name':request.form['name'], 'photo_path': filename}, '')
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.send(request_str)
    prot, status, text, head, content = response_translator(s)
    s.close()
    return redirect(url_for('home'))

@app.route('/Modify',methods=['POST'])
def modifystudent():
    try:
        filedata = request.files.get('file')
        filename = filename = str(random.randint(1000000000,9999999999)) +'.' + filedata.filename.split('.')[1]
        filedata.save("static/img/%s" %(filename))
        send_file(filename)
        request_str = create_request('MODIFY', '', {'id':request.form['id'], 'name':request.form['name'], 'photo_path': filename}, '')
    except Exception:
        request_str = create_request('MODIFY', '', {'id':request.form['id'], 'name':request.form['name']}, '')
    # 数据库增加学生
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.send(request_str)
    prot, status, text, head, content = response_translator(s)
    s.close()
    return redirect(url_for('home'))


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

def send_file(path):
    file_content = b''
    file_content = file_reader("static/img/%s" %(path))
    request = create_request('IMGPOST',path,{}, file_content)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.send(request)
    prot, status, text, head, content = response_translator(s)
    s.close()
    if prot != 'MyHTTP' or status != '200':
        return -1
    return 0


def create_request(op, path, heads, content):
    request_head = ""
    request_head += op + ' '
    request_head += path + ' '
    request_head += 'MyHTTP\r\n'
    request_body = b''
    final_content = b''
    for key in heads.keys():
        request_body += (key + ':' + heads[key] + '\r\n').encode()
    request_body += '\r\n'.encode()
    try:
        final_content = content.encode()
    except Exception:
        final_content = content
    request_body += final_content
    length = len(request_body)
    request_head += "Length:" + str(length) + '\r\n'
    return request_head.encode() + request_body

def extract_head(head_text):
    head_texts = head_text.split(';')
    prot = head_texts[0]
    status = head_texts[1]
    text = head_texts[2]
    return [prot, status, text]

def response_translator(s):
    response = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data
    
    [head_content, body_content] = response.split('\r\n\r\n'.encode())
    head_content = head_content.decode()
    heads = head_content.split('\r\n')
    head = heads[0]
    head_texts =  extract_head(head)
    prot = head_texts[0]
    status = head_texts[1]
    text = head_texts[2]
    pairs = {}
    for i in range(1, len(heads)):
        pair_str = heads[i]
        pair = pair_str.split(':')
        pairs[pair[0]] = pair[1]
    return prot, status, text, pairs, body_content
    
def content_to_student_info(content):
    try:
        student_infos = content.split('\r\n')
    except Exception:
        student_infos = content.decode().split('\r\n')
    students = []
    if student_infos == ['']:
        return []
    for student_info in student_infos:
        if student_info == '':
            continue
        attributes = student_info.split(' ')
        students.append({"name":attributes[0],"id":attributes[1],"photo_path":attributes[2]})
    return students
    
def fetch_all_students():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    request = create_request('ALL','',{}, ''.encode())
    s.send(request)
    prot, status, text, head, content = response_translator(s)
    s.close()
    if prot != 'MyHTTP' or status != '200':
        return -1
    global students
    students = content_to_student_info(content)
    for student in students:
        path = student['photo_path']
        if path == "None":
            continue
        request = create_request('IMGGET',path,{'id':student['id']}, ''.encode())
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        s.send(request)
        prot, status, text, head, content = response_translator(s)
        s.close()
        if prot != 'MyHTTP' or status != '200':
            return -1
        write_file("static/img/%s" %(student['photo_path']), content)
    return 0

def fetch_students(stuid):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    request = create_request('CHECK','',{'id':stuid}, ''.encode())
    s.send(request)
    prot, status, text, head, content = response_translator(s)
    s.close()
    student = {}
    if prot != 'MyHTTP' or status != '200':
        return student, -1
    student['id'] = head['id']
    student['name'] = head['name']
    try:
        student['photo_path'] = head['photo_path']
    except Exception:
        return student, -1
    path = student['photo_path']
    if path == "None":
        return student, -1
    request = create_request('IMGGET',path,{'id':student['id']}, ''.encode())
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.send(request)
    prot, status, text, head, content = response_translator(s)
    s.close()
    if prot != 'MyHTTP' or status != '200':
        return student, -1
    write_file("static/img/%s" %(student['photo_path']), content)
    return student, 0
    
@app.route('/')
def home():
    fetch_all_students()
    return render_template('home.html', students = students)

@app.route('/add')
def add():
    return render_template('modify.html', type = 'Add', student = {'id':'', 'name':'', 'photo_path':'No image here'})

@app.route('/modify/<stuid>')
def modify(stuid):
    student, errcode = fetch_students(stuid)
    if errcode != 0:
        return render_template('home.html', students = students)
    return render_template('modify.html', type = 'Modify',student = student)

@app.route('/delete/<stuid>')
def delete(stuid):
    request_str = create_request('DELETE', '', {'id':stuid}, '')
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.send(request_str)
    prot, status, text, head, content = response_translator(s)
    s.close()
    return redirect(url_for('home'))

if __name__ == "__main__":
	app.run(host='127.0.0.1', port=9222)