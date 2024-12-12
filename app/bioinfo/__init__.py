from flask import Blueprint, request, jsonify, g
from app.models import SampleInfo, experimenttohos, qctohos, pipelineMonitor, Traceableclones
from app import db
import json
from app.utils import changeUTCtoLocal, addOneday
from flask_jwt_extended import jwt_required
from sqlalchemy import between, or_, and_
from datetime import datetime
from collections import defaultdict
from app.updatedb.qcmodels import IGHqc, IGDHqc, IGKqc, IGLqc, TRBDJqc, TRBVJqc, TRDqc, TRGqc
from app.updatedb.qcmodels import app as qcapp
from app.updatedb.top15models import IGHtop15,IGKtop15,IGLtop15,IGDHtop15,KDEtop15,TRBDJtop15,TRBVJtop15,TRDDJtop15,TRDVJtop15,TRGtop15
from app.updatedb.top15models import app as top15app

qcdb = {'IGH': IGHqc, 'IGDH': IGDHqc, 'IGK': IGKqc, 'IGL': IGLqc, 'TRBDJ': TRBDJqc, 'TRBVJ': TRBVJqc, 'TRD': TRDqc, 'TRG': TRGqc}
top15db = {'IGH':IGHtop15, 'IGDH':IGDHtop15, 'IGK':IGKtop15, 'IGL':IGLtop15, 'IGK+':KDEtop15, \
           'TRBVJ':TRBVJtop15, 'TRBDJ':TRBDJtop15, 'TRD':TRDVJtop15, 'TRD+':TRDDJtop15, 'TRG':TRGtop15}

bioinfo = Blueprint('bioinfo', __name__)

## 检索所有已实验样本分析流程状态
@bioinfo.post('searchlibanalysis')
@jwt_required()
def searchlibanalysis():
    data = request.get_json()
    libinfo = pipelineMonitor.query.order_by(pipelineMonitor.addtime.desc()).paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in libinfo]
    if not a:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in libinfo:
            res.append(i.to_json())
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': libinfo.pages, 'data':res}})

## 检索所有待出具报告样本
@bioinfo.post('getreportsample')
@jwt_required()
def getreportsample():
    data = request.get_json()
    sampleinfo = SampleInfo.query.filter(SampleInfo.sampleStatus != '已出报告').order_by(SampleInfo.addtime.desc()).paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in sampleinfo]
    if not a:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in sampleinfo:
            res.append(i.to_json())
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': sampleinfo.pages, 'data':res}})

## 获取待出具报告样本实验信息等
@bioinfo.post('getreportinfo')
@jwt_required()
def getreportinfo():
    data = request.get_json()
    sampleBarcode = data['sampleBarcode']
    diagnosisPeriod = data['diagnosisPeriod']
    experinfo = experimenttohos.query.filter(and_(experimenttohos.sampleBarcode == sampleBarcode, experimenttohos.diagnosisPeriod == diagnosisPeriod)).all()
    if not experinfo:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        with qcapp.app_context():
            for i in experinfo:
                i = i.to_json()
                qc = qcdb[i['pcrSite']]
                qcinfo = qc.query.filter(and_(qc.sampleBarcode == sampleBarcode, qc.labDate == i['labDate'], qc.barcodeGroup == i['barcodeGroup'])).first()
                i['finalQCres'] = qcinfo.finalQCres
                res.append(i)
        return jsonify({'msg': 'success', 'code': 200, 'data': res})

## 获取文库质控信息
@bioinfo.post('getqcinfo')
@jwt_required()
def getqcinfo():
    data = request.get_json()
    sampleBarcode = data['sampleBarcode']
    labDate = data['labDate']
    barcodeGroup = data['barcodeGroup']
    pcrSite = data['pcrSite']
    with qcapp.app_context():
        qc = qcdb[pcrSite]
        qcinfo = qc.query.filter(and_(qc.sampleBarcode == sampleBarcode, qc.labDate == labDate, qc.barcodeGroup == barcodeGroup)).first()
        if not qcinfo:
            return jsonify({'msg': 'no data', 'code': 204})
        else:
            qcres = []
            qcinfo = qcinfo.to_json()
            print(qcinfo)
            for i in list(qcinfo.keys())[20:-1]:
                if qcinfo[i] == 0:
                    qcres.append({'key': i, 'value': qcinfo[i], 'res':'不合格'})
                else:
                    qcres.append({'key': i, 'value': qcinfo[i], 'res':'合格'})
            a = [
                {'key': 'Total reads', 'value': qcinfo['totalReads'], 'res':qcinfo['totalReadsRes']},\
                {'key': 'Q30', 'value': qcinfo['q30'], 'res':qcinfo['q30Res']},\
                {'key': '拼接率', 'value': qcinfo['assembleRate'], 'res':qcinfo['assembleRateRes']},\
                {'key': '本批次阳性质控结果', 'value': qcinfo['posQC'], 'res':qcinfo['posQCres']},\
                {'key': '本批次阴性质控结果', 'value': qcinfo['negQC'], 'res':qcinfo['negQC']},\
                {'key': '样本间污染', 'value': qcinfo['samplesPollute'], 'res':qcinfo['samplesPollute']},\
                {'key': '引物二聚体', 'value': qcinfo['primerDimers'], 'res':qcinfo['primerDimersRes']},\
                {'key': 'QC质控结果', 'value': qcinfo['qcReads'], 'res':qcinfo['qcRes']},\
            ]
            res = a + qcres + [{'key': '总的质控结果', 'value': qcinfo['finalQCres'], 'res':qcinfo['finalQCres']}]
            return jsonify({'msg': 'success', 'code': 200, 'data': res})

## 获取文库top15结果        
@bioinfo.post('gettop15info')
@jwt_required()
def gettop15info():
    data = request.get_json()
    sampleBarcode = data['sampleBarcode']
    labDate = data['labDate']
    barcodeGroup = data['barcodeGroup']
    pcrSite = data['pcrSite']
    res = []
    with top15app.app_context():
        if pcrSite == 'IGK':
            top15_1 = top15db['IGK']
            top15_2 = top15db['IGK+']
            top15info_1 = top15_1.query.filter(and_(top15_1.sampleBarcode == sampleBarcode, top15_1.labDate == labDate, top15_1.barcodeGroup == barcodeGroup)).all()
            top15info_2 = top15_2.query.filter(and_(top15_2.sampleBarcode == sampleBarcode, top15_2.labDate == labDate, top15_2.barcodeGroup == barcodeGroup)).all()
            if top15info_1:
                for i in top15info_1:
                    i = i.to_json()
                    i['top'] = f'IGK_{i["top"]}'
                    res.append(i)
            if top15info_2:
                for i in top15info_2:
                    i = i.to_json()
                    i['top'] = f'IGK+_{i["top"]}'
                    res.append(i)
        elif pcrSite == 'TRD':
            top15_1 = top15db['TRD']
            top15_2 = top15db['TRD+']
            top15info_1 = top15_1.query.filter(and_(top15_1.sampleBarcode == sampleBarcode, top15_1.labDate == labDate, top15_1.barcodeGroup == barcodeGroup)).all()
            top15info_2 = top15_2.query.filter(and_(top15_2.sampleBarcode == sampleBarcode, top15_2.labDate == labDate, top15_2.barcodeGroup == barcodeGroup)).all()
            if top15info_1:
                for i in top15info_1:
                    i = i.to_json()
                    i['top'] = f'TRD_{i["top"]}'
                    res.append(i)
            if top15info_2:
                for i in top15info_2:
                    i = i.to_json()
                    i['top'] = f'TRD+_{i["top"]}'
                    res.append(i)
        else:
            top15 = top15db[pcrSite]
            top15info = top15.query.filter(and_(top15.sampleBarcode == sampleBarcode, top15.labDate == labDate, top15.barcodeGroup == barcodeGroup)).all()
            if top15info:
                for i in top15info:
                    i = i.to_json()
                    i['top'] = f'{pcrSite}_{i["top"]}'
                    res.append(i)
        # if res == []:
        #     return jsonify({'msg': 'no data', 'code': 204})
        # else:
        return jsonify({'msg': 'success', 'code': 200, 'data': res})

## 生成主克隆信息表格
@bioinfo.post('getmainclones')
@jwt_required()
def getmainclones():
    data = request.json['data']
    with top15app.app_context():
        res = []
        for i in data:
            print(i)
            sampleBarcode = i['sampleBarcode']
            labDate = i['labDate']
            barcodeGroup = i['barcodeGroup']
            pcrSite = i['pcrSite']
            if pcrSite == 'IGK':
                top15_1 = top15db['IGK']
                top15_2 = top15db['IGK+']
                top15info_1 = top15_1.query.filter(and_(top15_1.sampleBarcode == sampleBarcode, top15_1.labDate == labDate, top15_1.barcodeGroup == barcodeGroup, top15_1.markerYN == 'yes')).all()
                top15info_2 = top15_2.query.filter(and_(top15_2.sampleBarcode == sampleBarcode, top15_2.labDate == labDate, top15_2.barcodeGroup == barcodeGroup, top15_2.markerYN == 'yes')).all()
                if top15info_1:
                    for j in top15info_1:
                        j = j.to_json()
                        j['pcrSite'] = 'IGK'
                        j['diagnosisPeriod'] = i['diagnosisPeriod']
                        res.append(j)
                if top15info_2:
                    for j in top15info_2:
                        j = j.to_json()
                        j['pcrSite'] = 'IGK+'
                        j['diagnosisPeriod'] = i['diagnosisPeriod']
                        res.append(j)
            elif pcrSite == 'TRD':
                top15_1 = top15db['TRD']
                top15_2 = top15db['TRD+']
                top15info_1 = top15_1.query.filter(and_(top15_1.sampleBarcode == sampleBarcode, top15_1.labDate == labDate, top15_1.barcodeGroup == barcodeGroup, top15_1.markerYN == 'yes')).all()
                top15info_2 = top15_2.query.filter(and_(top15_2.sampleBarcode == sampleBarcode, top15_2.labDate == labDate, top15_2.barcodeGroup == barcodeGroup, top15_2.markerYN == 'yes')).all()
                if top15info_1:
                    for j in top15info_1:
                        j = j.to_json()
                        j['pcrSite'] = 'TRD'
                        j['diagnosisPeriod'] = i['diagnosisPeriod']
                        res.append(j)
                if top15info_2:
                    for j in top15info_2:
                        j = j.to_json()
                        j['pcrSite'] = 'TRD+'
                        j['diagnosisPeriod'] = i['diagnosisPeriod']
                        res.append(j)
            else:
                top15 = top15db[pcrSite]
                top15info = top15.query.filter(and_(top15.sampleBarcode == sampleBarcode, top15.labDate == labDate, top15.barcodeGroup == barcodeGroup, top15.markerYN == 'yes')).all()
                if top15info:
                    for j in top15info:
                        j = j.to_json()
                        j['pcrSite'] = pcrSite
                        j['diagnosisPeriod'] = i['diagnosisPeriod']
                        res.append(j)
        if res == []:
            return jsonify({'msg': '没有检测到主克隆！', 'code': 205})
        else:
            return jsonify({'msg': 'success', 'code': 200, 'data': res})
        
### 获取生成报告信息
def getsampleinfo(sampleBarcode,diagnosisPeriod):
    sampleinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod)).first()
    data = {}
    if sampleinfo:
        data = {
                'name':sampleinfo.patientName, 
                'department' : sampleinfo.hosDepartment,
                'project_type' : sampleinfo.projectName,
                'barcodeid' : sampleinfo.sampleBarcode,
                'hospitalid' : sampleinfo.patientNo,
                'sex' : sampleinfo.sexName,
                'sample_type' : sampleinfo.sampleType,
                'age' : sampleinfo.patientAge,
                'doctor' : sampleinfo.doctorName,
                'diagnosis' : sampleinfo.clinicalDiagnosis,
                'submission_time' : datetime.strftime(sampleinfo.sampleCollectionTime, '%Y-%m-%d') if sampleinfo.sampleCollectionTime != None else '',
                }
    return data

## 生成报告
@bioinfo.post('getreport')
@jwt_required()
def getreport():
    print(request.get_json())
    data = request.json['data']
    inputNG = request.json['inputNG']
    sampleBarcode = data[0]['sampleBarcode']
    labDate = data[0]['labDate']
    barcodeGroup = data[0]['barcodeGroup']
    patientID = data[0]['patientID']
    sampleCollectionTime = data[0]['sampleCollectionTime']
    lab, diagnosisTime = data[0]['diagnosisPeriod'].split('_')
    sampledata = getsampleinfo(sampleBarcode,data[0]['diagnosisPeriod'])
    sampledata['input_dna'] = inputNG
    with open("config.json","w", encoding='gbk') as f:
        json.dump(sampledata,f)
    cloneinfo = Traceableclones.query.filter(and_(Traceableclones.sampleBarcode == sampleBarcode, Traceableclones.labDate == labDate)).all()
    if cloneinfo:
        db.session.delete(cloneinfo)
    if diagnosisTime == '0':
        if lab == 'B':
            sitelist = ['IGH', 'IGDH', 'IGK', 'IGK+', 'IGL']
        else:
            sitelist = ['TRBVJ', 'TRBDJ', 'TRD', 'TRD+', 'TRG']
        n = 1
        outdata = []
        for s in sitelist:
            for i in data:
                if i['pcrSite'] == s:
                    top15 = top15db[s]
                    if s == 'IGDH':
                        s = 'IGH+'
                    elif s == 'TRBVJ':
                        s = 'TRB'
                    elif s == 'TRBDJ':
                        s = 'TRB+'
                    i['cloneIndex'] = f'{s}-SEQ{n}'
                    n += 1
                    with top15app.app_context():
                        top15info = top15.query.filter(and_(top15.sampleBarcode == sampleBarcode, top15.labDate == labDate, top15.barcodeGroup == barcodeGroup)).all()
                        if top15info:
                            for j in top15info:
                                if j.top == 'top11':
                                    break
                                if j.markerSeq == i['markerSeq']:
                                    SEQ_number = i['cloneIndex'] 
                                else:
                                    SEQ_number = '-'
                                outdata.append({'collection_data':sampleCollectionTime.split(' ')[0],
                                                'SEQ_number': SEQ_number,'locus': s,'CDR3': j.markerSeq,'freq':j.cloneFreq,
                                                'Vgene':j.vGene,'Jgene':j.jGene,'Total_nucleated_cells/%':j.adjustedCellRatio,
                                                })
                        clones = {
                            'sampleBarcode' : sampleBarcode,
                            'labDate' : labDate,
                            'patientID' : patientID,
                            'sampleCollectionTime' : sampleCollectionTime.split(' ')[0],
                            'cloneIndex' : i['cloneIndex'],'pcrSite' : i['pcrSite'],'markerSeq' : i['markerSeq'],
                            'markerReads' : i['markerReads'],'cloneFreq' : i['cloneFreq'],'vGene' : i['vGene'],'jGene' : i['jGene'],
                            'adjustedCellRatio' : i['adjustedCellRatio'],
                        }
                        cloneinfo = Traceableclones(**clones)
                        db.session.add(cloneinfo)
            with open("test.json","w") as f:
                json.dump(outdata,f)
    else:
        MRD_clones = {}
        cloneinfo = Traceableclones.query.filter(and_(Traceableclones.patientID == patientID, Traceableclones.sampleCollectionTime != sampleCollectionTime)).order_by(Traceableclones.sampleCollectionTime.desc()).all()
        if cloneinfo:
            for i in cloneinfo:
                if i.markerSeq not in MRD_clones:
                    MRD_clones[i.markerSeq] = i.cloneFreq
                else:
                    MRD_clones[i.markerSeq] += i.cloneFreq
            for i in MRD_clones:
                outdata.append({'CDR3': i,'freq':MRD_clones[i]})
        for i in data:
            cloneinfo = Traceableclones(**i)
            db.session.add(cloneinfo)
    db.session.commit()
    return jsonify({'msg': 'success', 'code': 200})                                                       
        