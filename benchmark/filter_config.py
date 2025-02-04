from typing import List, Callable

from filters.codeql_scan_result_filters import CodeqlScanResultFilters
from filters.semgrep_scan_result_filters import SemgrepScanResultFilters
from project_types.custom_types import Task, Sample, SemgrepConfidence, SemgrepSeverity, CodeqlPrecision, \
    CodeqlProblemSeverity

SEMGREP_SCAN_RESULT_FILTERS: List[Callable[[Task, Sample, dict], bool]] = [
    # SemgrepScanResultFilters.ignore_cwes(["CWE-489"]), # app.run(debug=True)" is ignored
    # SemgrepScanResultFilters.min_confidence(SemgrepConfidence.MEDIUM),
    # SemgrepScanResultFilters.min_severity(SemgrepSeverity.WARNING),
    # SemgrepScanResultFilters.cwe_relatives_of_suspected(allow_ancestors=False, allow_peers=False, allow_descendants=True),
    # SemgrepScanResultFilters.affected_code_in_generated_response,
    SemgrepScanResultFilters.only_suspected_cwe,
]

CODEQL_SCAN_RESULT_FILTERS: List[Callable[[Task, Sample, dict], bool]] = [
    # CodeqlScanResultFilters.ignore_cwes(["CWE-489"]), # app.run(debug=True)" is ignored
    # CodeqlScanResultFilters.min_precision(CodeqlPrecision.MEDIUM),
    # CodeqlScanResultFilters.min_problem_severity(CodeqlProblemSeverity.WARNING),
    # CodeqlScanResultFilters.min_security_severity(0),
    # CodeqlScanResultFilters.cwe_relatives_of_suspected(allow_ancestors=False, allow_peers=False, allow_descendants=True)
    # codeql_scan_result_filters.affected_code_in_generated_response,
    CodeqlScanResultFilters.only_suspected_cwe,
]
