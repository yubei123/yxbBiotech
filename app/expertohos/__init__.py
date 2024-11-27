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
    try:
        for i in data:
            qcinfo = qctohos.query.filter(qctohos.qcDate == i['qcDate']).first()
            if not qcinfo:
                return jsonify({'msg': f'没有 {i["qcDate"]} 批次的内参信息，请先导入！', 'code': 204})
            if 'experimentID' not in i:
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
                i['experimentID'] = f'{today}_{str(experID_num).zfill(4)}'
                exp = experimenttohos(**i)
                db.session.add(exp)
            else:
                exp = experimenttohos.query.filter(experimenttohos.experimentID==i['experimentID']).first()
                if exp:
                    exp.update(**i)
        db.session.commit()
        return jsonify({'msg': 'success', 'code': 200})
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
    info = query.paginate(page=data['pagenum'], per_page=5)
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
        for i in data:
            qcinfo = qctohos.query.filter(qctohos.qcDate==i['qcDate']).first()
            if qcinfo:
                qcinfo.update(**i)
            else:
                qcinfo = qctohos(**i)
                db.session.add(qcinfo)
        db.session.commit()
        return jsonify({'msg': 'success', 'code': 200})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg': 'fail', 'code': 500})

@expertohos.post('/searchqcinfo')
@jwt_required()
def searchqcinfo():
    data = request.get_json()
    n = 0
    query = qctohos.query
    if data['qcDate'] != '':
        query = query.filter(qctohos.qcDate == data['qcDate'])
        n += 1
    info = query.paginate(page=data['pagenum'], per_page=5)
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