from flask import Blueprint, request, jsonify, g
from app.models import SampleInfo, delSampleInfo, addPatientID, experimenttohos,addexperimentID, pendingSample
from app import db
from flask_jwt_extended import jwt_required
from app.tasks import onProcessPipline
from datetime import datetime
from sqlalchemy import between, and_, or_
import requests
import subprocess
from app.utils import changeUTCtoLocal, addOneday
from collections import defaultdict

pipeline = Blueprint('pipeline', __name__)

@pipeline.post('/runPipeline')
@jwt_required
def runPipeline():
    shell = request.json['shell']
    res = onProcessPipline.delay(shell)
    return {'code':200, 'msg':res.id}

