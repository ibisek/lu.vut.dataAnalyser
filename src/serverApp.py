import sys
import traceback
from time import sleep
from typing import List

from data.structures import EngineWork
from db.dao.filesDao import FilesDao, File, FileStatus
from flow.preprocessing import checkForWork, migrate, preprocess
from flow.processing import Processing
from flow.fileFormatIdentification import FileFormatDetector


if __name__ == '__main__':
    processing = Processing()
    filesDao = FilesDao()

    while True:
        file: File = checkForWork()

        if not file:
            sleep(30)
            continue

        res = migrate(file)
        if not res:
            file.status = FileStatus.FAILED
            filesDao.save(file)
            print(f'[ERROR] Could not migrate file.id {file.id} or the file is not available!')
            continue

        FileFormatDetector.identify(file)

        try:
            file.status = FileStatus.UNDER_ANALYSIS
            # filesDao.save(file)  # TODO uncomment (!)

            engineWorks: List[EngineWork] = preprocess(file)
            for ew in engineWorks:
                processing.process(engineWork=ew)

            file.status = FileStatus.ANALYSIS_COMPLETE

        except Exception as ex:
            print(f"[ERROR] in processing file {file}:", str(ex))
            traceback.print_exc(file=sys.stderr)
            file.status = FileStatus.FAILED

        finally:
            filesDao.save(file)     # TODO uncomment (!)

    print('KOHEU.')
