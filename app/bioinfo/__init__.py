from flask import Blueprint, request, jsonify, g
from app.models import SampleInfo, experimenttohos, qctohos, pipelineMonitor
from app import db
from app.utils import changeUTCtoLocal, addOneday
from flask_jwt_extended import jwt_required
from sqlalchemy import between, or_, and_
from datetime import datetime
from collections import defaultdict

bioinfo = Blueprint('bioinfo', __name__)

@bioinfo.post('searchlibanalysis')
@jwt_required()
def searchlibanalysis():
    data = request.get_json()
    libinfo = pipelineMonitor.query.order_by(pipelineMonitor.addtime.desc()).paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in libinfo]
    if not a:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in libinfo:
            res.append(i.to_json())
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': libinfo.pages, 'data':res}})

@bioinfo.post('getreportsample')
@jwt_required()
def getreportsample():
    data = request.get_json()
    sampleinfo = SampleInfo.query.filter(SampleInfo.sampleStatus != '已出报告').order_by(SampleInfo.addtime.desc()).paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in sampleinfo]
    if not a:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in sampleinfo:
            res.append(i.to_json())
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': sampleinfo.pages, 'data':res}})

@bioinfo.post('getreportinfo')
@jwt_required()
def getreportinfo():
    data = request.get_json()
    experinfo = experimenttohos.query.filter(experimenttohos.sampleBarcode == data['sampleBarcode'], experimenttohos.diagnosisPeriod == data['diagnosisPeriod']).all()
    if not experinfo:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = [i.to_json() for i in experinfo]
        return jsonify({'msg': 'success', 'code': 200, 'data': res})