"""The TestReducer class."""
import shutil
import fnmatch
from lxml import etree
from bs4 import BeautifulSoup
import os
import sys


class TestReducer(object):
    """Class responsible for all test reduction functionality."""

    def __init__(self, test_files, mvn_runner):
        """Initialize the object."""
        with open(test_files, 'r') as test_files_f:
            data = test_files_f.read()
        self.file_list = data.split('\n')
        self.mvn_runner = mvn_runner

    def parse_html_table(self, bs_table):
        """Parse an html table and return a list of k-v pairs."""

        table_str = str(bs_table)
        table_str = table_str.replace('\n', '')
        table_str = table_str.replace('<thead>', '')
        table_str = table_str.replace('</thead>', '')
        table_str = table_str.replace('<tbody>', '')
        table_str = table_str.replace('</tbody>', '')

        list_of_dicts = []
        s = """""" + table_str
        table = etree.XML(s)
        rows = iter(table)
        headers = [col.text for col in next(rows)]

        for row in rows:
            values = []

            for td in row:
                value = td.text
                print value
                for bar_div in td:
                    for div in bar_div:
                        if div.text is not None:
                            value = div.text
                values += [value]
            list_of_dicts += [dict(zip(headers, values))]

        return list_of_dicts

    def get_coverage(self, coverage_file):

        with open(coverage_file, 'r') as html_file:
            data = html_file.read()
        soup = BeautifulSoup(data)
        table = soup.find('table')
        stats = self.parse_html_table(table)[0]
        if 'Number of Classes' in stats:
            stats.pop('Number of Classes')

        if 'Line Coverage' in stats:
            lc_str = stats['Line Coverage']
            nums = lc_str.split('/')
            stats['Line Coverage'] = float(nums[0]) / float(nums[1])

        if 'Mutation Coverage' in stats:
            mc_str = stats['Mutation Coverage']
            nums = mc_str.split('/')
            stats['Mutation Coverage'] = float(nums[0]) / float(nums[1])

        return stats

    def reduce(self):
        """Reduce the number of tests by evaluating coverage stats."""
        coverage_file = '/'.join([self.mvn_runner.dir, 'wolf_reports',
                                  'index.html'])
        coverage_stats = self.get_coverage(coverage_file)
        orig_mc = coverage_stats['Mutation Coverage']
        orig_lc = coverage_stats['Line Coverage']

        groups = self._group_tests()
        # updated_groups = {}
        init_num_tests = 0
        final_num_tests = sys.maxint
        for prefix in groups:
            # Get a list of performers
            # tests = groups[prefix]
            tests_obj = self._cull_non_perf(prefix=prefix,
                                            orig_mc=orig_mc, orig_lc=orig_lc)
            print "Initial: " + str(tests_obj['init_tests'])
            print "Final: " + str(tests_obj['final_tests'])
            init_num_tests = max(init_num_tests, tests_obj['init_tests'])
            final_num_tests = min(final_num_tests, tests_obj['final_tests'])
            # updated_groups[prefix] = perf_list
        print "Tests Reduced: " + str(init_num_tests) + " -> " + str(final_num_tests)
        return None

    def _cull_non_perf(self, prefix, orig_mc, orig_lc, test_list=None):
        main_class_path = prefix + 'RegressionTest.java'
        main_class_file_name = main_class_path.rsplit('/', 1)[1]
        main_class_name = main_class_file_name.replace('.java', '.class')

        with open(main_class_path, 'r') as main_test_file:
            contents = main_test_file.read()

        shutil.move(main_class_path, main_class_path + '.orig')

        new_contents_top = []
        new_contents_bottom = []

        inner_test_flag = False
        bottom_flag = False
        inner_class_list = []
        for line in contents.splitlines():
            if inner_test_flag or bottom_flag:
                if not bottom_flag and '.class' in line:
                    print "Inside if"
                    print line
                    inner_class_list += [line.rsplit(',')[0]]
                elif line:
                    print "Else" + str(bottom_flag)
                    print line
                    bottom_flag = True
                    new_contents_bottom += [line]
                    # print line
                continue
            if line:
                new_contents_top += [line]
            if "@Suite.SuiteClasses({" in line:
                inner_test_flag = True

        non_perf = []
        coverage_file = '/'.join([self.mvn_runner.dir, 'wolf_reports',
                                  'index.html'])

        package_name = new_contents_top[0]
        package_name = package_name.replace('package ', '')
        package_name = package_name.replace(';', '')
        package_path = package_name.replace('.', '/') + '/'
        gen_class_dir = self.mvn_runner.dir + '/target/test-classes/' + package_path

        print "cycling through inner classes:"
        print inner_class_list
        improvement_classes = []
        max_mc = orig_mc
        max_lc = orig_lc
        for class_name in inner_class_list:

            current_class_list = improvement_classes + [class_name]

            classes_string = ',\n'.join(current_class_list)

            new_test_file = '\n'.join(new_contents_top +
                                      [classes_string] +
                                      new_contents_bottom)
            print new_test_file
            with open(main_class_path, 'w') as main_class_file:
                main_class_file.write(new_test_file)
            print main_class_file_name
            self.mvn_runner.clean()
            test_output = self.mvn_runner.test()

            # Get the number of tests
            init_num_tests = self._extract_num_tests(test_output)

            # Delete all other classes except one under test
            print gen_class_dir
            for file_d in os.listdir(gen_class_dir):
                if os.path.isfile(gen_class_dir + '/' + str(file_d)):
                    del_flag = True
                    if fnmatch.fnmatch(file_d, '*' + main_class_name):
                        print "continue-1"
                        del_flag = False
                    elif fnmatch.fnmatch(file_d, '*' + class_name):
                        print "continue-2"
                        del_flag = False
                    else:
                        for class_n in current_class_list:
                            if fnmatch.fnmatch(file_d, '*' + class_n):
                                print "continue-3"
                                del_flag = False
                                break
                    if del_flag and fnmatch.fnmatch(file_d, '*RegressionTest*'):
                        print "Deleting:" + str(file_d)
                        os.remove(gen_class_dir + '/' + file_d)

            self.mvn_runner.custom('org.pitest:pitest-maven:mutationCoverage')
            coverage_stats = self.get_coverage(coverage_file)
            mc = coverage_stats['Mutation Coverage']
            lc = coverage_stats['Line Coverage']
            if mc <= max_mc and lc <= max_lc:
                non_perf += [class_name.rsplit('.class')[0]]
                print class_name.rsplit('.class')[0] + " did not improve coverage"
                print "MC:" + str(mc)
                print "LC:" + str(lc)
            else:
                improvement_classes += [class_name]
                print class_name.rsplit('.class')[0] + " improved coverage"
                max_mc = mc
                max_lc = lc

        # shutil.move(main_class_path + '.orig', main_class_path)

        classes_string = ',\n'.join(improvement_classes)

        new_test_file = '\n'.join(new_contents_top +
                                  [classes_string] +
                                  new_contents_bottom)
        print "***********FINAL OUTPUT FILE*******"
        print new_test_file
        with open(main_class_path, 'w') as main_class_file:
            main_class_file.write(new_test_file)

        test_path = main_class_path.rsplit('/', 1)[0]

        for class_n in non_perf:
            full_class_path = test_path + '/' + class_n + '.java'
            print 'Deleting: ' + full_class_path
            os.remove(full_class_path)

        self.mvn_runner.clean()
        test_output = self.mvn_runner.test()
        # Get the number of tests
        final_num_tests = self._extract_num_tests(test_output)

        return_obj = {}
        return_obj['lc'] = max_lc
        return_obj['mc'] = max_mc
        return_obj['init_tests'] = init_num_tests
        return_obj['final_tests'] = final_num_tests

        return return_obj

    def _extract_num_tests(self, mvn_output):
        last_test_line = None
        for line in mvn_output.split('\n'):
            if 'Tests run' in line:
                last_test_line = line

        num_tests = 0
        if last_test_line is not None:
            last_test_line = last_test_line.rsplit(': ')[1]
            num_tests = int(last_test_line.split(',')[0])
        return num_tests

    def _generate_test_class(self, class_name):

        contents = """public class """ + class_name + """{


                                public static void main(String[] args){
                                    junit.textui.TestRunner.run (suite());
                                }

                                // The suite() method is helpful when using JUnit 3 Test Runners or Ant.
                                public static junit.framework.Test suite()
                                {
                                   return new JUnit4TestAdapter(""" + class_name + """.class);
                                }

                            }"""
        return contents

    def _group_tests(self):
        """Group tests by File under test."""
        groups = {}

        for test_file in self.file_list:
            if 'RegressionTest.java' in test_file:
                prefix = test_file[:-len('RegressionTest.java')]
                groups[prefix] = []

        for test_file in self.file_list:
            for prefix in groups:
                if prefix in test_file:
                    groups[prefix] += [test_file]

        print groups
        return groups
