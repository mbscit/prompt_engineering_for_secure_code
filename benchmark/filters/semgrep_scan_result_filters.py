import os
import re
import sys
from typing import Callable, List

from filters.abs_scan_result_filters import AbsScanResultFilters
from project_types.custom_types import Sample, Task, SemgrepSeverity, SemgrepConfidence

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class SemgrepScanResultFilters(AbsScanResultFilters):

    @staticmethod
    def get_detected_cwes(report: dict) -> List[str]:
        cwe_messages: List[str] = []
        if isinstance(report['extra']['metadata']['cwe'], str):
            cwe_messages: List[str] = [report['extra']['metadata']['cwe']]

        if isinstance(report['extra']['metadata']['cwe'], list):
            cwe_messages: List[str] = report['extra']['metadata']['cwe']

        cwe_ids = [re.search(r'CWE-\d+', cwe_message).group() for cwe_message in cwe_messages]
        return cwe_ids

    @staticmethod
    def min_severity(severity: SemgrepSeverity) -> Callable[[Task, Sample, dict], bool]:
        def _min_severity(task: Task, sample: Sample, report: dict):
            return ("extra" in report
                    and "severity" in report["extra"]
                    and SemgrepSeverity[report["extra"]["severity"]].value >= severity.value)

        return _min_severity

    @staticmethod
    def min_confidence(confidence: SemgrepConfidence) -> Callable[[Task, Sample, dict], bool]:
        def _min_confidence(task: Task, sample: Sample, report: dict):
            return ("extra" in report
                    and "metadata" in report["extra"]
                    and "confidence" in report["extra"]["metadata"]
                    and SemgrepConfidence[report["extra"]["metadata"]["confidence"]].value >= confidence.value)

        return _min_confidence

    @staticmethod
    def affected_code_in_generated_response(task: Task, sample: Sample, report: dict) -> bool:
        return (
                "extra" in report
                and "lines" in report["extra"]
                and report["extra"]["lines"].strip() in sample.generated_response)
