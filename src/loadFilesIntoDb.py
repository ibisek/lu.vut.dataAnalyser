"""
Script for loading files into processing system.
This serves as mass alternative to manual upload via the web interface.
"""

import os
import shutil
import hashlib

from dao.configurationDao import getConfiguration
from dao import fileDao
from dao.fileDao import File, FileStatus

c = getConfiguration()
FILE_INGESTION_ROOT = c['FILE_INGESTION_ROOT']
FILE_STORAGE_ROOT = c['FILE_STORAGE_ROOT']

if __name__ == '__main__':

    IN_PATH = '/tmp/00/'
    ENGINE_ID = 1

    print(f"[INFO] Reading files from {IN_PATH}..")

    for fileName in sorted(os.listdir(IN_PATH)):
        srcFilePath = f"{IN_PATH}/{fileName}"

        if os.path.isfile(srcFilePath) and fileName.lower().endswith('.csv'):
            print(f"[INFO] Processing {fileName}..")

            with open(srcFilePath, "rb") as f:
                bytes = f.read()
                fileHash = hashlib.sha256(bytes).hexdigest()

            print("[INFO] file hash:", fileHash, len(fileHash))

            flightId = None
            engineId = ENGINE_ID
            source = True
            generated = False
            status = FileStatus.UNDEF

            file: File = File(id=None, name=fileName, flightId=flightId, engineId=engineId, source=source, generated=generated, status=status, hash=fileHash)

            file = fileDao.save(file)

            # mv file from IN_DIR to FILE_INGESTION_ROOT:
            dstFilePath = f"{FILE_INGESTION_ROOT}/{file.id}"
            print(f"[INFO] mv '{srcFilePath}' '{dstFilePath}'")
            shutil.move(src=srcFilePath, dst=dstFilePath)

            file.status = FileStatus.READY_TO_PROCESS
            fileDao.save(file)

    print('KOHEU.')
