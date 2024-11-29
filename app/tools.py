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