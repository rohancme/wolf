class FileDesc(object):

    def __init__(self, path, ext, change_type=None):
        self.path = path
        self.ext = ext
        self.change_type = change_type

    def __str__(self):
        string = "<File Descriptor Object>"
        string += "\nFull Path:" + self.path
        string += "\nExtension:" + self.ext
        string += "\nChange Type:" + self.change_type
        string += "\n\t------------------"
        return string
