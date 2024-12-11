# from app.updatedb.top15models import IGHtop15,IGKtop15,IGLtop15,IGDHtop15,KDEtop15,TRBDJtop15,TRBVJtop15,TRDDJtop15,TRDVJtop15,TRGtop15
# from app.updatedb.top15models import IGHtop15, TRBVJtop15
# from app.updatedb.top15models import app as apps
# from app.updatedb.top15models import db as dbs
from sqlalchemy import and_
from collections import defaultdict
from app import db
from app.models import SampleInfo, Traceableclones

# top15db = {'IGH':IGHtop15, 'IGDH':IGDHtop15, 'IGK':IGKtop15, 'IGL':IGLtop15, 'IGK+':KDEtop15, \
#            'TRB':TRBVJtop15, 'TRB+':TRBDJtop15, 'TRD':TRDVJtop15, 'TRD+':TRDDJtop15, 'TRG':TRGtop15}

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
    
def getCloneInfo(libID, patientID, current_sampleCollectionTime):
    labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = libID.split('/')[-1].split('-')
    data = defaultdict(list)
    cloneinfo = Traceableclones.query.filter(and_(Traceableclones.patientID == patientID, Traceableclones.sampleCollectionTime != current_sampleCollectionTime)).order_by(Traceableclones.sampleCollectionTime.desc()).first()
    cloneinfos = Traceableclones.query.filter(Traceableclones.sampleCollectionTime == cloneinfo.sampleCollectionTime).all()
    for i in cloneinfos:
        data[i.pcrSite].append({'CDR3':i.markerSeq,'vgene':i.vGene, 'jgene':i.jGene})
    return data