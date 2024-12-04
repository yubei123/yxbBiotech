from celery import Celery
import subprocess, os
from flask import Flask
from flask_jwt_extended import jwt_required
from app import db
from app.models import SampleInfo, pipelineMonitor
from sqlalchemy import and_
import time

apps = Flask(__name__)
apps.config.from_pyfile('/data/yubei/Biotech/config.py')
db.init_app(apps)

broker = 'redis://127.0.0.1:6379/0'
backend = 'redis://127.0.0.1:6379/1'

celery_app = Celery('lym', broker=broker, backend=backend, include=["app.tasks"])

@celery_app.task
@jwt_required()
def onProcessPipline(sh):
    spp = subprocess.run(sh, shell=True, stderr=subprocess.PIPE)
    if spp.returncode == 0:
        return '运行脚本成功！'
    else:
        return f'运行脚本失败！{spp.stderr}'

@celery_app.task
@jwt_required()
def sampleMonitor(libID):
    while True:
        if os.path.exists(f'/data/yubei/Biotech/testdata/{libID}_R1.fastq.gz') and os.path.exists(f'/data/yubei/Biotech/testdata/{libID}_R2.fastq.gz'):
            pipeinfo = pipelineMonitor.query.filter(pipelineMonitor.libID == libID).first()
            if pipeinfo.fqMonitor == '不存在':
                re = onProcessPipline.delay(f'touch 1.txt')
                pipeinfo.update(fqMonitor='已存在')
                print(re)
            break
            db.session.commit()
        else:
            print('文件不存在')
            time.sleep(5)


