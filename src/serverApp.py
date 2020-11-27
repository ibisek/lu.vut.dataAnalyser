
from dao.fileDao import FileDao, File, FileStatus
from flow.preprocessing import checkForWork, prepare, process

if __name__ == '__main__':
    while True:
        file: File = checkForWork()

        if not file:
            break

        if file and prepare(file):
            try:
                process(file)
                # TODO uncomment (!)
                FileDao.setFileStatus(file=file, status=FileStatus.ANALYSIS_COMPLETE)

            except Exception as ex:
                print(f"[ERROR] in processing file {file}:", str(ex))
                FileDao.setFileStatus(file=file, status=FileStatus.FAILED)

    print('KOHEU.')
