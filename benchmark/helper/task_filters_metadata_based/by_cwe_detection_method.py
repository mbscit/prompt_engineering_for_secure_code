import sys
from typing import List

from cwe_resources.cwe_infos import get_mapping_level, get_detection_methods
from cwe_resources.structures.enum.detection_effectiveness import DetectionEffectivenessEnumeration
from cwe_resources.structures.enum.detection_method import DetectionMethodEnumeration
from helper.task_filters_metadata_based.abs_get_prompt_ids_by import GetIDsBy

sys.path.append("../sec_prompt_benchmark")


class ByCWEDetectionMethod(GetIDsBy):

    def __init__(self, allowed_detection_methods: List[DetectionMethodEnumeration], allowed_effectiveness: List[DetectionEffectivenessEnumeration] = []):
        self.allowed_detection_methods = allowed_detection_methods
        self.allowed_effectivenesses = allowed_effectiveness

    def condition(self, prompt) -> bool:
        detection_methods = get_detection_methods(prompt.suspected_vulnerability)
        if self.allowed_effectivenesses:
            return any(detection_method for detection_method in detection_methods if
                       detection_method.method in self.allowed_detection_methods
                       and detection_method.effectiveness in self.allowed_effectivenesses)
        else:
            return any(detection_method for detection_method in detection_methods if
                       detection_method.method in self.allowed_detection_methods)


if __name__ == "__main__":
    ByCWEDetectionMethod(
        [DetectionMethodEnumeration.AUTOMATED_STATIC_ANALYSIS,
         DetectionMethodEnumeration.AUTOMATED_ANALYSIS,
         DetectionMethodEnumeration.AUTOMATED_STATIC_ANALYSIS___SOURCE_CODE
         ], [DetectionEffectivenessEnumeration.HIGH]).filtered_from_dataset(print_ids=True)
