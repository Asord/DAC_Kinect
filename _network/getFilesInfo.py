from os import walk
from os.path import join, getsize, getmtime
from json import dumps

class getFilesInfo:

    def __init__(self, root, ignore_files = None, ignore_dirs = None):
        self._root = root
        self._ignore_files = ignore_files if ignore_files is not None else ["desktop.ini"]
        self._ignore_dirs = ignore_dirs if ignore_dirs is not None else ["__lib", ".idea", "__pycache__"]

        self._content = self.__getFiles()

        self._infoData = self.__getFilesInfo()

    def getFiles(self):
        return self._content

    def getFilesInfo(self):
        return self._infoData

    def getFormatedFileInfo(self):
        return str.encode(dumps(self._infoData))

    def __getFilesInfo(self):
        result = {}
        for file in self._content:
            result[file] = (getsize(file), getmtime(file))

        return result

    def __getFiles(self):
        fileList = []

        for root, directories, files in walk(self._root):

            if self.__is_root_ignored(root): continue

            for file in files:
                if file in self._ignore_files: continue
                fileList.append(join(root, file))

        return fileList

    def __is_root_ignored(self, root):
        for ignore in self._ignore_dirs:
            if ignore in root: return True
        return False

def compare(localFileList, distantFileList):
    result = []
    for file in distantFileList:
        if file in localFileList:
            size, time = localFileList[file]
            dsize, dtime = distantFileList[file]
            if size != dsize or time != dtime:
                result.append(file)

    return result

def serializedCompare(localFileList, distantFileList):
    res = compare(localFileList, distantFileList)
    return str.encode(dumps(res))