from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from glob import glob

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

class pipelineMonitor(db.Model):
    __tablename__ = 'pipelineMonitor'
    id = db.Column(db.Integer, primary_key=True)
    libID = db.Column(db.String(64), unique=True, index=True)
    patientName = db.Column(db.String(10), index=True)
    fqMonitor = db.Column(db.String(20))
    fpMonitor = db.Column(db.String(20))
    pearMonitor = db.Column(db.String(20))
    top15Monitor = db.Column(db.String(20))
    qcMonitor = db.Column(db.String(20))
    reportMonitor = db.Column(db.String(20))
    reportcheckMonitor = db.Column(db.String(20))
    remark = db.Column(db.Text)
    addtime = db.Column(db.DateTime, default=datetime.now)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()