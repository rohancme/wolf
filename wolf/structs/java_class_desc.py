

class JavaClassDesc(object):

    def __init__(self, name, package):
        self.name = name
        self.package = package

    def __str__(self):
        string = "<Java Class Descriptor Object>"
        string += "\nName: " + self.name
        string += "\nPackage: " + self.package
        string += "\n\t-------------------------"
        return string
