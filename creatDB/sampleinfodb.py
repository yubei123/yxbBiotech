from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from glob import glob

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

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

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()