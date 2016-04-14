from repo_handler import RepoHandler
from parser import Parser
from mvn_runner import MvnRunner
from randoop_runner import RandoopRunner
from pitest import PITest
from test_reducer import TestReducer
import os
import argparse

parser = argparse.ArgumentParser()

repo_path = None

parser.add_argument('--url',
                    metavar='URL',
                    help='The Github URL for the repo')
parser.add_argument('--repoPath',
                    metavar='FOLDER',
                    help='Local Path to existing maven java project')
parser.add_argument('--skipClassList',
                    default='skipClasses.txt',
                    metavar='FILE',
                    help='Specify a file with classes that should be ignored')
parser.add_argument('--testListFile',
                    default='testFileList.txt',
                    metavar='FILE',
                    help='Specify output file with list of tests generated')
parser.add_argument('--numCommits',
                    help='Numbers of commits to check for modified files' +
                    '(default 20)',
                    metavar='INTEGER',
                    type=int,
                    default=20)
parser.add_argument('--subfolder',
                    metavar='FOLDER',
                    help='Specify a specific subfolder for which wolf should'
                    ' be run. NOTE: The subfolder must contain pom.xml')
parser.add_argument('--randoopPath',
                    metavar='JAR',
                    default='randoop-2.1.1.jar',
                    help='Path to the randoop jar wolf should use')
parser.add_argument('--testsPerFile',
                    help='Max number of tests per test file (default 500)',
                    metavar='INTEGER',
                    type=int,
                    default=500)
parser.add_argument('--randoopTimeout',
                    help='Max time randoop should spend on generating tests',
                    metavar='SECONDS',
                    type=int,
                    default=10)
parser.add_argument('--reduce',
                    action='store_true',
                    help='Attempt to reduce the number of test cases')
parser.add_argument('--noPrompts',
                    action='store_true',
                    help='No prompts after each step. Wolf runs with all ' +
                    'options specified without waiting for additional inputs.')
args = parser.parse_args()

skip_class_list = []
if args.skipClassList:
    if os.path.exists(args.skipClassList):
        with open(args.skipClassList, 'r') as listFile:
            data = listFile.read()
        skip_class_list = data.split('\n')
    else:
        print '\033[91mERROR: Path does not exist:' + args.skipClassList
        print 'Proceeding without skipping any files..\033[37m'

if skip_class_list:
    print skip_class_list

if args.repoPath:
    repo_path = args.repoPath
    rh = RepoHandler(temp_dir_path=repo_path)

elif args.url:
    repo_url = args.url
    rh = RepoHandler(repo_url=repo_url)
    print "***********************************************"
    print "\033[92mCloning repo...\033[37m"
    rh.clone_repo()
    print "\033[92mDone.\033[37m"
    print "Repo cloned in folder:" + rh.get_path()
    print "***********************************************\n"

if not args.noPrompts:
    raw_input()

num_commits = args.numCommits

print "***********************************************"
print "\033[92mRetrieving the list of modified files..\033[37m"
print "Number of commits being analyzed:" + str(num_commits)

file_name_list = []
valid_file_desc = []

if args.subfolder:
    repo_path = '/'.join([rh.get_path(), args.subfolder])

if not repo_path:
    repo_path = rh.get_path()
# Get the list of all the recently modified java files which are not tests

print "Generating test cases for:"
path_with_slash = repo_path + '/'
for file_desc in rh.get_modified_files(prev_commits=num_commits):

    if path_with_slash in file_desc.path:
        if (file_desc.ext == ".java"):
            if '/test' not in file_desc.path:
                print file_desc.path
                # print file_desc.change_type
                file_name_list += [file_desc.path]
                valid_file_desc += [file_desc]

parser = Parser(file_name_list)
class_desc_list = parser.get_class_descs()

package_list = []

for class_desc in class_desc_list:
    print class_desc.package + '.' + class_desc.name
    package_list += [class_desc.package]
package_name = os.path.commonprefix(package_list)
if package_name.endswith('.'):
    package_name = package_name[:-1]
print "Package Name:" + package_name
print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()


print "***********************************************"
print "\033[92mInserting PITest plugin into existing pom.xml..\033[37m"
pitest_runner = PITest('/'.join([repo_path, 'pom.xml']))
pitest_runner.insert_into_pom(package_name)
print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()

print "***********************************************"
print "\033[92mAssembling the jar with dependencies..\033[37m"
mvn_runner = MvnRunner(project_path=rh.get_path(), subfolder=args.subfolder,
                       quiet_mode=True)
# assemble the jar with dependencies
jar_path = mvn_runner.get_jar_with_deps()
if jar_path is None:
    mvn_runner.assemble_with_deps()
    jar_path = mvn_runner.get_jar_with_deps()
print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()

print "***********************************************"
print "\033[92mRunning PITest for initial analysis..\033[37m"
mvn_runner.custom('org.pitest:pitest-maven:mutationCoverage')
print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()

print "***********************************************"
print "\033[92mRunning Randoop...\033[37m"
randoop_runner = RandoopRunner(randoop_jar=args.randoopPath,
                               project_jar=jar_path,
                               timeout=args.randoopTimeout,
                               quiet_mode=True,
                               tests_per_file=args.testsPerFile)

test_file_list = []

for file_d, class_d in zip(valid_file_desc, class_desc_list):

    if class_d.name not in skip_class_list:
        print "Generating tests for:" + class_d.name
        file_list = randoop_runner.generate_tests(file_d, class_d)
        if file_list is not None:
            test_file_list += file_list

with open(args.testListFile, 'w') as outFile:
    outFile.write('\n'.join(test_file_list))

print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()

mvn_runner = MvnRunner(project_path=rh.get_path(), subfolder=args.subfolder,
                       quiet_mode=True)
if args.reduce:
    print "***********************************************"
    print "\033[92mReducing number of test cases...\033[37m"
    reducer = TestReducer(test_files=args.testListFile,
                          mvn_runner=mvn_runner)
    # reducer.group_tests()
    reducer.reduce()
    print "\033[92mDone.\033[37m"
    print "***********************************************\n"


print "***********************************************"
print "\033[92mGenerating new class files..\033[37m"
mvn_runner.clean()
mvn_runner.install()
print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()

print "***********************************************"
print "\033[92mRunning PITest for final analysis..\033[37m"
mvn_runner.custom('org.pitest:pitest-maven:mutationCoverage')
print "\033[92mDone.\033[37m"
print "***********************************************\n"
if not args.noPrompts:
    raw_input()
