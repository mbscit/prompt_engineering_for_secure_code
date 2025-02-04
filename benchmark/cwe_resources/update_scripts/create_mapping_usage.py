import json
import os
import sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import utils
import cwe_utils


def build_usage_dict():
    root, namespaces = cwe_utils.read_cwe_xml()
    usage_dict = defaultdict(list)
    weaknesses = root.findall(".//ns:Weakness", namespaces)

    for weakness in weaknesses:
        cwe_id = weakness.get('ID')
        usage_xpath = "ns:Mapping_Notes/ns:Usage"
        usage_element = weakness.find(usage_xpath, namespaces)
        if usage_element is not None:
            usage_dict[cwe_id] = usage_element.text.replace("-", "_").upper()

    return usage_dict


def create_mapping_usage_structure():
    usages_file_path = utils.relative_path_from_root('cwe_resources/structures/json/cwe_mapping_usage.json')

    usages_dict = build_usage_dict()

    with open(usages_file_path, 'w') as f:
        json.dump(usages_dict, f, indent=4)


if __name__ == "__main__":
    create_mapping_usage_structure()
