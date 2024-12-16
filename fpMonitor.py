from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sys

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

class pipelineMonitor(db.Model):
    __tablename__ = 'pipelineMonitor'
    id = db.Column(db.Integer, primary_key=True)
    libID = db.Column(db.String(64), unique=True, index=True)
    fqMonitor = db.Column(db.String(20))
    fpMonitor = db.Column(db.String(20))
    pearMonitor = db.Column(db.String(20))
    top15Monitor = db.Column(db.String(20))
    qcMonitor = db.Column(db.String(20))
    reportMonitor = db.Column(db.String(20))
    reportcheckMonitor = db.Column(db.String(20))
    remark = db.Column(db.Text)
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class SampleInfo(db.Model):
    __tablename__ = 'sampleinfo'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    projectBarcode = db.Column(db.String(20), index=True)
    projectName = db.Column(db.String(50), index=True)
    patientName = db.Column(db.String(10), index=True)
    patientID = db.Column(db.String(20), index=True)
    hospitalName = db.Column(db.String(50), index=True)
    sexName = db.Column(db.String(2))
    patientAge = db.Column(db.String(20))
    patientCardNo = db.Column(db.String(20))
    patientPhone = db.Column(db.String(20))
    sampleType = db.Column(db.String(20), index=True)
    hosDepartment = db.Column(db.String(20))
    patientNo = db.Column(db.String(20))
    bedNo = db.Column(db.String(20))
    doctorName = db.Column(db.String(20))
    clinicalDiagnosis = db.Column(db.String(100))
    sampleCollectionTime = db.Column(db.DateTime)
    sampleReceiveTime = db.Column(db.DateTime)
    diagnosisPeriod = db.Column(db.String(20), index=True)
    projectType = db.Column(db.String(20), index=True)
    reportTime = db.Column(db.DateTime)
    sampleStatus = db.Column(db.String(64), index=True)
    remark = db.Column(db.String(256))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

if __name__ == '__main__':
    with app.app_context():
        libID = sys.argv[1]
        labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = libID.split('/')[-1].split('.')[0].split('-')
        info = pipelineMonitor.query.filter(pipelineMonitor.libID == libID).first()
        if info:
            info.update(qcMonitor='已完成')
        else:
            print(f'{libID} 文库不存在，请核实！')

        sampleinfo = SampleInfo.query.filter(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod).first()
        if sampleinfo:
            sampleinfo.update(sampleStatus='已分析')
        else:
            print(f'{sampleBarcode} 样本不存在，请核实！')
        db.session.commit()
        