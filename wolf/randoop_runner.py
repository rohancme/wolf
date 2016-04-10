"""This module handles all the functionality related to a github repo."""
from subprocess import call
import shutil
import os
import fnmatch


class RandoopRunner(object):

    def __init__(self, randoop_jar, project_jar, timeout,
                 tests_per_file, quiet_mode=False):
        """Initialize randoop and project jar paths."""
        self.randoop_jar = randoop_jar
        self.project_jar = project_jar
        self.quiet_mode = quiet_mode
        self.timeout = timeout
        self.tests_per_file = tests_per_file

    def generate_tests(self, file_desc, class_desc):
        """Generate tests and move them to correct directory."""
        list_of_tests = []
        path = file_desc.path
        class_name = class_desc.name
        package_name = class_desc.package

        test_path = path.replace('/main/', '/test/', 1)

        # strip the name of the class under test
        test_path = test_path[0:test_path.rfind('/')]

        self.run(package_name, class_name)

        if not os.path.isfile('RegressionTest.java'):
            print "No RegressionTests generated!"
            return None

        # Now we have Regression tests and Error Tests
        # Handling Regression Tests only for now
        # **********PLEASE clean this up somehow. This is horrible

        new_file_contents = ['package ' + package_name + ';',
                             'import junit.framework.JUnit4TestAdapter;']

        new_class_descriptor = 'public class ' + class_name + \
                               'RegressionTest{' + '\n'

        new_class_data = """
                                public static void main(String[] args){
                                    junit.textui.TestRunner.run (suite());
                                }

                                // The suite() method is helpful when using JUnit 3 Test Runners or Ant.
                                public static junit.framework.Test suite()
                                {
                                   return new JUnit4TestAdapter(""" + class_name + """RegressionTest.class);
                                }

                            }"""

        with open('RegressionTest.java', 'r') as testRunnerFile:
            for line in testRunnerFile:
                if "class RegressionTest" not in line:
                    if "RegressionTest" in line:
                        line = line.replace('RegressionTest',
                                            class_name + 'RegressionTest')
                    new_file_contents += [line]
                else:
                    break

        new_file_contents += [new_class_descriptor, new_class_data]

        new_file_contents = '\n'.join(new_file_contents)

        with open('RegressionTest.java', 'w') as testRunnerFile:
            testRunnerFile.write(new_file_contents)

        # move this file to relevant directory

        test_file_name = class_name + 'RegressionTest.java'
        test_file_path = '/'.join([test_path, test_file_name])
        if not os.path.exists(test_path):
            os.makedirs(test_path)
        shutil.move('RegressionTest.java', test_file_path)
        list_of_tests += [test_file_path]

        # Now add package name and move all the other RegressionTest files

        for fileName in os.listdir('.'):
            if fnmatch.fnmatch(fileName, 'RegressionTest*.java'):
                package_line = 'package ' + package_name + ';\n'

                with open(fileName, 'r') as test_file:
                    data = test_file.read()
                    data = data.replace('RegressionTest',
                                        class_name + 'RegressionTest')

                with open(fileName, 'w') as test_file:
                    test_file.write(package_line + data)

                new_file_name = class_name + fileName
                test_file_path = '/'.join([test_path, new_file_name])
                shutil.move(fileName, test_file_path)
                list_of_tests += [test_file_path]

        return list_of_tests

    def run(self, package_name, class_name):
        """Run randoop to generate tests."""
        # print self.randoop_jar
        # print self.project_jar
        classpath = ':'.join([self.randoop_jar, self.project_jar])
        randoop_class = 'randoop.main.Main'
        method = 'gentests'
        full_class_name = '.'.join([package_name, class_name])
        cmd_list = ['java', '-classpath', classpath, randoop_class, method,
                    '--testclass=' + full_class_name,
                    '--timelimit=' + str(self.timeout),
                    '--testsperfile=' + str(self.tests_per_file)]
        if self.quiet_mode:
            cmd_list += ['--noprogressdisplay=true']
        # print "Executing the following command:"
        # print ' '.join(cmd_list)

        return call(cmd_list)
