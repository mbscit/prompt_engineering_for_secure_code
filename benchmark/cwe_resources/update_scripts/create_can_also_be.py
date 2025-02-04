import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import cwe_utils
import utils


def create_can_also_be_structure():
    usages_file_path = utils.relative_path_from_root('cwe_resources/structures/json/cwe_can_also_be.json')

    root, namespaces = cwe_utils.read_cwe_xml()

    cwe_can_also_be: dict = {}

    for weakness in root.findall("ns:Weaknesses/ns:Weakness", namespaces):
        can_also_be = []
        for related_weakness in weakness.findall("ns:Related_Weaknesses/ns:Related_Weakness", namespaces):
            if (related_weakness.attrib.get('Nature') == 'CanAlsoBe' and related_weakness.attrib.get(
                    'View_ID') == '1000'):
                can_also_be.append(related_weakness.attrib.get('CWE_ID'))

        if can_also_be:
            cwe_can_also_be[weakness.get('ID')] = can_also_be

    print(json.dumps(cwe_can_also_be, indent=4))

    with open(usages_file_path, 'w') as f:
        json.dump(cwe_can_also_be, f, indent=4)


if __name__ == "__main__":
    create_can_also_be_structure()
