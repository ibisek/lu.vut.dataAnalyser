from time import sleep
from typing import List

from data.structures import EngineWork
from db.dao.filesDao import FilesDao, File, FileStatus
from flow.preprocessing import checkForWork, prepare, preprocess
from flow.processing import Processing

if __name__ == '__main__':
    processing = Processing()

    while True:
        file: File = checkForWork()

        if not file:
            sleep(30)

        elif prepare(file):
            try:
                FilesDao.setFileStatus(file=file, status=FileStatus.UNDER_ANALYSIS)

                engineWorks: List[EngineWork] = preprocess(file)
                for ew in engineWorks:
                    processing.process(engineWorks=ew)

                # TODO uncomment (!)
                FilesDao.setFileStatus(file=file, status=FileStatus.ANALYSIS_COMPLETE)

            except Exception as ex:
                print(f"[ERROR] in processing file {file}:", str(ex))
                FilesDao.setFileStatus(file=file, status=FileStatus.FAILED)

    print('KOHEU.')
