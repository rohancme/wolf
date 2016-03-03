from repo_handler import RepoHandler
from parser import Parser
from mvn_runner import MvnRunner
from randoop_runner import RandoopRunner
from pitest import PITest
import sys
import os

cmd_args = sys.argv
skip_class_list = []
for arg in cmd_args:
    param = arg.split('=')
    if param[0] == 'skipClassList':
        if os.path.exists(param[1]):
            with open(param[1], 'r') as listFile:
                data = listFile.read()
            skip_class_list = data.split('\n')
        else:
            print 'path does not exist'

rh = RepoHandler(repo_url='https://github.com/rometools/rome.git')
print "Cloning repo..."
rh.clone_repo()
print "Done."
# rh = RepoHandler(temp_dir_path='/home/rohan/courses/wolf/rome')
print "Repo cloned in folder:" + rh.get_path()

print "Retrieving the list of modified files.."

file_name_list = []
valid_file_desc = []

# Get the list of all the recently modified java files which are not tests
repo_path = '/'.join([rh.get_path(), 'rome'])

for file_desc in rh.get_modified_files(prev_commits=10):

    if repo_path in file_desc.path:
        if (file_desc.ext == ".java"):
            if '/test' not in file_desc.path:
                print 'Adding ' + file_desc.path
                file_name_list += [file_desc.path]
                valid_file_desc += [file_desc]

parser = Parser(file_name_list)
class_desc_list = parser.get_class_descs()
print "Done."

print "Inserting PITest plugin into existing pom.xml.."
pitest_runner = PITest('/'.join([repo_path, 'pom.xml']))
pitest_runner.insert_into_pom('com.rometools')
print "Done."

print "Assembling the jar with dependencies.."
mvn_runner = MvnRunner(repo_path, True)
# assemble the jar with dependencies
jar_path = mvn_runner.get_jar_with_deps()

if jar_path is None:
    mvn_runner.assemble_with_deps()
    jar_path = mvn_runner.get_jar_with_deps()
print "Done."

print "Running PITest for initial analysis.."
mvn_runner.custom('org.pitest:pitest-maven:mutationCoverage')
print "Done."


print "Running Randoop..."
randoop_runner = RandoopRunner('randoop-2.1.1.jar', jar_path, quiet_mode=True)

for file_d, class_d in zip(valid_file_desc, class_desc_list):

    if class_d.name not in skip_class_list:
        print class_d.name + ' not in '
        print skip_class_list
        print "Generating tests for:" + class_d.name
        randoop_runner.generate_tests(file_d, class_d)

print "Done."

print "Running mvn install to generate new class files.."
mvn_runner.install()
print "Done."

print "Running PITest for final analysis.."
mvn_runner.custom('org.pitest:pitest-maven:mutationCoverage')
print "Done."
# for class_desc in parser.get_class_descs():
#     print class_desc
#     print ""

# rh.delete_temp_dir()
