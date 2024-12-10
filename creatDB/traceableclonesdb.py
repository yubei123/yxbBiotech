from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

class Traceableclones(db.Model):
    __tablename__ = 'Traceableclones'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    labDate = db.Column(db.String(8), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    cloneIndex = db.Column(db.String(15))
    pcrSite = db.Column(db.String(10))
    markerSeq = db.Column(db.String(100))
    markerReads = db.Column(db.Integer)
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    addtime = db.Column(db.DateTime, default=datetime.now)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()


