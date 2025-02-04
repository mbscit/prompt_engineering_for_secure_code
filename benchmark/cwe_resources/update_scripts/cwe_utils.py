import os
import sys
import xml.etree.ElementTree as ET

import xmlschema

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import utils

xsd_path = utils.relative_path_from_root('cwe_resources/data/cwe_schema_v7.1.xsd')
xml_path = utils.relative_path_from_root('cwe_resources/data/cwec_v4.14.xml')


def read_cwe_xml():
    schema = xmlschema.XMLSchema(xsd_path)
    if not schema.is_valid(xml_path):
        raise ValueError("XML file is not valid according to the provided XSD schema.")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    namespaces = {'ns': root.tag.split('}')[0].strip('{')}

    return root, namespaces


def read_cwe_xsd():
    tree = ET.parse(xsd_path)
    root = tree.getroot()

    m = root.tag
    namespaces = {'xs': m[m.find("{") + 1:m.rfind("}")]}

    return root, namespaces
