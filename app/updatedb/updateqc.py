import sys
from qcmodels import IGHqc, IGDHqc, IGKqc, IGLqc, TRBDJqc, TRBVJqc, TRDqc, TRGqc, SampleInfo
from sqlalchemy import and_
from qcmodels import app, db

qcdb = {'IGH': IGHqc, 'IGDH': IGDHqc, 'IGK': IGKqc, 'IGL': IGLqc, 'TRBDJ': TRBDJqc, 'TRBVJ': TRBVJqc, 'TRD': TRDqc, 'TRG': TRGqc}

def updateData(input):
    try:
        with app.app_context():
            with open(input, 'r', encoding='utf-8') as f:
                head = f.readline().strip().split(',')
                for line in f:
                    l = line.strip().split(',')
                    print(head)
                    labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = l[0].split('-')
                    data = {
                        'sampleBarcode': sampleBarcode,'labDate': labdate,'barcodeGroup':barcodeGroup,'labUser':labUser, 
                        'posQC' : l[3], 'posQCres':l[4], 'negQC' : l[5], 'samplesPollute' : l[6],
                        'totalReads' : l[7], 'totalReadsRes' : l[8],
                        'q30' : l[9], 'q30Res' : l[10],
                        'primerDimers' : l[11], 'primerDimersRes' : l[12],
                        'assembleRate' : l[13], 'assembleRateRes' : l[14],
                        'qcRes' : l[15],'qcReads' : l[16], 'finalQCres' : l[2]
                        }
                    for i, e in enumerate(l[17:]):
                        if e != '':
                            data.update({f'{head[17+i].lower()}' : e})
                    qc = qcdb[l[1]].query.filter(and_(qcdb[l[1]].sampleBarcode==sampleBarcode, qcdb[l[1]].barcodeGroup==barcodeGroup, qcdb[l[1]].labDate==labdate)).first()
                    if qc:
                        qc.update(**data)
                    else:
                        qcinfo = qcdb[l[1]](**data)
                        db.session.add(qcinfo)
            db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

if __name__ == "__main__":
    input = sys.argv[1]
    updateData(input)