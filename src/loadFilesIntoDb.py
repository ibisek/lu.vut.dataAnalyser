"""
Script for loading files into processing system.
This serves as mass alternative to manual upload via the web interface.
"""

import os
import shutil
import hashlib

from dao.configurationDao import getConfiguration
from db.dao.filesDao import FilesDao, FileStatus
from db.dao.airplanesDao import AirplanesDao
from db.dao.enginesDao import EnginesDao
from db.dao.flightsDao import FlightsDao
from db.dao.filesFlightsDao import FilesFlightsDao
from db.dao.enginesFlightsDao import EnginesFlightsDao
from data.structures import FileFormat

c = getConfiguration()
FILE_INGESTION_ROOT = c['FILE_INGESTION_ROOT']
FILE_STORAGE_ROOT = c['FILE_STORAGE_ROOT']

if __name__ == '__main__':

    IN_PATH = '/tmp/00/'

    # AIRPLANE_ID = 1         # Pilatus PC-12 / PC6
    AIRPLANE_ID = 3         # L410 / 2 x H80

    # --

    airplanesDao = AirplanesDao()
    airplane = airplanesDao.getOne(id=AIRPLANE_ID)
    assert airplane

    enginesDao = EnginesDao()
    engines = enginesDao.get(airplane_id=airplane.id)
    engines = [e for e in engines]
    assert len(engines) > 0

    # --

    filesDao = FilesDao()
    flightsDao = FlightsDao()
    filesFlightsDao = FilesFlightsDao()
    enginesFlightsDao = EnginesFlightsDao()

    print(f"[INFO] Reading files from {IN_PATH}..")

    for fileName in sorted(os.listdir(IN_PATH)):
        srcFilePath = f"{IN_PATH}/{fileName}"

        if os.path.isfile(srcFilePath) and fileName.lower().endswith('.csv'):
            print(f"[INFO] Processing {fileName}..")

            if '___' in fileName:   # files with multiple underscores in name are empty
                continue

            with open(srcFilePath, "rb") as f:
                bytes = f.read()
                fileHash = hashlib.sha256(bytes).hexdigest()

            print("[INFO] file hash:", fileHash)

            file = filesDao.getOne(name=fileName)
            if file:
                print(f"[WARN] File '{fileName}' already in DB .. skipping.")
                continue

            file = filesDao.createNew()
            file.name = fileName
            file.raw = True
            file.status = FileStatus.UNDEF
            file.format = FileFormat.UNDEFINED
            file.hash = fileHash
            filesDao.save(file)

            # create new flight:
            flight = flightsDao.createNew()
            flight.airplane_id = airplane.id
            flightsDao.save(flight)

            # create new flight-file record:
            ff = filesFlightsDao.createNew()
            ff.file_id = file.id
            ff.flight_id = flight.id
            filesFlightsDao.save(ff)

            # create new flight-engine record:
            for engine in engines:
                ef = enginesFlightsDao.createNew()
                ef.engine_id = engine.id
                ef.flight_id = flight.id
                enginesFlightsDao.save(ef)

            # mv file from IN_DIR to FILE_INGESTION_ROOT:
            dstFilePath = f"{FILE_INGESTION_ROOT}/{file.id}"
            print(f"[INFO] mv '{srcFilePath}' '{dstFilePath}'")
            shutil.move(src=srcFilePath, dst=dstFilePath)

            file.status = FileStatus.READY_TO_PROCESS
            filesDao.save(file)

    print('KOHEU.')
