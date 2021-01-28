import pandas as pd

from configuration import OUT_PATH


def genGpx(inPath, fileName):
    filePath = f"{inPath}/{fileName}"

    df = pd.read_csv(f"{inPath}/{fileName}", delimiter=';', encoding='utf_8')
    df = df.drop(axis=0, index=[0])  # drop the first row

    lats = df[df.keys()[3]].values
    lons = df[df.keys()[4]].values
    alts = df[df.keys()[5]].values
    assert len(lats) == len(lons) == len(alts)

    gpxHeader = """<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" creator="gpx.py -- https://github.com/tkrajina/gpxpy">
  <trk>
    <name>Active Log: 18 SEP 2019 13:49</name>
    <trkseg>
    """
    gpxFooter = """    </trkseg>
  </trk>
</gpx>"""
    trackPointTeplate = """<trkpt lat="{lat}" lon="{lon}"><ele>{alt}</ele></trkpt>"""

    fn = OUT_PATH + fileName[:fileName.rindex('.')] + '.gpx'
    print(f"Writing flight track to '{fn}'")
    with open(fn, 'w') as f:
        f.write(gpxHeader + '\n')

        for i in range(len(lats)):
            lat = lats[i].strip()
            lon = lons[i].strip()
            alt = float(alts[i].strip()) * 0.3048   # ft -> m

            if lat != "" and lon != "" and alt != "":
                line = trackPointTeplate.format(lat=lat, lon=lon, alt=alt)
                f.write(line + '\n')

        f.write(gpxFooter + '\n')

    return df


if __name__ == '__main__':
    inPath = '/home/ibisek/wqz/prog/python/radec-dataAnalyser/data/'
    fileName = ''

    df = genGpx(inPath, fileName)

    print('KOHEU.')
