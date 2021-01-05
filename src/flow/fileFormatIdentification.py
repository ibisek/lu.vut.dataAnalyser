"""
File type identification.
"""

from data.sources.fileLoader import loadRawData
from data.structures import FileFormat

from dao.configurationDao import getConfiguration
from db.dao.filesDao import FilesDao, FileStatus


class FileFormatDetector:
    filesDao = FilesDao()

    def __init__(self):
        dbConfiguration = getConfiguration()
        self.FILE_STORAGE_ROOT = dbConfiguration['FILE_STORAGE_ROOT']

    def processFilesInDb(self):
        resultSet = self.filesDao.get(status=FileStatus.READY_TO_PROCESS.value, format=0)
        for file in resultSet:
            path = f'{self.FILE_STORAGE_ROOT}/{file.id}'
            fileFormat = self.identifyFileFormat(path=path, filename=file.name)

            file.format = fileFormat.value
            self.filesDao.save(file)

            file = self.filesDao.getOne(status=FileStatus.READY_TO_PROCESS.value, format=0)

    @staticmethod
    def identifyFileFormat(path: str, filename: str) -> FileFormat:
        """
        :param path:
        :param filename:
        :return: detected file format
        """
        print(f'[INFO] File format identification of {path}/{filename}')

        for fileFormat in FileFormat:
            if fileFormat is FileFormat.UNDEFINED or fileFormat is FileFormat.UNKNOWN:
                continue

            try:
                loadRawData(fileFormat=fileFormat, inPath=path, fileName=filename)
                break  # loading was successful, this is the right format

            except ValueError as e:
                pass

        print(f'[INFO] Detected {fileFormat}')

        return fileFormat


if __name__ == '__main__':
    # path = '/tmp/00/'
    #
    # filename = 'pt6.csv'
    # # filename = 'let.txt'
    #
    # ff: FileFormat = FileFormatDetector.identifyFileFormat(path, filename)
    # print('Detected file format:', ff)

    # --

    ffd = FileFormatDetector()
    ffd.processFilesInDb()

    print('KOHEU.')
