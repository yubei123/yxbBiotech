from flask import Blueprint, request, jsonify, g
from app.models import SampleInfo, experimenttohos, qctohos, addexperimentID
from app import db
from app.utils import changeUTCtoLocal, addOneday
from flask_jwt_extended import jwt_required
from sqlalchemy import between, or_
from datetime import datetime

expertohos = Blueprint('expertohos', __name__)

### 导入实验信息
@expertohos.post('/inputexperinfo')
@jwt_required()
def inputexperinfo():
    today = datetime.now().strftime('%Y%m%d')
    data = request.json['data']
    # print(data)
    try:
        experID = addexperimentID.query.all()
        experID_num = 0
        if not experID:
            experID_num = 1
        else:
            experIDs = experID[-1].experimentIDs
            if today in experIDs:
                experID_num = int(experIDs[-4:]) + 1
            else:
                experID_num = 1
        experID_list = []
        ## 导入实验信息，判断是否存在对应的内参批次信息，不存在不允许更新
        for i in data:
            qcinfo = qctohos.query.filter(qctohos.qcDate == i['qcDate']).first()
            if not qcinfo and '空白' not in i['patientName']:
                return jsonify({'msg': f'没有 {i["qcDate"]} 批次的内参信息，请先导入！', 'code': 204})
            ## 如果导入的实验信息中不存在实验编号，则重新生成新的实验编号并添加新的实验信息
            if 'experimentID' not in i:
                i['experimentID'] = f'{today}_{str(experID_num).zfill(4)}'
                experID_list.append(i['experimentID'])
                exp = experimenttohos(**i)
                db.session.add(addexperimentID(**{'experimentIDs':f'{today}_{str(experID_num).zfill(4)}'}))
                experID_num += 1
                db.session.add(exp)
            ## 如果导入的实验信息中存在实验编号，则根据对应实验编号对实验信息进行更新
            else:
                if i['experimentID'] == '':
                    i['experimentID'] = f'{today}_{str(experID_num).zfill(4)}'
                    experID_list.append(i['experimentID'])
                    exp = experimenttohos(**i)
                    db.session.add(addexperimentID(**{'experimentIDs':f'{today}_{str(experID_num).zfill(4)}'}))
                    experID_num += 1
                    db.session.add(exp)
                else:
                    exp = experimenttohos.query.filter(experimenttohos.experimentID==i['experimentID']).first()
                    experID_list.append(i['experimentID'])
                    if exp:
                        exp.update(**i)
        db.session.commit()
        experinfo_list = []
        for i in experID_list:
            experinfo = experimenttohos.query.filter(experimenttohos.experimentID == i).first()
            experinfo_list.append(experinfo.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data':experinfo_list})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg': 'fail', 'code': 500})

@expertohos.post('/searchexperinfo')
@jwt_required()
def searchexperinfo():
    data = request.get_json()
    n = 0
    query = experimenttohos.query
    if data['sampleBarcode'] != '':
        query = query.filter(experimenttohos.sampleBarcode == data['sampleBarcode'])
        n += 1
    if data['patientID'] != '':
        query = query.filter(experimenttohos.patientID == data['patientID'])
        n += 1
    if data['labDate'] != '':
        query = query.filter(experimenttohos.labDate == data['labDate'])
        n += 1
    if data['diagnosisPeriod'] != '':
        query = query.filter(experimenttohos.diagnosisPeriod.contains(data['diagnosisPeriod']))
        n += 1
    if data['qcDate'] != '':
        query = query.filter(experimenttohos.qcDate == data['qcDate'])
        n += 1
    if data['labSite'] != '':
        query = query.filter(experimenttohos.labSite.contains(data['labSite']))
        n += 1
    if data['addtime'] != '':
        stime = changeUTCtoLocal(data["addtime"])
        etime = addOneday(data["addtime"])
        query = query.filter(between(experimenttohos.addtime, stime, etime))
        n += 1
    info = query.paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in info]
    if not a or n == 0:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in info:
            res.append(i.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': info.pages, 'data':res}})

### 导入内参信息
@expertohos.post('/inputqcinfo')
@jwt_required()
def inputqcinfo():
    data = request.json['data']
    try:
        qcdate_list = []
        for i in data:
            qcdate_list.append(i['qcDate'])
            qcinfo = qctohos.query.filter(qctohos.qcDate==i['qcDate']).first()
            if qcinfo:
                qcinfo.update(**i)
            else:
                qcinfo = qctohos(**i)
                db.session.add(qcinfo)
        db.session.commit()
        qcinfo_list = []
        for i in qcdate_list:
            info = qctohos.query.filter(qctohos.qcDate==i).first()
            qcinfo_list.append(info.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data':qcinfo_list})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg': 'fail', 'code': 500})

@expertohos.post('/searchallqc')
@jwt_required()
def searchallqc():
    data = request.get_json()
    qcinfo = qctohos.query.order_by(qctohos.addtime.desc()).paginate(page=data['pagenum'], per_page=data['pagesize'])
    res = []
    for i in qcinfo:
        res.append(i.to_json())
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': qcinfo.pages, 'data':res}})

## 搜索指定内参批次
@expertohos.post('/searchqcinfo')
@jwt_required()
def searchqcinfo():
    data = request.get_json()
    n = 0
    query = qctohos.query
    if data['qcDate'] != '':
        query = query.filter(qctohos.qcDate.contains(data['qcDate']))
        n += 1
    info = query.paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in info]
    if not a or n == 0:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in info:
            res.append(i.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': info.pages, 'data':res}})

### 待补充实验信息
@expertohos.get('/searchaddexperinfo')
@jwt_required()
def searchaddexperinfo():
    experinfo = experimenttohos.query.filter(or_(experimenttohos.labDate == None, experimenttohos.labDate == '')).order_by(experimenttohos.addtime.desc()).all()
    if not experinfo:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in experinfo:
            res.append(i.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data': res})