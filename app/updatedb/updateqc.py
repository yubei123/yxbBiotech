import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from qcmodels import IGHqc, IGDHqc, IGKqc, IGLqc, TRBDJqc, TRBVJqc, TRDqc, TRGqc
from sqlalchemy import and_
from qcmodels import app, db

qcdb = {'IGH': IGHqc, 'IGDH': IGDHqc, 'IGK': IGKqc, 'IGL': IGLqc, 'TRBDJ': TRBDJqc, 'TRBVJ': TRBVJqc, 'TRD': TRDqc, 'TRG': TRGqc}

def updateData(input):
    try:
        with app.app_context():
            labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = input.split('/')[-1].split('.')[0].split('-')
            with open(input, 'r', encoding='gbk') as f:
                head = f.readline().strip().split(',')
                for line in f:
                    l = line.strip().split(',')
                    data = {
                        'sampleBarcode': sampleBarcode,'labDate': labdate,'barcodeGroup': barcodeGroup,'labUser' : labUser,
                        'posQC' : l[2], 'negQC' : l[3], 'samplesPollute' : l[4],
                        'totalReads' : l[5], 'totalReadsRes' : l[6],
                        'q30' : l[7], 'q30Res' : l[8],
                        'primerDimers' : l[9], 'primerDimersRes' : l[10],
                        'assembleRate' : l[11], 'assembleRateRes' : l[12],
                        'qcRes' : l[13],'qcReads' : l[14]
                        }
                    for i, e in enumerate(l[15:]):
                        if e != '':
                            data.update({f'{head[15+i].lower()}' : e})
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