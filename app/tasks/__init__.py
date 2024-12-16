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

celery_app = Celery('lym', broker=broker, backend=backend)
celery_app.conf.broker_connection_retry_on_startup = False

@celery_app.task
def onProcessPipline(sh,libID):
    labdate = libID.split('-')[0]
    spp = subprocess.run(sh, shell=True, stderr=subprocess.PIPE)
    if spp.returncode == 0:
        with apps.app_context():
            pipeinfo = pipelineMonitor.query.filter(pipelineMonitor.libID.contains(labdate)).all()
            top15Monitor = [p.top15Monitor for p in pipeinfo]
            if list(set(top15Monitor)) == ['已完成']:
                for i in pipeinfo:
                    sp = subprocess.run(f'echo beiyu98234 |sudo -S /opt/miniconda/bin/python /data/1-test-zrz/QC.cpython-37.pyc {i.libID}', shell=True, stderr=subprocess.PIPE)
        return '运行脚本成功！'
    else:
        return f'运行脚本失败！{spp.stderr}'

@celery_app.task
def sampleMonitor(libID):
    print(libID)
    labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = libID.split('/')[-1].split('.')[0].split('-')
    while True:
        if os.path.exists(f'/data/1-test-zrz/00_rawdata/{labdate}/{libID}_R1.fastq.gz') and os.path.exists(f'/data/1-test-zrz/00_rawdata/{labdate}/{libID}_R2.fastq.gz'):
            with apps.app_context():
                pipeinfo = pipelineMonitor.query.filter(pipelineMonitor.libID == libID).first()
                sampleinfo = SampleInfo.query.filter(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod ).first()
                print(pipeinfo.fqMonitor)
                if pipeinfo.fqMonitor == '不存在':
                    onProcessPipline.delay(f'echo beiyu98234 |sudo -S /opt/miniconda/bin/python /data/1-test-zrz/1-unix-1204.cpython-37.pyc {libID}',labdate)
                    pipeinfo.update(fqMonitor='已存在')
                    sampleinfo.update(sampleStatus='分析中')
                    db.session.commit()
                else:
                    break
            break
        else:
            print('文件不存在')
            time.sleep(10)