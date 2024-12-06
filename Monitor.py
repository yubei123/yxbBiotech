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

if __name__ == '__main__':
    with app.app_context():
        libID = sys.argv[1]
        Monitor = sys.argv[2]
        print(libID, Monitor)
        info = pipelineMonitor.query.filter(pipelineMonitor.libID == libID).first()
        if info:
            info.update(Monitor='已完成')
            #info.update(fqMonitor='已完成')
            #info.update(fqMonitor='出错', remark='报错信息')
            db.session.commit()
        else:
            print(f'{libID} 文库不存在，请核实！')
