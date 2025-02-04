import json
import os
import sys
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import utils
import cwe_utils


def build_detection_method_dict():
    root, namespaces = cwe_utils.read_cwe_xml()
    detection_dict = defaultdict(list)
    weaknesses = root.findall(".//ns:Weakness", namespaces)

    for weakness in weaknesses:
        cwe_id = weakness.get('ID')
        method_xpath = "ns:Detection_Methods/ns:Detection_Method"
        detection_method_elements = weakness.findall(method_xpath, namespaces)
        detection_methods = []
        for detection_method_element in detection_method_elements:
            detection_method = {
                "Method": detection_method_element.find("ns:Method", namespaces).text,
            }
            effectiveness = detection_method_element.find("ns:Effectiveness", namespaces)

            if effectiveness is not None:
                detection_method["Effectiveness"] = effectiveness.text

            detection_methods.append(detection_method)

        detection_dict[cwe_id] = detection_methods

    return detection_dict


def create_detection_methods_structure():
    detection_method_dict = utils.relative_path_from_root('cwe_resources/structures/json/cwe_detection_method.json')

    detections_dict = build_detection_method_dict()

    with open(detection_method_dict, 'w') as f:
        json.dump(detections_dict, f, indent=4)


if __name__ == "__main__":
    create_detection_methods_structure()
