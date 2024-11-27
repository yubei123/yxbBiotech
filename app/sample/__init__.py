from flask import Blueprint, request, jsonify, g
from app.models import SampleInfo, delSampleInfo, addPatientID, experimenttohos,addexperimentID, pendingSample
from app import db
from flask_jwt_extended import jwt_required
from datetime import datetime
from sqlalchemy import between, and_, or_
import requests
from app.utils import changeUTCtoLocal, addOneday
from collections import defaultdict

sample = Blueprint('sample', __name__)

projectName2Barcode = {'BCR克隆鉴定': 'KSB001', 'TCR克隆鉴定': 'KSB002', 'BCR MRD监测': 'KSB003', 'TCR MRD监测': 'KSB004'}

### 样本信息上传及更新api
@sample.post('/uploadsampleinfo')
@jwt_required()
def uploadsampleinfo():
    data = request.json['data']
    tag = request.json['tag']
    print(data)
    try:
        if tag == 'edit':
            i = data[0]
            i['sampleCollectionTime'] = changeUTCtoLocal(i['sampleCollectionTime']) if i['sampleCollectionTime'] != '' else None
            i['sampleReceiveTime'] = changeUTCtoLocal(i['sampleReceiveTime']) if i['sampleReceiveTime'] != '' else None
            sampleinfo = i
            pendinginfo = pendingSample.query.filter(pendingSample.sampleBarcode==i['sampleBarcode']).first()
            if pendinginfo:
                if i['projectName'] == ['待定']:
                    pendinginfo.update(**i)
                else:
                    for pb in i['projectName']:
                        if pb == '待定':
                            continue
                        sampleinfo['projectName'] = pb
                        sampleinfo['projectBarcode'] = projectName2Barcode[pb]
                        info = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==i['sampleBarcode'], SampleInfo.projectName==pb)).first()
                        if info:
                            info.update(**i)
                        else:
                            sample = SampleInfo(**i)
                            db.session.add(sample)
                    db.session.delete(pendinginfo)
            else:
                info = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==i['sampleBarcode'], SampleInfo.projectName==i['projectName'])).first()
                if info:
                    info.update(**i)
        else:
            for i in data:
                i['sampleCollectionTime'] = changeUTCtoLocal(i['sampleCollectionTime']) if i['sampleCollectionTime'] != '' else None
                i['sampleReceiveTime'] = changeUTCtoLocal(i['sampleReceiveTime']) if i['sampleReceiveTime'] != '' else None
                sampleinfo = i
                if i['projectName'] == ['待定']:
                    sampleinfo['projectName'] = '待定'
                    sampleinfo['projectBarcode'] = '待定'
                    sampleinfo['sampleStatus'] = '已收样'
                    info = pendingSample.query.filter(and_(pendingSample.sampleBarcode==i['sampleBarcode'], pendingSample.projectName==i['projectName'])).first()
                    if info:
                        info.update(**i)
                    else:
                        sample = pendingSample(**i)
                        db.session.add(sample)
                else:
                    for pb in i['projectName']:
                        info = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==i['sampleBarcode'], SampleInfo.projectName==pb)).first()
                        sampleinfo['projectName'] = pb
                        sampleinfo['projectBarcode'] = projectName2Barcode[pb]
                        if info:
                            info.update(**i)
                        else:
                            sample = SampleInfo(**i)
                            db.session.add(sample)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg':'fail!', 'code':500})
    return jsonify({'msg':'success!', 'code':200})

### lis系统获取样本信息api
@sample.post('/getsampleinfo')
@jwt_required()
def getsampleinfo():
    dup_barcode = []
    for i in request.json['data']:
        sampleBarcode = i['sampleBarcode']
        projectBarcode = i['projectBarcode']
        patientID = i['patientID']
        diagnosisPeriod = i['diagnosisPeriod']
        re = requests.post(f'https://tempest.kindstar.com.cn/aspid/login', json={"userName": "KSBT001","password": "1!2@3#4$fgh"}).json()
        token = re['tokenResponse']['access_token']
        headers = {}
        headers["Authorization"] = f"Bearer {token}"
        r = requests.get(f'https://itdevelop.kindstar.com.cn/api/external-common/api/SampleInfo/GetSampleByBacodeAndApplyItemCode?barcode={sampleBarcode}&applyitmeCode={projectBarcode}&affiliatedGroup=9030', headers=headers).json()
        if r['code'] == 'fail':
            data = i
        else:
            sampledata = r['data']
            data = {
                'sampleBarcode':sampleBarcode,
                'projectBarcode':projectBarcode,
                'projectName':sampledata['applyItemName'] if sampledata['applyItemName'] else '-',
                'patientName':sampledata['patientName'],
                'patientID':patientID,
                'hospitalName':sampledata['hospitalName'] if sampledata['hospitalName'] else '-',
                'sexName':sampledata['sexName'] if sampledata['sexName'] else '-',
                'patientAge':sampledata['patientAgeDisplay'] if sampledata['patientAgeDisplay'] else '-',
                'patientCardNo':sampledata['patientCardNo'] if sampledata['patientCardNo'] else '-',
                'patientPhone':sampledata['patientPhone'] if sampledata['patientPhone'] else '-',
                'sampleType':sampledata['sampleTypeName'] if sampledata['sampleTypeName'] else '-',
                'hosDepartment':sampledata['hosDepartment'] if sampledata['hosDepartment'] else '-',
                'patientNo':sampledata['patientNo'] if sampledata['patientNo'] else '-',
                'bedNo':sampledata['bedNo'] if sampledata['bedNo'] else '-',
                'doctorName':sampledata['doctorName'] if sampledata['doctorName'] else '-',
                'clinicalDiagnosis':sampledata['clinicalDiagnosis'] if sampledata['clinicalDiagnosis'] else '-',
                'sampleCollectionTime':sampledata['sampleCollectionTime'] if sampledata['sampleCollectionTime'] else None,
                'sampleReceiveTime':sampledata['createDate'] if sampledata['createDate'] else None,
                'diagnosisPeriod':diagnosisPeriod,
                'projectType':'临床项目',
                'reportTime':None,
                'sampleStatus':'已收样',
                }
        info = SampleInfo.query.filter_by(sampleBarcode=sampleBarcode).first()
        if not info:
            sampleinfo = SampleInfo(**data)
            db.session.add(sampleinfo)
        else:
            dup_barcode.append(info.sampleBarcode)
    db.session.commit()
    if dup_barcode != []:
        return jsonify({'msg': f'以下样本条码重复，请检查：{dup_barcode}', 'code': 222})
    return jsonify({'msg': 'success', 'code': 200})

### 样本信息查询api
@sample.post('/searchsampleinfo')
@jwt_required()
def searchsampleinfo():
    data = request.get_json()
    n = 0
    query = SampleInfo.query
    if data['sampleBarcode'] != '':
        query = query.filter(SampleInfo.sampleBarcode == data['sampleBarcode'])
        n += 1
    if data['projectBarcode'] != '':
        query = query.filter(SampleInfo.projectBarcode == data['projectBarcode'])
        n += 1
    if data['projectName'] != '':
        query = query.filter(SampleInfo.projectName.contains(data['projectName']))
        n += 1
    if data['patientName'] != '':
        query = query.filter(SampleInfo.patientName.contains(data['patientName']))
        n += 1
    if data['patientID'] != '':
        query = query.filter(SampleInfo.patientID == data['patientID'])
        n += 1
    if data['hospitalName'] != '':
        query = query.filter(SampleInfo.hospitalName.contains(data['hospitalName']))
        n += 1
    if data['sampleType'] != '':
        query = query.filter(SampleInfo.sampleType.contains(data['sampleType']))
        n += 1
    if data['diagnosisPeriod'] != '':
        query = query.filter(SampleInfo.diagnosisPeriod.contains(data['diagnosisPeriod']))
        n += 1
    if data['projectType'] != '':
        query = query.filter(SampleInfo.projectType.contains(data['projectType']))
        n += 1
    if data['sampleStatus'] != '':
        query = query.filter(SampleInfo.sampleStatus.contains(data['sampleStatus']))
        n += 1
    if data['sampleCollectionTime'] != '':
        stime = changeUTCtoLocal(data["sampleCollectionTime"])
        etime = addOneday(data["sampleCollectionTime"])
        query = query.filter(between(SampleInfo.sampleCollectionTime, stime, etime))
        n += 1
    if data['addtime'] != '':
        stime = changeUTCtoLocal(data["addtime"])
        etime = addOneday(data["addtime"])
        query = query.filter(between(SampleInfo.addtime, stime, etime))
        n += 1
    info = query.order_by(SampleInfo.addtime.desc()).paginate(page=data['pagenum'], per_page=10)
    a = [i.to_json() for i in info]
    if not a or n == 0:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in info:
            res.append(i.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data': {'pages': info.pages, 'data':res}})

@sample.post('/searchnameorbarcode')
@jwt_required()
def searchnameorbarcode():
    data = request.get_json()
    projectName = data['projectName']
    if 'sampleBarcode' in data.keys():
        info = SampleInfo.query.filter(SampleInfo.sampleBarcode == data['sampleBarcode']).all()
    elif 'patientName' in data.keys():
        info = SampleInfo.query.filter(and_(SampleInfo.patientName == data['patientName'], SampleInfo.projectName.contains(projectName[0:3]), SampleInfo.sampleStatus != '已退项')).all()
    if not info:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        res = []
        for i in info:
            res.append(i.to_json())
        return jsonify({'msg': 'success', 'code': 200, 'data':res})

### 样本信息删除api
@sample.post('/deletesampleinfo')
@jwt_required()
def deletesampleinfo():
    sampleBarcode = request.json['sampleBarcode']
    projectName = request.json['projectName']
    try:
        info = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==sampleBarcode, SampleInfo.projectName==projectName)).first()
        delinfo = info.to_json()
        delinfo['delOperator'] = g.username
        del delinfo['id']
        del delinfo['addtime']
        delinfo['sampleStatus'] = '已退项'
        delsample = delSampleInfo(**delinfo)
        db.session.add(delsample)
        db.session.delete(info)
        db.session.commit()
        return jsonify({'msg': 'success', 'code': 200})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg':'fail!', 'code':500})

### 生成样本唯一性ID
@sample.post('/generatePatientID')
@jwt_required()
def generatePatientID():
    project2site = {'KSB001':'B', 'KSB002':'T', 'KSB003':'B', 'KSB004':'T'}
    Period2inputDNA = {'time0':100, 'MRD':''}
    today = datetime.now().strftime('%Y%m%d')
    data = request.get_json()
    currentBarcode, currentproject = data['currentBarcode'].split('+')
    selectBarcode, selectproject = data['selectBarcode'].split('+')
    dupSite = data['dupSite']
    try:
        l_sinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==selectBarcode, SampleInfo.projectName==selectproject)).first()
        c_sinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==currentBarcode, SampleInfo.projectName==currentproject)).first()
        projectBarcode = c_sinfo.projectBarcode
        experID = addexperimentID.query.all()
        experID_num = 0
        if not experID:
            experID_num = 1
        else:
            experIDs = experID[-1].experimentIDs
            if today in experIDs:
                experID_num = int(experIDs[-4:]) + 1
            else:
                experID_num = 1
        diagnosisPeriod_list = defaultdict(lambda: defaultdict(str))
        if currentBarcode == selectBarcode:
            IDinfo = addPatientID.query.all()
            if not IDinfo:
                PatientIDs = 'lym000001'
            else:
                PatientIDs = IDinfo[-1].patientIDs
                PatientIDs = str(int(PatientIDs[3:]) + 1).zfill(6)
                PatientIDs = 'lym' + PatientIDs
            PatientID = PatientIDs + '_0'
            diagnosisPeriods = f'{project2site[projectBarcode]}_0'
            diagnosisPeriod_list['time0'][project2site[projectBarcode]] = diagnosisPeriods
            db.session.add(addPatientID(patientIDs=PatientIDs))
        else:
            if c_sinfo.projectBarcode == 'KSB001' or c_sinfo.projectBarcode == 'KSB002':
                PatientIDs,num = l_sinfo.patientID.split('_')
                PatientID = f'{PatientIDs}_{int(num) + 1}'
                diagnosisPeriods = f'{project2site[projectBarcode]}_0'
                diagnosisPeriod_list['time0'][project2site[projectBarcode]] = diagnosisPeriods
            else:
                pnum = l_sinfo.diagnosisPeriod.split('_')[1]
                PatientID = l_sinfo.patientID
                diagnosisPeriods = f'{project2site[projectBarcode]}_{int(pnum) + 1}'
                diagnosisPeriod_list['MRD'][project2site[projectBarcode]] = diagnosisPeriods
        c_sinfo.update(patientID=PatientID, diagnosisPeriod=diagnosisPeriods)
        for i in diagnosisPeriod_list:
            for k,v in diagnosisPeriod_list[i].items():
                if k == 'B':
                    for s in ['IGH','IGDH','IGK','IGL']:
                        experinfo = {'sampleBarcode': currentBarcode, 'patientName':c_sinfo.patientName, 'patientID': PatientID,'experimentID':f'{today}_{str(experID_num).zfill(4)}','diagnosisPeriod':v, 'inputNG':Period2inputDNA[i], 'pcrSite':s}
                        db.session.add(experimenttohos(**experinfo))
                        db.session.add(addexperimentID(**{'experimentIDs':f'{today}_{str(experID_num).zfill(4)}'}))
                        experID_num += 1
                elif k == 'T':
                    for s in ['TRBVJ','TRBDJ','TRD','TRG']:
                        experinfo = {'sampleBarcode': currentBarcode, 'patientName':c_sinfo.patientName, 'patientID': PatientID,'experimentID':f'{today}_{str(experID_num).zfill(4)}','diagnosisPeriod':v, 'inputNG':Period2inputDNA[i], 'pcrSite':s}
                        db.session.add(experimenttohos(**experinfo))
                        db.session.add(addexperimentID(**{'experimentIDs':f'{today}_{str(experID_num).zfill(4)}'}))
                        experID_num += 1
        if dupSite != []:
            for i in dupSite:
                if i in ['IGH','IGDH','IGK','IGL']:
                    experinfo = {'sampleBarcode': currentBarcode, 'patientName':c_sinfo.patientName, 'patientID': PatientID,'experimentID':f'{today}_{str(experID_num).zfill(4)}','diagnosisPeriod':f'B_{diagnosisPeriods.split("_")[1]}', 'pcrSite':i}
                    db.session.add(experimenttohos(**experinfo))
                    db.session.add(addexperimentID(**{'experimentIDs':f'{today}_{str(experID_num).zfill(4)}'}))
                    experID_num += 1
                elif i in ['TRBVJ','TRBDJ','TRD','TRG']:
                    experinfo = {'sampleBarcode': currentBarcode, 'patientName':c_sinfo.patientName, 'patientID': PatientID,'experimentID':f'{today}_{str(experID_num).zfill(4)}','diagnosisPeriod':f'T_{diagnosisPeriods.split("_")[1]}', 'pcrSite':i}
                    db.session.add(experimenttohos(**experinfo))
                    db.session.add(addexperimentID(**{'experimentIDs':f'{today}_{str(experID_num).zfill(4)}'}))
                    experID_num += 1
        db.session.commit()
        c_sinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==currentBarcode, SampleInfo.projectName==currentproject)).first()
        return jsonify({'msg': 'success', 'code': 200, 'data': [c_sinfo.to_json()]})
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'msg':'fail!', 'code':500})

### 退项
@sample.post('/exitproject')
def exitproject():
    sampleBarcode = request.get_json()['sampleBarcode']
    projectName = request.get_json()['projectName']
    c_sinfo = SampleInfo.query.filter(and_(SampleInfo.sampleBarcode==sampleBarcode, SampleInfo.projectName==projectName)).first()
    if not c_sinfo:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        c_sinfo.update(sampleStatus='已退项')
        db.session.commit()
    return jsonify({'msg': 'success', 'code': 200})

### 检索待定样本样本
@sample.get('/searchpending')
def searchpending():
    c_sinfo = pendingSample.query.filter(pendingSample.projectName=='待定').order_by(pendingSample.addtime.desc()).all()
    if not c_sinfo:
        return jsonify({'msg': 'no data', 'code': 204})
    else:
        return jsonify({'msg': 'success', 'code': 200, 'data': [i.to_json() for i in c_sinfo]})