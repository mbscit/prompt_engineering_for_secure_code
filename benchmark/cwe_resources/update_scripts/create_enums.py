import os
import sys

import utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

import cwe_utils


def create_enum_script(enum_name):
    root, namespaces = cwe_utils.read_cwe_xsd()

    # Find the simpleType named DetectionMethodEnumeration
    detection_method_enum = root.find(f".//xs:simpleType[@name='{enum_name}']", namespaces)

    # Extract the enum values
    enum_values = []
    if detection_method_enum is not None:
        for enum in detection_method_enum.findall(".//xs:enumeration", namespaces):
            enum_values.append(enum.get('value'))

    enum_script = f"from enum import Enum\n\n\n" \
                  f"class {enum_name}(Enum):\n"
    for value in enum_values:
        identifier = utils.convert_to_enum_identifier(value)
        enum_script += f"    {identifier} = \"{value}\"\n"
    return enum_script


def save_enum_to_file(enum_script, filename):
    directory = utils.relative_path_from_root('cwe_resources/structures/enum')
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w') as file:
        file.write(enum_script)


def create_enums():
    save_enum_to_file(
        create_enum_script("DetectionMethodEnumeration"),
        "detection_method.py"
    )
    save_enum_to_file(
        create_enum_script("DetectionEffectivenessEnumeration"),
        "detection_effectiveness.py"
    )
    save_enum_to_file(
        create_enum_script("UsageEnumeration"),
        "usage.py"
    )


if __name__ == "__main__":
    create_enums()
