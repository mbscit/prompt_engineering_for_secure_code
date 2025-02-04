import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import cwe_utils
import utils


def build_hierarchy_dict():
    root, namespaces = cwe_utils.read_cwe_xml()

    # Parse the <Views> section to identify the first children of cwe-1000
    view_root_cwe_id = '1000'
    view_element = root.find(f'ns:Views/ns:View[@ID="{view_root_cwe_id}"]', namespaces)
    if view_element is None:
        raise ValueError("View with ID 1000 not found.")

    first_children = []
    for member in view_element.findall('ns:Members/ns:Has_Member', namespaces):
        cwe_id = member.get('CWE_ID')
        first_children.append(cwe_id)

    def build_subtree(cwe_id):
        subtree = {"CWE_ID": cwe_id, "Children": []}
        for weakness in root.findall("ns:Weaknesses/ns:Weakness", namespaces):
            for related_weakness in weakness.findall("ns:Related_Weaknesses/ns:Related_Weakness", namespaces):
                if (related_weakness.attrib.get('Nature') == 'ChildOf' and related_weakness.attrib.get(
                        'View_ID') == '1000' and related_weakness.attrib.get('CWE_ID')) == cwe_id:
                    child_id = weakness.attrib.get('ID')
                    child_subtree = build_subtree(child_id)
                    subtree["Children"].append(child_subtree)
        return subtree

    tree_structure = {"CWE_ID": view_root_cwe_id, "Children": []}
    for child_cwe_id in first_children:
        child_tree = build_subtree(child_cwe_id)
        tree_structure["Children"].append(child_tree)

    print(json.dumps(tree_structure, indent=4))
    return tree_structure


def create_cwe_hierarchy_structure():
    usages_file_path = utils.relative_path_from_root('cwe_resources/structures/json/cwe_hierarchy.json')

    hierarchy = build_hierarchy_dict()

    with open(usages_file_path, 'w') as f:
        json.dump(hierarchy, f, indent=4)


if __name__ == "__main__":
    create_cwe_hierarchy_structure()
