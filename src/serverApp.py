import sys
import traceback
from typing import List
import os
import signal

from data.structures import EngineWork
from db.dao.filesDao import FilesDao, File, FileStatus
from flow.preprocessing import checkForWork, migrate, preprocess
from flow.processing import Processing
from flow.fileFormatIdentification import FileFormatDetector

if __name__ == '__main__':
    processing = Processing()
    filesDao = FilesDao()

    file: File = checkForWork()
    while file:
        res = migrate(file)
        if not res:
            file.status = FileStatus.FAILED
            filesDao.save(file)
            print(f'[ERROR] Could not migrate file.id {file.id} or the file is not available!')
            continue

        FileFormatDetector.identify(file)

        try:
            file.status = FileStatus.UNDER_ANALYSIS
            filesDao.save(file)  # TODO uncomment (!)

            engineWorks: List[EngineWork] = preprocess(file)
            for ew in engineWorks:
                processing.process(engineWork=ew)

            file.status = FileStatus.ANALYSIS_COMPLETE
            print(f'[INFO] Work for file id {file.id} finished.')

        except Exception as ex:
            print(f"[ERROR] in processing file id {file.id}:", str(ex))
            traceback.print_exc(file=sys.stdout)
            file.status = FileStatus.FAILED

        finally:
            filesDao.save(file)  # TODO uncomment (!)

        # get next work assignment:
        file: File = checkForWork()

    print('KOHEU.')

    pid = os.getpid()
    if pid:
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        print(f"[FATAL] No PID for running process: {pid}")

    sys.exit()    # does not normally work as there is an sqlAchemy thread hanging.. Hence the genocide above.
