import javalang
from structs.java_class_desc import JavaClassDesc


class Parser(object):

    def __init__(self, files=None):

        self.class_list = []

        for fileName in files:
            self.parse(fileName)

    def parse(self, file_name):

        try:
            with open(file_name, "r") as file:
                contents = file.read()
        except IOError:
            return None
        tree = javalang.parse.parse(contents)

        package_name = tree.package.name
        class_name = None

        for child in tree.types:
            if type(child) is javalang.tree.ClassDeclaration:
                class_name = child.name
                break
        if class_name is not None:
            java_descriptor = JavaClassDesc(name=class_name, package=package_name)
            self.class_list += [java_descriptor]
        # else:
        #     print "No class found for:" + str(file_name)

    def get_class_descs(self):
        return self.class_list
