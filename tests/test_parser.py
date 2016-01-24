from wolf.parser import Parser


def test_package_name():

    file_list = ["tests/javaExamples/Test.java"]

    parser = Parser(file_list)

    for class_desc in parser.get_class_descs():
        assert class_desc.name == "Test"
        assert class_desc.package == "javalang.brewtab.com"
