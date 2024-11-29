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
def get_sampleinfo():
    data = request.get_json()
    libinfo = pipelineMonitor.query.order_by(pipelineMonitor.addtime.desc()).paginate(page=data['page'], per_page=data['per_page'])
    res = []
    for i in libinfo:
        res.append(i.to_json())
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': libinfo.pages, 'data':res}})