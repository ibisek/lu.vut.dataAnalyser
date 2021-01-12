"""
File type identification.
"""

from data.sources.fileLoader import loadRawData
from data.structures import FileFormat

from dao.configurationDao import getConfiguration
from db.dao.filesDao import FilesDao, FileStatus


class FileFormatDetector:
    filesDao = FilesDao()
    FILE_STORAGE_ROOT = getConfiguration()['FILE_STORAGE_ROOT']

    def processFilesInDb(self):
        resultSet = self.filesDao.get(status=FileStatus.READY_TO_PROCESS.value, format=0)
        for file in resultSet:
            path = f'{self.FILE_STORAGE_ROOT}/{file.id}'
            fileFormat = self.identifyFileFormat(path=path, filename=file.name)

            file.format = fileFormat.value
            self.filesDao.save(file)

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
                return fileFormat  # loading was successful, this is the right format

            except (ValueError, IndexError) as e:
                pass

        print(f'[INFO] Detected {fileFormat}')

        return FileFormat.UNKNOWN

    @staticmethod
    def identify(file):
        if file.format not in [FileFormat.UNKNOWN, FileFormat.UNDEFINED]:
            return  # file format already identified; repeated identifications is just waste of time

        path = f'{FileFormatDetector.FILE_STORAGE_ROOT}/{file.id}'
        file.format = FileFormatDetector.identifyFileFormat(path, file.name)
        FileFormatDetector.filesDao.save(file)


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
