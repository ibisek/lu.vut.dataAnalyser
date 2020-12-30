from time import sleep
from typing import List

from data.structures import EngineWork
from dao.fileDao import FileDao, File, FileStatus
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
                FileDao.setFileStatus(file=file, status=FileStatus.UNDER_ANALYSIS)

                engineWorks: List[EngineWork] = preprocess(file)
                for ew in engineWorks:
                    processing.process(engineWorks=ew)

                # TODO uncomment (!)
                FileDao.setFileStatus(file=file, status=FileStatus.ANALYSIS_COMPLETE)

            except Exception as ex:
                print(f"[ERROR] in processing file {file}:", str(ex))
                FileDao.setFileStatus(file=file, status=FileStatus.FAILED)

    print('KOHEU.')
