from flask import Blueprint, jsonify, g, request
from app.usermodels import Menu
from flask_jwt_extended import jwt_required
from collections import defaultdict
from app.tasks import onProcessPipline

menu = Blueprint('menu', __name__)

@menu.get('/menulist')
@jwt_required()
def menulist():
    order = ['首页', '实验处理', '报告分析', '用户管理']
    resp = {'msg': '', 'code': '', 'data': []}
    mlist = Menu.query.all()
    subname = defaultdict(list)
    subpath = defaultdict(list)
    for i in mlist:
        if i.subname != '核酸提取' and i.subname != '文库构建':
            if g.department == 'root':
                subname[i.name].append(i.subname)
                subpath[i.name].append(i.subpath)
            elif g.department == i.department or i.department == 'Public':
                subname[i.name].append(i.subname)
                subpath[i.name].append(i.subpath)
    listsubs = sorted(subname.keys(), key=order.index)
    for e in listsubs:
        resp['data'].append({'name': e, 'subname': subname[e], 'subpath': subpath[e]})
    resp['msg'] = 'get menulist success!'
    resp['code'] = 200

    return jsonify(resp)
