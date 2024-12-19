
from flask import Blueprint, request, jsonify, g
from app.usermodels import User
from app.models import testandcheck
from app import db
from flask_jwt_extended import jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
import base64
import random  
import string

user = Blueprint('user', __name__)

##获取token并登录
@user.post('/login')
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        return {'msg': f'用户不存在！', 'code': 412}
    if not check_password_hash(user.password, password):
        return {'msg': f'密码错误！', 'code': 412}
    return jsonify({'msg': '登录成功！','username':username, 'code': 200, 'token': user.generate_auth_token()})

##验证token是否有效
@user.get('/check_token')
@jwt_required()
def check_token():
    return jsonify({'msg':'success', 'code':200})

##注册新用户
@user.post('/addUser')
@jwt_required()
def addUser():
    print(request.get_json())
    if g.username == 'root':
        data = request.json['data']
        print(data)
        username = data['username']
        password = data['password']
        department = data['department']
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({'msg':'用户已存在！', 'code':412})
        else:
            u = User(username=username, password=generate_password_hash(password), department=department)
            db.session.add(u)
            db.session.commit()
            return jsonify({'msg':'注册成功！', 'code':200})

##删除用户
@user.post('/deleteUser')
@jwt_required()
def deleteUser():
    if g.username == 'root':
        data = request.json['data']
        print(data)
        username = data['username']
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'msg':'删除成功！', 'code':200})

##修改用户密码
@user.post('/changePassword')
@jwt_required()
def changePassword():
    print(request.get_json())
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user:
        user.update(password=generate_password_hash(password))
        db.session.commit()
        return jsonify({'msg':'修改密码成功！', 'code':200})
    else:
        return jsonify({'msg':'用户不存在！', 'code':412})

##获取用户列表
@user.get('/getUserList')
@jwt_required()
def getUserList():
    department = {'Laboratory':'实验处理', 'Bioinfo':'报告分析', 'root':'管理员'}
    userList = User.query.filter(User.username != 'root').all()
    if not userList:
        return jsonify({'msg':'用户列表为空！', 'code':412})
    res = []
    for i in userList:
        i = i.to_json()
        i['department'] = department[i['department']]
        res.append({'username':i['username'], 'department':i['department'], 'addtime':i['addtime']})
    return jsonify({'msg':'success', 'code':200, 'data':res})

##上传签名图片
@user.post('/uploadSignature')
@jwt_required()
def uploadSignature():
    username = request.json['username']
    signature = request.json['signature']
    imgdata = base64.b64decode(signature)
    random_letters = ''.join(random.choices(string.ascii_letters, k=6))
    info = testandcheck.query.filter(testandcheck.Name == username).first()
    if info:
        return jsonify({'msg':'签名已存在！', 'code':412})
    else:    
        #将图片保存为文件
        with open(f"/data/yubei/Biotech_report/images/{random_letters}.png",'wb') as f:
            f.write(imgdata)
        return jsonify({'msg':'success', 'code':200})
    
##删除签名图片
@user.post('/deleteSignature')
@jwt_required()
def deleteSignature():
    username = request.json['username']
    info = testandcheck.query.filter(testandcheck.Name == username).first()
    if info:
        db.session.delete(info)
        db.session.commit()
        return jsonify({'msg':'删除成功！', 'code':200})
    else:
        return jsonify({'msg':'签名不存在！', 'code':412})