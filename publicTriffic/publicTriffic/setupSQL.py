# -*- coding =utf-8 -*-
import shelve

host = input("请输入地址")
port = int(input("请输入端口"))
user = input("输入用户名")
password = input("输入密码")
DBname = input("输入数据库名")
db = shelve.open('db/SQL')
SQLdict = {
    'host': host,
    'port': port,
    'user': user,
    "password": password,
    'DBname': DBname
}
db['db'] = SQLdict
print("初始化完成")
