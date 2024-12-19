from flask import Blueprint, request, jsonify, g, send_from_directory, make_response
from app.models import SampleInfo, experimenttohos, pipelineMonitor, Traceableclones, pipelineMonitor, testandcheck
from app import db
import json, os, glob
import subprocess
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
    sampleinfo = SampleInfo.query.filter(SampleInfo.sampleStatus != '已退项').order_by(SampleInfo.addtime.desc()).paginate(page=data['pagenum'], per_page=data['pagesize'])
    a = [i.to_json() for i in sampleinfo]
    if not a:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in sampleinfo:
            i = i.to_json()
            experinfo = experimenttohos.query.filter(and_(experimenttohos.sampleBarcode == i['sampleBarcode'], experimenttohos.diagnosisPeriod == i['diagnosisPeriod'])).first()
            if experinfo:
                i['labDate'] = experinfo.labDate if experinfo.labDate != None else ''
            else:
                i['labDate'] = ''
            res.append(i)
    return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': sampleinfo.pages, 'data':res}})

## 获取之前的报告
def getbeforereport(sampleBarcode,diagnosisPeriod):
    sampleinfo = SampleInfo.query.filter(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod).first()
    if sampleinfo:
        patientID = sampleinfo.patientID
        sampleCollectionTime = sampleinfo.sampleCollectionTime
        beforesample = SampleInfo.query.filter(SampleInfo.patientID == patientID, SampleInfo.sampleCollectionTime < sampleCollectionTime).order_by(SampleInfo.sampleCollectionTime.desc()).all()
        if beforesample:
            for i in beforesample:
                experinfo = experimenttohos.query.filter(experimenttohos.sampleBarcode == i.sampleBarcode, experimenttohos.diagnosisPeriod == i.diagnosisPeriod).first()
                res = []
                if experinfo:
                    CollectionTime = datetime.strftime(i.sampleCollectionTime, '%Y-%m-%d')
                    res.append({'sampleCollectionTime':CollectionTime, 'report': f'/data/yubei/Biotech/report/{experinfo.labDate}/{patientID}+{i.patientName}+{i.sampleBarcode}+{i.diagnosisPeriod}+{CollectionTime}.report.pdf'})
            return res
        else:
            return []

def getcurrentreport(sampleBarcode,diagnosisPeriod):
    sampleinfo = SampleInfo.query.filter(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod).first()
    if sampleinfo:
        patientID = sampleinfo.patientID
        CollectionTime = datetime.strftime(sampleinfo.sampleCollectionTime, '%Y-%m-%d')
        experinfo = experimenttohos.query.filter(experimenttohos.sampleBarcode == sampleBarcode, experimenttohos.diagnosisPeriod == diagnosisPeriod).first()
        if experinfo:
            res = [{'sampleCollectionTime':CollectionTime, 'report': f'/data/yubei/Biotech/report/{experinfo.labDate}/{patientID}+{sampleinfo.patientName}+{sampleBarcode}+{diagnosisPeriod}+{CollectionTime}.report.pdf'}]
            return res
        else:
            return []

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
        return jsonify({'msg': 'success', 'code': 200, 'data':res, 'report': {'currentreport': getcurrentreport(sampleBarcode,diagnosisPeriod), 'beforereport': getbeforereport(sampleBarcode,diagnosisPeriod)}})

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
            for i in list(qcinfo.keys())[20:-1]:
                qcres.append({'key': i, 'value': qcinfo[i], 'res':''})
            a = [
                {'key': 'Total reads', 'value': qcinfo['totalReads'], 'res':qcinfo['totalReadsRes']},\
                {'key': 'Q30', 'value': qcinfo['q30'], 'res':qcinfo['q30Res']},\
                {'key': '拼接率', 'value': qcinfo['assembleRate'], 'res':qcinfo['assembleRateRes']},\
                {'key': '本批次阳性质控结果', 'value': qcinfo['posQC'], 'res':qcinfo['posQCres']},\
                {'key': '本批次阴性质控结果', 'value': '', 'res':qcinfo['negQC']},\
                {'key': '样本间污染', 'value': '', 'res':qcinfo['samplesPollute']},\
                {'key': '引物二聚体', 'value': qcinfo['primerDimers'], 'res':qcinfo['primerDimersRes']},\
                {'key': 'QC质控结果', 'value': qcinfo['qcReads'], 'res':qcinfo['qcRes']},\
            ]
            res = a + qcres + [{'key': '总的质控结果', 'value': '', 'res':qcinfo['finalQCres']}]
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
        if res == []:
            return jsonify({'msg': 'no data', 'code': 204})
        else:
            return jsonify({'msg': 'success', 'code': 200, 'data': res})

## 生成主克隆信息表格
@bioinfo.post('getmainclones')
@jwt_required()
def getmainclones():
    data = request.json['data']
    site = {'TRBVJ':'TRB', 'TRBDJ':'TRB+', 'IGH':'IGH', 'IGDH':'IGDH', 'IGL':'IGL', 'TRG':'TRG'}
    tester = testandcheck.query.all()
    tester = [i.Name for i in tester]
    with top15app.app_context():
        res = []
        for i in data:
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
                        j['pcrSite'] = site[pcrSite]
                        j['diagnosisPeriod'] = i['diagnosisPeriod']
                        res.append(j)
        if res == []:
            return jsonify({'msg': '没有检测到主克隆！', 'code': 205})
        else:
            return jsonify({'msg': 'success', 'code': 200, 'data': res, 'tester':tester})
        
## 查看主克隆信息表格
@bioinfo.post('searchmainclones')
@jwt_required()
def searchmainclones():
    data = request.json['data']
    res = []
    sampleBarcode = data[0]['sampleBarcode']
    labDate = data[0]['labDate']
    patientID = data[0]['patientID']
    cloneinfo = Traceableclones.query.filter(and_(Traceableclones.sampleBarcode == sampleBarcode, Traceableclones.labDate == labDate, Traceableclones.patientID == patientID)).all()
    if cloneinfo:
        for i in cloneinfo:
            i = i.to_json()
            res.append(i)
        return jsonify({'msg': 'success', 'code': 200, 'data': res})
    else:
        return jsonify({'msg': '没有主克隆信息！', 'code': 204})
        
### 获取生成报告信息
def getsampleinfo(sampleBarcode,diagnosisPeriod,tester,reviewer):
    sampleinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod)).first()
    data = {}
    test = testandcheck.query.filter(testandcheck.Name == tester).first().pngPath
    review = testandcheck.query.filter(testandcheck.Name == reviewer).first().pngPath
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
                'jyz_name_png': f'images/{test}.png',
                'shz_name_png': f'images/{review}.png',
                'chapters_png': 'images/hst.png'
                }
    return data

## 生成报告
@bioinfo.post('getreport')
@jwt_required()
def getreport():
    site = {'IGH':'IGH','IGDH':'IGDH','IGK':'IGK', 'IGK+':'IGK+','IGL':'IGL','TRBVJ':'TRB', 'TRBDJ':'TRB+','TRD':'TRD','TRD+':'TRD+','TRG':'TRG'}
    data = request.json['data']
    try:
        inputNG = request.json['inputNG']
        tester = request.json['tester']
        reviewer = request.json['reviewer']
        sampleBarcode = data[0]['sampleBarcode']
        labDate = data[0]['labDate']
        barcodeGroup = data[0]['barcodeGroup']
        patientID = data[0]['patientID']
        sampleCollectionTime = data[0]['sampleCollectionTime']
        diagnosisPeriod = data[0]['diagnosisPeriod']
        lab, diagnosisTime = diagnosisPeriod.split('_')
        libID = f'{labDate}-{sampleBarcode}-{barcodeGroup}-{diagnosisPeriod}'
        sampledata = getsampleinfo(sampleBarcode,diagnosisPeriod,tester,reviewer)
        sampledata['input_dna'] = inputNG
        patientName = sampledata['name']

        out_dir = f'/data/yubei/Biotech/report/{labDate}'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        cofing_json = f'{out_dir}/{patientID}+{patientName}+{sampleBarcode}+{diagnosisPeriod}+{sampleCollectionTime.split(" ")[0]}.config.json'
        out_json = f'{out_dir}/{patientID}+{patientName}+{sampleBarcode}+{diagnosisPeriod}+{sampleCollectionTime.split(" ")[0]}.report.json'
        with open(cofing_json,"w") as f:
            json.dump(sampledata,f)

        cloneinfo = Traceableclones.query.filter(and_(Traceableclones.sampleBarcode == sampleBarcode, Traceableclones.labDate == labDate, Traceableclones.patientID == patientID)).delete()
        if lab == 'B':
            sitelist = ['IGH', 'IGDH', 'IGK', 'IGK+', 'IGL']
        else:
            sitelist = ['TRBVJ', 'TRBDJ', 'TRD', 'TRD+', 'TRG']
        if diagnosisTime == '0':
            main_clone = {}
            for i in data:
                main_clone[i['markerSeq']] = i['pcrSite']
            n = 1
            outdata = []
            for s in sitelist:
                top15 = top15db[s]
                with top15app.app_context():
                    top15info = top15.query.filter(and_(top15.sampleBarcode == sampleBarcode, top15.labDate == labDate, top15.barcodeGroup == barcodeGroup)).all()
                    if top15info:
                        for j in top15info:
                            if j.top == 'top11':
                                break
                            if j.markerSeq in main_clone.keys():
                                main_clone[j.markerSeq] = f'{site[s]}-SEQ{n}'
                                SEQ_number = f'{site[s]}-SEQ{n}'
                                n += 1
                            else:
                                SEQ_number = '-'
                            outdata.append({'collection_data':sampleCollectionTime.split(' ')[0],
                                            'SEQ_number': SEQ_number,'locus': site[s],'CDR3': j.markerSeq,'freq':j.cloneFreq,
                                            'Vgene':j.vGene,'Jgene':j.jGene,'Total_nucleated_cells':j.adjustedCellRatio,
                                            })
            with open(out_json,"w") as f:
                json.dump(outdata,f)
            sp = subprocess.run(f'/opt/miniconda/envs/myenv_report_lqj/bin/python /data/yubei/Biotech_report/report-1218-v1.pyc \
                                -c {cofing_json} -i {out_json} -o {out_dir}', shell=True, stderr=subprocess.PIPE)
            if sp.returncode == 0:
                subprocess.run(f'rm -rf {cofing_json} {out_json}', shell=True)
                pipeinfo = pipelineMonitor.query.filter(pipelineMonitor.libID.contains(libID)).first()
                sampleinfo = SampleInfo.query.filter(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod).first()
                if pipeinfo:
                    pipeinfo.update(reportMonitor = '已生成', reportcheckMonitor = '未审核')
                if sampleinfo:
                    sampleinfo.update(sampleStatus = '已出报告')
            else:
                print(sp.stderr)
            for i in data:
                clone = {'sampleBarcode' : sampleBarcode,'labDate' : labDate,'patientID' : patientID,'sampleCollectionTime' : sampleCollectionTime.split(' ')[0],
                    'cloneIndex' : main_clone[i['markerSeq']],'pcrSite' : i['pcrSite'], 'markerSeq' : i['markerSeq'],
                    'markerReads' : i['markerReads'],'cloneFreq' : i['cloneFreq'],'vGene' : i['vGene'],'jGene' : i['jGene'],
                    'adjustedCellRatio' : i['adjustedCellRatio']}
                clones = Traceableclones(**clone)
                db.session.add(clones)
        else:
            MRD_clones = {}
            XF_clones = {}
            outdata = []
            cloneinfo = Traceableclones.query.filter(and_(Traceableclones.patientID == patientID, Traceableclones.sampleCollectionTime < sampleCollectionTime)).order_by(Traceableclones.sampleCollectionTime).all()
            if cloneinfo:
                for i in cloneinfo:
                    MRD_clones[i.markerSeq] = i.cloneIndex
                    if i.markerSeq.startswith('XF'):
                        XF_clones[i.markerSeq] = i.cloneIndex
                    outdata.append({'collection_data':datetime.strftime(i.sampleCollectionTime, '%Y-%m-%d'),
                                    'SEQ_number': i.cloneIndex,'locus': i.pcrSite,'CDR3': i.markerSeq,'freq':i.cloneFreq,
                                    'Vgene':i.vGene,'Jgene':i.jGene,'Total_nucleated_cells':i.adjustedCellRatio,
                                    })
            if XF_clones == {}:
                n = 1
            else:
                max_n = sorted([i.split('-')[-1] for i in XF_clones.values()], reverse=True)
                n = int(max_n[0][3:])+1
            for i in data:
                for s in sitelist: 
                    if i['pcrSite'] == s:
                        if i['markerSeq'] in MRD_clones:
                            cloneIndex = MRD_clones[i['markerSeq']]
                        elif i['markerSeq'] in XF_clones:
                            cloneIndex = XF_clones[i['markerSeq']]
                        else:
                            cloneIndex = f'XF-{site[s]}-SEQ{n}'
                            n += 1
                        outdata.append({'collection_data':sampleCollectionTime.split(' ')[0],
                                        'SEQ_number': cloneIndex,'locus': i['pcrSite'],'CDR3': i['markerSeq'],'freq':i['cloneFreq'],
                                        'Vgene':i['vGene'],'Jgene':i['jGene'],'Total_nucleated_cells':i['adjustedCellRatio'],
                                        })
                        clone = {'sampleBarcode' : sampleBarcode,'labDate' : labDate,'patientID' : patientID,'sampleCollectionTime' : sampleCollectionTime.split(' ')[0],
                            'cloneIndex' : cloneIndex, 'pcrSite' : i['pcrSite'], 'markerSeq' : i['markerSeq'],
                            'markerReads' : i['markerReads'],'cloneFreq' : i['cloneFreq'],'vGene' : i['vGene'],'jGene' : i['jGene'],
                            'adjustedCellRatio' : i['adjustedCellRatio']}
                        clones = Traceableclones(**clone)
                        db.session.add(clones)
            with open(out_json,"w") as f:
                json.dump(outdata,f)
            sp = subprocess.run(f'/opt/miniconda/envs/myenv_report_lqj/bin/python /data/0_html_report/0_Report_scripts/report-1213-v1.pyc \
                                -c {cofing_json} -i {out_json} -o {out_dir}', shell=True, stderr=subprocess.PIPE)
            if sp.returncode == 0:
                pipeinfo = pipelineMonitor.query.filter(pipelineMonitor.libID.contains(libID)).first()
                sampleinfo = SampleInfo.query.filter(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == data[0]['diagnosisPeriod']).first()
                if pipeinfo:
                    pipeinfo.update(reportMonitor = '已生成', reportcheckMonitor = '未审核')
                if sampleinfo:
                    sampleinfo.update(reportMonitor = '已出报告')
            else:
                print(sp.stderr)
        db.session.commit()
        return jsonify({'msg': 'success', 'code': 200})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg': 'error', 'code': 500})

## 查看报告
@bioinfo.post('reviewreport')
@jwt_required()
def reviewreport():
    data = request.get_json()
    reportdir = data['pdf']
    if os.path.exists(reportdir):
        dirname = '/'.join(reportdir.split('/')[:-1])
        basename = reportdir.split('/')[-1]
        response = make_response(send_from_directory(dirname, basename, as_attachment=True))
        return response
    else:
        return jsonify({'msg': 'error', 'code': 500})
    
## 下载报告
@bioinfo.post('downloadreport')
@jwt_required()
def downloadreport():
    data = request.json['data']
    labDate = data['labDate']
    patientID = data['patientID']
    patientName = data['patientName']
    sampleBarcode = data['sampleBarcode']
    diagnosisPeriod = data['diagnosisPeriod']
    sampleCollectionTime = data['sampleCollectionTime']
    reportdir = f'/data/yubei/Biotech/report/{labDate}/{patientID}+{patientName}+{sampleBarcode}+{diagnosisPeriod}+{sampleCollectionTime.split(" ")[0]}.report.pdf'
    if os.path.exists(reportdir):
        dirname = '/'.join(reportdir.split('/')[:-1])
        basename = reportdir.split('/')[-1]
        response = make_response(send_from_directory(dirname, basename, as_attachment=True))
        return response
    else:
        return jsonify({'msg': 'error', 'code': 500})

## 报告审核
@bioinfo.post('reportcheck')
@jwt_required()
def reportcheck():
    data = request.json['data']
    try:
        labDate = data['labDate']
        labSite = data['labSite']
        labUser = data['labUser']
        barcodeGroup = data['barcodeGroup']
        sampleBarcode = data['sampleBarcode']
        diagnosisPeriod = data['diagnosisPeriod']
        libID = f'{labDate}-{sampleBarcode}-{barcodeGroup}-{diagnosisPeriod}-{labSite}-{labUser}'
        sampleinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode == sampleBarcode, SampleInfo.diagnosisPeriod == diagnosisPeriod)).first()
        pipeinfo = pipelineMonitor.query.filter(pipelineMonitor.libID == libID).first()
        if sampleinfo:
            sampleinfo.update(sampleStatus = '已审核')
        if pipeinfo:
            pipeinfo.update(reportcheckMonitor = '已审核')
        db.session.commit()
        return jsonify({'msg': 'success', 'code': 200})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg': 'error', 'code': 500})