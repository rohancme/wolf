from repo_handler import RepoHandler
from parser import Parser

rh = RepoHandler("https://github.com/Netflix/Hystrix.git",
                 temp_dir_path='temp_dir')
rh.clone_repo()
for file_desc in rh.get_modified_files():
    print file_desc
    print ""


file_name_list = []

for file_desc in rh.get_modified_files():
    file_name_list += [file_desc.path]

parser = Parser(file_name_list)

for class_desc in parser.get_class_descs():
    print class_desc
    print ""

rh.delete_temp_dir()
