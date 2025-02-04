from typing import Optional

from cwe_resources.structures.enum.detection_effectiveness import DetectionEffectivenessEnumeration
from cwe_resources.structures.enum.detection_method import DetectionMethodEnumeration


class DetectionInformation:
    method: DetectionMethodEnumeration
    effectiveness: Optional[DetectionEffectivenessEnumeration]

    def __init__(self, method: DetectionMethodEnumeration,
                 effectiveness: Optional[DetectionEffectivenessEnumeration] = None):
        self.method = method
        self.effectiveness = effectiveness
