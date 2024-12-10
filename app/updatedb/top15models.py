from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

def serialize(self):
    json = {}
    for i in self.__table__.c:
        key = str(i.key)
        json[key] = getattr(self, key)
    return json

class IGHtop15(db.Model):
    __tablename__ = 'IGHtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class IGDHtop15(db.Model):
    __tablename__ = 'IGDHtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class IGKtop15(db.Model):
    __tablename__ = 'IGKtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class KDEtop15(db.Model):
    __tablename__ = 'KDEtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)


class IGLtop15(db.Model):
    __tablename__ = 'IGLtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class TRBVJtop15(db.Model):
    __tablename__ = 'TRBVJtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class TRBDJtop15(db.Model):
    __tablename__ = 'TRBDJtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class TRDVJtop15(db.Model):
    __tablename__ = 'TRDVJtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class TRDDJtop15(db.Model):
    __tablename__ = 'TRDDJtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

class TRGtop15(db.Model):
    __tablename__ = 'TRGtop15'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    patientID = db.Column(db.String(20), index=True)
    sampleCollectionTime = db.Column(db.DateTime)
    labDate = db.Column(db.String(8), index=True)
    barcodeGroup = db.Column(db.String(10))
    top = db.Column(db.String(10))
    markerReads = db.Column(db.Integer)
    cloneFreq = db.Column(db.Float)
    cellRatio = db.Column(db.Float)
    ampFactor = db.Column(db.Float)
    markerCellsByN = db.Column(db.Float)
    markerSeq = db.Column(db.String(100))
    vGene = db.Column(db.String(100))
    jGene = db.Column(db.String(100))
    adjustedCellRatio = db.Column(db.Float)
    markerYN = db.Column(db.String(10))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)
    
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

    def to_json(self):
        return serialize(self)
