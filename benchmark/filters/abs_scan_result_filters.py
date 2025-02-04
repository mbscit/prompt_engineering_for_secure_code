import os
import sys
from abc import abstractmethod
from typing import Callable, List

from project_types.custom_types import Sample, Task

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cwe_resources import cwe_infos


class AbsScanResultFilters:

    @staticmethod
    @abstractmethod
    def get_detected_cwes(report: dict) -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def affected_code_in_generated_response(task: Task, sample: Sample, report: dict) -> bool:
        pass

    @classmethod
    def only_suspected_cwe(cls, task: Task, sample: Sample, report: dict) -> bool:
        return any(suspected_vulnerability for suspected_vulnerability in task.suspected_vulnerabilities if suspected_vulnerability in cls.get_detected_cwes(report))

    @classmethod
    def cwe_relatives_of_suspected(cls, allow_ancestors=True, allow_peers=True, allow_descendants=True) -> Callable[
        [Task, Sample, dict], bool]:
        def _cwe_relatives_of_suspected(task: Task, sample: Sample, report: dict) -> bool:
            suspected_vulnerability_ids = [suspected_vulnerability.replace("CWE-", "") for suspected_vulnerability in task.suspected_vulnerabilities]

            allowed_cwes = []
            for suspected_vulnerability_id in suspected_vulnerability_ids:
                ancestors, peers, descendants = cwe_infos.get_related(suspected_vulnerability_id)
                allowed_cwes += [suspected_vulnerability_id]
                if allow_ancestors:
                    allowed_cwes += ancestors
                if allow_peers:
                    allowed_cwes += peers
                if allow_descendants:
                    allowed_cwes += descendants

            allowed_cwes = [f"CWE-{allowed_cwe}" for allowed_cwe in allowed_cwes]
            return cls.only_allow_cwes(report, allowed_cwes)

        return _cwe_relatives_of_suspected

    @classmethod
    def cwe_in_recommended_mapping(cls, task: Task, sample: Sample, report: dict) -> bool:
        allowed_cwes: List[str] = []
        for suspected_vulnerability in task.suspected_vulnerabilities:
            suggested_mappings = cwe_infos.get_suggested_mappings(suspected_vulnerability)
            allowed_cwes += suggested_mappings + [suspected_vulnerability]
        allowed_cwes = list(set(allowed_cwes))
        return cls.only_allow_cwes(report, allowed_cwes)

    @classmethod
    def cwe_in_can_also_be(cls, task: Task, sample: Sample, report: dict) -> bool:
        can_be: List[str] = []
        for suspected_vulnerability in task.suspected_vulnerabilities:
            can_also_be = cwe_infos.get_can_also_be(suspected_vulnerability)
            can_be += can_also_be + [suspected_vulnerability]
        can_be = list(set(can_be))
        return cls.only_allow_cwes(report, can_be)

    @classmethod
    def only_allow_cwes(cls, report: dict, allowed_cwes):
        found_cwes = cls.get_detected_cwes(report)
        found_cwes = [found_cwe for found_cwe in found_cwes if
                      any(allowed_cwe == found_cwe for allowed_cwe in allowed_cwes)]
        return len(found_cwes) > 0

    @classmethod
    def ignore_cwes(cls, cwes_to_ignore: List[str]) -> Callable[[Task, Sample, dict], bool]:
        def _ignore_cwes(task: Task, sample: Sample, report: dict):
            found_cwes: List[str] = cls.get_detected_cwes(report)
            for ignored_cwe in cwes_to_ignore:
                found_cwes = [cwe for cwe in found_cwes if cwe != ignored_cwe]
            return len(found_cwes) > 0

        return _ignore_cwes
