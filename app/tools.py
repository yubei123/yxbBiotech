from app.updatedb.top15models import IGHtop15,IGKtop15,IGLtop15,IGDHtop15,KDEtop15,TRBDJtop15,TRBVJtop15,TRDDJtop15,TRDVJtop15,TRGtop15
from app.updatedb.top15models import app as apps
from app.updatedb.top15models import db as dbs
from sqlalchemy import and_
from collections import defaultdict

top15db = {'IGH':IGHtop15, 'IGDH':IGDHtop15, 'IGK':IGKtop15, 'IGL':IGLtop15, 'IGK+':KDEtop15, \
           'TRB':TRBVJtop15, 'TRB+':TRBDJtop15, 'TRD':TRDVJtop15, 'TRD+':TRDDJtop15, 'TRG':TRGtop15}

def generateLibID(data):
    missdata = []
    n = 0
    for i in ['labDate', 'sampleBarcode', 'barcodeGroup', 'labSite', 'labUser', 'diagnosisPeriod']:
        if data[i] == '' or data[i] == None:
            missdata.append(i)
        else:
            n += 1
    if n == 6:
        libID = f'{data["labDate"]}-{data["sampleBarcode"]}-{data["barcodeGroup"]}-{data["diagnosisPeriod"]}-{data["labSite"]}-{data["labUser"]}'
        return {'msg':'success', 'libID':libID}
    else:
        return {'msg':'fail', 'missdata':missdata}
    
def getCloneInfo(libID):
    labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = libID.split('/')[-1].split('-')
    data = defaultdict(list)
    with apps.app_context():
        if labSite == 'BCR':
            for i in ['IGH', 'IGDH', 'IGK', 'IGK+','IGL']:
                cloneinfo = top15db[i].query.filter(and_(top15db[i].sampleBarcode == sampleBarcode, top15db[i].labDate == labdate, \
                                                         top15db[i].barcodeGroup == barcodeGroup, top15db[i].markerYN == 'yes')).all()
                for j in cloneinfo:
                    data[i].append({'CDR3':j.markerSeq,'vgene':j.vGene, 'jgene':j.jGene})
        else:
            for i in ['TRB', 'TRB+','TRD', 'TRD+','TRG']:
                cloneinfo = top15db[i].query.filter(and_(top15db[i].sampleBarcode == sampleBarcode, top15db[i].labDate == labdate, \
                                                         top15db[i].barcodeGroup == barcodeGroup, top15db[i].markerYN == 'yes')).all()
                for j in cloneinfo:
                    data[i].append({'CDR3':j.markerSeq,'vgene':j.vGene, 'jgene':j.jGene})
        return data