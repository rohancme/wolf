import xml.etree.ElementTree as ET


class PITest(object):

    def __init__(self, pom_path):
        self.pom_path = pom_path

    def insert_into_pom(self, test_package):

        if test_package is None:
            return None

        test_package = test_package + '*'
        ET.register_namespace('', 'http://www.w3.org/2000/svg')

        xml_data = None

        with open(self.pom_path, 'r') as pom_file:
            xml_data = pom_file.read()

        root = ET.XML(xml_data)
        # print root.attrib
        plugins_element = None

        # There needs to be a check here to see if pitest is already included

        for neighb in root.iter():
            if neighb.tag.endswith('plugins'):
                plugins_element = neighb
                break

        if plugins_element is not None:
            plugin_element = ET.SubElement(plugins_element, 'plugin')
            groupid_elem = ET.SubElement(plugin_element, 'groupId')
            groupid_elem.text = 'org.pitest'
            artifactid_elem = ET.SubElement(plugin_element, 'artifactId')
            artifactid_elem.text = 'pitest-maven'
            version_elem = ET.SubElement(plugin_element, 'version')
            version_elem.text = '1.1.2'
            configuration = ET.SubElement(plugin_element, 'configuration')

            threads_elem = ET.SubElement(configuration, 'threads')
            threads_elem.text = '4'
            target_classes = ET.SubElement(configuration, 'targetClasses')
            class_param_elem = ET.SubElement(target_classes, 'param')
            class_param_elem.text = test_package
            target_tests = ET.SubElement(configuration, 'targetTests')
            test_param_elem = ET.SubElement(target_tests, 'param')
            test_param_elem.text = test_package
            reports_dir_elem = ET.SubElement(configuration, 'reportsDirectory')
            reports_dir_elem.text = 'wolf_reports'
            ts_report_elem = ET.SubElement(configuration, 'timestampedReports')
            ts_report_elem.text = 'false'

            export_line_coverage_elem = ET.SubElement(configuration, 'exportLineCoverage')
            export_line_coverage_elem.text = 'true'

        new_data = ET.tostring(root)
        new_data = new_data.replace('ns0:', '')
        new_data = new_data.replace(':ns0', '')

        with open(self.pom_path, 'w') as xml_file:
            xml_file.write(new_data)
