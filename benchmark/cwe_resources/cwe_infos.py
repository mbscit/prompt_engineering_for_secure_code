import json
import sys
from typing import List, Dict

from cwe_resources.structures.enum.detection_effectiveness import DetectionEffectivenessEnumeration
from cwe_resources.structures.enum.detection_information import DetectionInformation
from cwe_resources.structures.enum.detection_method import DetectionMethodEnumeration
from cwe_resources.structures.enum.usage import UsageEnumeration

sys.path.append("../sec_prompt_benchmark")

import utils

# Global variables to cache data
cwe_hierarchy_data = None
cwe_mapping_suggestions_data = None
cwe_can_also_be_data = None
cwe_mapping_usage_data = None
cwe_detection_method_data: Dict[str, List[DetectionInformation]] = {}


def load_data():
    global cwe_hierarchy_data, cwe_mapping_suggestions_data, cwe_can_also_be_data, cwe_mapping_usage_data, cwe_detection_method_data
    cwe_hierarchy_file_path = utils.relative_path_from_root('cwe_resources/structures/json/cwe_hierarchy.json')
    with open(cwe_hierarchy_file_path, 'r') as file:
        cwe_hierarchy_data = json.load(file)

    cwe_mapping_suggestions_file_path = utils.relative_path_from_root(
        'cwe_resources/structures/json/cwe_mapping_suggestions.json')
    with open(cwe_mapping_suggestions_file_path, 'r') as file:
        cwe_mapping_suggestions_data = json.load(file)

    cwe_can_also_be_file_path = utils.relative_path_from_root(
        'cwe_resources/structures/json/cwe_can_also_be.json')
    with open(cwe_can_also_be_file_path, 'r') as file:
        cwe_can_also_be_data = json.load(file)

    cwe_mapping_usage_file_path = utils.relative_path_from_root(
        'cwe_resources/structures/json/cwe_mapping_usage.json')
    with open(cwe_mapping_usage_file_path, 'r') as file:
        cwe_mapping_usage_data = json.load(file)

    cwe_detection_method_file_path = utils.relative_path_from_root(
        'cwe_resources/structures/json/cwe_detection_method.json')
    with open(cwe_detection_method_file_path, 'r') as file:
        json_data = json.load(file)

        for key, entries in json_data.items():
            detection_info_list = []
            for entry in entries:
                method = DetectionMethodEnumeration[utils.convert_to_enum_identifier(entry["Method"])]
                effectiveness = DetectionEffectivenessEnumeration[
                    utils.convert_to_enum_identifier(entry["Effectiveness"])] if "Effectiveness" in entry else None
                detection_info_list.append(DetectionInformation(method, effectiveness))
            cwe_detection_method_data[key] = detection_info_list


load_data()


def find_cwe(data, id, parents=None):
    if parents is None:
        parents = []
    if data['CWE_ID'] == id:
        return data, parents
    for child in data.get('Children', []):
        found, p = find_cwe(child, id, parents + [data['CWE_ID']])
        if found:
            return found, p
    return None, []


def get_descendants(node):
    descendants = []
    for child in node.get('Children', []):
        descendants.append(child['CWE_ID'])
        descendants.extend(get_descendants(child))
    return descendants


def get_related(id):
    id = id.replace("CWE-", "")
    data = cwe_hierarchy_data

    node, parents = find_cwe(data, id)
    if not node:
        return [], [], []

    # Get peers
    if parents:
        parent_id = parents[-1]
        if parent_id != "1000":
            parent_node, _ = find_cwe(data, parent_id)
            peers = [child['CWE_ID'] for child in parent_node.get('Children', []) if child['CWE_ID'] != id]
        else:
            # top-level peers (CWE-1000 research view pillars) are not considered to be peers
            # since they do not share a parent weakness (only a parent view)
            peers = []
    else:
        peers = []

    descendants = get_descendants(node)

    # cwe-1000 is not considered an ancestor, since it is a view, not a weakness
    ancestors = [ancestor for ancestor in parents if ancestor != "1000"]

    return ancestors, peers, descendants


def get_suggested_mappings(id) -> List[str]:
    id = id.replace("CWE-", "")
    data = cwe_mapping_suggestions_data
    try:
        suggested_mapping_ids = data[id]
        suggested_mapping_cwe_ids = [f"CWE-{suggested_mapping_id}" for suggested_mapping_id in suggested_mapping_ids]
    except KeyError:
        return []


    try:
        return suggested_mapping_cwe_ids
    except KeyError:
        return []


def get_can_also_be(id) -> List[str]:
    id = id.replace("CWE-", "")
    data = cwe_can_also_be_data
    try:
        can_also_be_ids = data[id]
        can_also_be_cwe_ids = [f"CWE-{can_also_be_id}" for can_also_be_id in can_also_be_ids]
    except KeyError:
        return []


    try:
        return can_also_be_cwe_ids
    except KeyError:
        return []


def get_mapping_level(id) -> UsageEnumeration:
    id = id.replace("CWE-", "")
    data = cwe_mapping_usage_data

    return UsageEnumeration[data[id]]


def get_detection_methods(id) -> List[DetectionInformation]:
    id = id.replace("CWE-", "")
    data: Dict[str, List[DetectionInformation]] = cwe_detection_method_data
    detection_methods = data.get(id, [])

    return detection_methods
