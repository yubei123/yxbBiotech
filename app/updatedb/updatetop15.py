import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from top15models import IGHtop15,IGKtop15,IGLtop15,IGDHtop15,KDEtop15,TRBDJtop15,TRBVJtop15,TRDDJtop15,TRDVJtop15,TRGtop15

app = Flask(__name__)
app.config.from_pyfile('/data/yubei/Biotech/config.py')
db = SQLAlchemy(app)

top15db = {'IGH':IGHtop15, 'IGDH':IGDHtop15, 'IGK':IGKtop15, 'IGL':IGLtop15, 'IGK+':KDEtop15, \
           'TRB':TRBVJtop15, 'TRB+':TRBDJtop15, 'TRD':TRDVJtop15, 'TRD+':TRDDJtop15, 'TRG':TRGtop15}

def updateData(input):
    try:
        with app.app_context():
            labdate,sampleBarcode,barcodeGroup,diagnosisPeriod,labSite,labUser = input.split('/')[-1].split('.')[0].split('-')
            with open(input, 'r') as f:
                for line in f:
                    l = line.strip().split(',')
                    if l[0].startswith('IG'):
                        ig = l[0].split('-')
                        continue
                    data = {
                            'sampleBarcode': sampleBarcode,
                            'labDate': labdate,
                            'barcodeGroup': barcodeGroup,
                            'top' : l[0],
                            'markerReads' : l[2],
                            'cloneFreq' : l[3],
                            'cellRatio' : l[6],
                            'ampFactor' : l[9],
                            'markerCellsByN' : l[7],
                            'markerSeq' : l[1],
                            'vGene' : l[4],
                            'jGene' : l[5],
                            'adjustedCellRatio' : l[11],
                            'markerYN' : l[10]
                        }
                    top15 = top15db[ig[0]](**data)
                    db.session.add(top15)
            db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()

if __name__ == "__main__":
    input = sys.argv[1]
    updateData(input)