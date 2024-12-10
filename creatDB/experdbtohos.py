from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from glob import glob

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

class experimenttohos(db.Model):
    __tablename__ = 'experimenttohos'
    id = db.Column(db.Integer, primary_key=True)
    experimentID = db.Column(db.String(20), unique=True, index=True)
    patientName = db.Column(db.String(10), index=True)
    labDate = db.Column(db.String(8), index=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    diagnosisPeriod = db.Column(db.String(20), index=True)
    barcodeGroup = db.Column(db.String(10))
    labSite = db.Column(db.String(10))
    labUser = db.Column(db.String(20))
    inputNG = db.Column(db.String(8))
    expectedReads = db.Column(db.String(20))
    qcDate = db.Column(db.String(8), index=True)
    pcrSite = db.Column(db.String(10), index=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)

class qctohos(db.Model):
    __tablename__ = 'qctohos'
    id = db.Column(db.Integer, primary_key=True)
    qcDate = db.Column(db.String(8), index=True)
    igh = db.Column(db.String(8))
    igdh = db.Column(db.String(8))
    igk = db.Column(db.String(8))
    igl = db.Column(db.String(8))
    trbvj = db.Column(db.String(8))
    trbdj = db.Column(db.String(8))
    trg = db.Column(db.String(8))
    trd = db.Column(db.String(8))
    addtime = db.Column(db.DateTime, default=datetime.now)

class addexperimentID(db.Model):
    __tablename__ = 'addexperimentID'
    id = db.Column(db.Integer, primary_key=True)
    experimentIDs = db.Column(db.String(20), index=True)
    addtime = db.Column(db.DateTime, default=datetime.now)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

