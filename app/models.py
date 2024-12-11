from app import db, jwt
from datetime import timedelta, datetime
from flask_jwt_extended import create_access_token
from functools import wraps
from flask import g

def serialize(self):
    json = {}
    for i in self.__table__.c:
        key = str(i.key)
        json[key] = getattr(self, key)
    return json

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
    
class extractANDpurify(db.Model):
    __tablename__ = 'extractANDpurify'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    projectBarcode = db.Column(db.String(20), index=True)
    projectName = db.Column(db.String(50), index=True)
    projectType = db.Column(db.String(20), index=True)
    patientName = db.Column(db.String(10), index=True)
    patientID = db.Column(db.String(20), index=True)
    diagnosisPeriod = db.Column(db.String(20), index=True)
    sampleType = db.Column(db.String(20), index=True)
    sampleSentNum = db.Column(db.String(20), index=True)
    bloodVolume = db.Column(db.String(20))
    bloodUsed = db.Column(db.String(20))
    extractDNAVolume = db.Column(db.String(20))
    originalTubeConcentration = db.Column(db.String(64))
    extractTubes = db.Column(db.String(10))
    purifyQubitConcentration = db.Column(db.String(20))
    purifyDNAVolume = db.Column(db.String(20))
    purifyOperator = db.Column(db.String(10))
    purifyDate = db.Column(db.DateTime)
    purifyStatus = db.Column(db.String(20), index=True)
    remark = db.Column(db.String(100))
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)
    
class delSampleInfo(db.Model):
    __tablename__ = 'delsampleinfo'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    projectBarcode = db.Column(db.String(20), index=True)
    projectName = db.Column(db.String(50), index=True)
    patientName = db.Column(db.String(10), index=True)
    patientID = db.Column(db.String(20), index=True)
    hospitalName = db.Column(db.String(50), index=True)
    sexName = db.Column(db.String(2))
    patientAge = db.Column(db.String(5))
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
    delOperator = db.Column(db.String(20), index=True)
    addtime = db.Column(db.DateTime, default=datetime.now)
    
    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)

class delextractANDpurify(db.Model):
    __tablename__ = 'delextractANDpurify'
    id = db.Column(db.Integer, primary_key=True)
    sampleBarcode = db.Column(db.String(50), index=True)
    projectBarcode = db.Column(db.String(20), index=True)
    projectName = db.Column(db.String(50), index=True)
    projectType = db.Column(db.String(20), index=True)
    patientName = db.Column(db.String(10), index=True)
    patientID = db.Column(db.String(20), index=True)
    diagnosisPeriod = db.Column(db.String(20), index=True)
    sampleType = db.Column(db.String(20), index=True)
    sampleSentNum = db.Column(db.String(20), index=True)
    bloodVolume = db.Column(db.String(20))
    bloodUsed = db.Column(db.String(20))
    extractDNAVolume = db.Column(db.String(20))
    originalTubeConcentration = db.Column(db.String(64))
    extractTubes = db.Column(db.String(10))
    purifyQubitConcentration = db.Column(db.String(20))
    purifyDNAVolume = db.Column(db.String(20))
    purifyOperator = db.Column(db.String(10))
    purifyDate = db.Column(db.DateTime)
    purifyStatus = db.Column(db.String(20), index=True)
    remark = db.Column(db.String(100))
    delOperator = db.Column(db.String(20), index=True)
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)

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

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_json(self):
        return serialize(self)

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

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)
    
class addPatientID(db.Model):
    __tablename__ = 'addPatientID'
    id = db.Column(db.Integer, primary_key=True)
    patientIDs = db.Column(db.String(20), index=True)
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)
    
class addexperimentID(db.Model):
    __tablename__ = 'addexperimentID'
    id = db.Column(db.Integer, primary_key=True)
    experimentIDs = db.Column(db.String(20), index=True)
    addtime = db.Column(db.DateTime, default=datetime.now)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)
    
class pendingSample(db.Model):
    __tablename__ = 'pendingsample'
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
    
    def to_json(self):
        return serialize(self)
    
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

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def to_json(self):
        return serialize(self)