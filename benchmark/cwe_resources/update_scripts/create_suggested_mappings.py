import json
import os
import sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import utils
import cwe_utils


def build_suggestions_dict():
    root, namespaces = cwe_utils.read_cwe_xml()

    suggestions_dict = defaultdict(list)
    weaknesses = root.findall(".//ns:Weakness", namespaces)

    for weakness in weaknesses:
        cwe_id = weakness.get('ID')
        suggestions_xpath = "ns:Mapping_Notes/ns:Suggestions/ns:Suggestion"
        suggestion_elements = weakness.findall(suggestions_xpath, namespaces)
        if suggestion_elements:
            suggestions_dict[cwe_id] = [suggestion.get('CWE_ID') for suggestion in suggestion_elements if
                                        suggestion.get('CWE_ID')]

    return suggestions_dict


def create_suggested_mappings_structure():
    suggestions_file_path = utils.relative_path_from_root('cwe_resources/structures/json/cwe_mapping_suggestions.json')

    suggestions_dict = build_suggestions_dict()

    with open(suggestions_file_path, 'w') as f:
        json.dump(suggestions_dict, f, indent=4)


if __name__ == "__main__":
    create_suggested_mappings_structure()
