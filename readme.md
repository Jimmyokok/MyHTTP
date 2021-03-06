# Lab5 实验报告

## 1、基本信息

- 姓名：贾子安

- 学号：18307130017

- 选择题目：类Http协议下的学生信息管理系统

- 使用方法：分别在相应目录启动`client.py`和`server.py`后，使用浏览器打开http://127.0.0.1:9222访问
---------------------------

## 2、项目完成情况

### 2.1 MyHTTP协议


MyHTTP是一个类HTTP协议，专门为客户端与服务器间传输学生数据定制，协议报文格式分为请求和响应两种。报文字段分隔符为`\r\n`，头部和报文主体之间分隔符为`\r\n\r\n`。

请求格式：
- 请求包含两部分，请求头和请求主体，其中请求头包含通用信息头和实体头。
  
  - 通用信息头包含操作、URL和协议三部分，其间由空格隔开。例如：`ADD NULL MyHTTP\r\n`表示客户端请求服务器增加学生，其中URL字段为空，协议为MyHTTP。
  
  - 实体头包含除了通用信息以外客户端应该传递的信息，比如上传学生的学号姓名等信息，实体头中的内容以键值对形式`key:value`表示，如`id:123456`。

- 请求主体包含所有客户端要传输的无法以键值对表示的情况，比如图片内容等。

- 一个示例请求如下：
  ```py
  sample_request = b'ADD NULL MyHTTP\r\nLength:0\r\nid:10000\r\nname:adef\r\nphoto_path:a.jpg\r\n\r\n'
  ```

响应格式：
- 响应同样包含两部分，响应头和响应主体，其中响应头也包含通用信息头和实体头。
  
  - 通用信息头包含协议、状态码和状态文本三部分，其间由空格隔开。例如：`MyHTTP 200 OK\r\n`表示服务器接收到消息且状态正常。
  
- 实体头和请求主体的表示同请求完全相同。

- 一个示例响应如下：
  ```py
  sample_response = b'MyHTTP 400 Bad Request\r\n\r\nsql error!'
  ```
    
---------------------------

### 2.1 主要功能

请求姓名、学号、头像
- 客户端向服务端发送请求，包含相应学生学号；服务端响应相应的学生学号、姓名和头像URL。
- 后续可以根据头像URL再次向服务器发送请求完整图片进行显示。
- 加载学生列表时会发送一个特殊的请求，同时请求所有学生的信息，服务端响应时将会将学生信息通过响应主体发送。后续客户端将会遍历响应主体，对每一个头像URL进行请求后获取头像。

增加学生
- 客户端在验证用户输入的新学生信息合法后，将会发送一条请求给服务器，上传学生信息和图片URL，如果服务器成功响应，则后续再上传图片内容到服务器由服务器进行储存。

删除学生
- 客户端之间发送请求给服务器即可，由服务器判断传输数据是否合法。

修改学生
- 客户端在验证用户输入的新学生信息合法后，将会发送一条请求给服务器，上传学生信息和图片URL，同时服务器也需要判断输入新学生信息的合法性，因为学生学号是可能重复的。之后的操作和增加学生相同。
  
-----------------------------

### 2.2 其他功能

图形界面
- 使用Python Flask框架编写，浏览器获取页面时仍然使用**Http**协议，后端(客户端)与服务端的通信皆使用**MyHTTP**协议。
- 后端即为`client.py`
  
多线程连接
- 使用线程池处理并发连接情况，每个线程都能独立处理一个请求，不会因为等待请求而阻塞，在这里线程池总共有四个线程，最大连接数设为8。

---------------------------

## 3、参考资料

<a href="https://dormousehole.readthedocs.io/en/latest/">Python Flask




        

      

