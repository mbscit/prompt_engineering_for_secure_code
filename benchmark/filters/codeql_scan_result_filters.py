import math
import re
from abc import ABC
from typing import Callable, List

import utils
from filters.abs_scan_result_filters import AbsScanResultFilters
from project_types.custom_types import Sample, Task, CodeqlPrecision, CodeqlProblemSeverity


class CodeqlScanResultFilters(AbsScanResultFilters):

    @staticmethod
    def get_detected_cwes(report: dict) -> List[str]:
        tags = report['rule']['properties']['tags']
        cwe_tags = [re.sub(r'CWE-0+', 'CWE-', tag.replace('external/cwe/cwe-', 'CWE-')) for tag in tags if
                tag.startswith('external/cwe/cwe-')]
        return cwe_tags

    @staticmethod
    def extract_region(file_content, region):
        # Split the file content into lines
        lines = file_content.splitlines()

        # Extract the specific line based on startLine (indexing starts from 0, hence subtract 1)
        target_line = lines[region["startLine"] - 1]

        # Determine the start column, defaulting to 1 if not provided
        start_column = region.get("startColumn", 1) - 1  # Convert to 0-based index
        end_column = region["endColumn"]

        # Extract the substring from the line based on startColumn and endColumn
        extracted_string = target_line[start_column:end_column]

        return extracted_string

    @staticmethod
    def min_problem_severity(severity: CodeqlProblemSeverity) -> Callable[[Task, Sample, dict], bool]:
        def _min_problem_severity(task: Task, sample: Sample, report: dict):
            actual_problem_severity = report['rule']['properties']['problem.severity']
            actual_severity_enum = CodeqlProblemSeverity[utils.convert_to_enum_identifier(actual_problem_severity)]
            return actual_severity_enum.value >= severity.value

        return _min_problem_severity

    @staticmethod
    def min_security_severity(severity: float) -> Callable[[Task, Sample, dict], bool]:
        assert 0 <= severity <= 10, "Security severity must be between 0 and 10"

        def _min_problem_severity(task: Task, sample: Sample, report: dict):
            actual_security_severity = report['rule']['properties']['security-severity']
            actual_security_severity_float = float(actual_security_severity)
            return actual_security_severity_float > severity or math.isclose(actual_security_severity_float, severity,
                                                                             abs_tol=1e-9, rel_tol=1e-9)

        return _min_problem_severity

    @staticmethod
    def min_precision(precision: CodeqlPrecision) -> Callable[[Task, Sample, dict], bool]:
        def _min_precision(task: Task, sample: Sample, report: dict):
            actual_precision = report['rule']['properties']['precision']
            actual_precision_enum = CodeqlPrecision[utils.convert_to_enum_identifier(actual_precision)]
            return actual_precision_enum.value >= precision.value

        return _min_precision

    @staticmethod
    def affected_code_in_generated_response(task: Task, sample: Sample, report: dict) -> bool:
        locations = report['locations']
        for location in locations:
            affected_code = CodeqlScanResultFilters.extract_region(sample.extracted_code,
                                                                   location['physicalLocation']['region'])
            if affected_code in sample.generated_response:
                return True
        return False
