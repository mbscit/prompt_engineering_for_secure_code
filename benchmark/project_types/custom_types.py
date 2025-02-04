from enum import Enum, auto
from typing import List, Optional, Dict

from pydantic import BaseModel


class SampleError(BaseModel):
    task_id: str
    sample_index: int
    error: str

    def __eq__(self, other):
        if isinstance(other, SampleError):
            return (self.task_id == other.task_id and
                    self.sample_index == other.sample_index and
                    self.error == other.error)
        return False

    def __hash__(self):
        return hash((self.task_id, self.sample_index, self.error))


class Sample(BaseModel):
    index: int
    original_prompt: Optional[str] = None
    modified_prompt: Optional[str] = None
    generated_response: Optional[str] = None
    extracted_code: Optional[str] = None
    semgrep_successfully_scanned: Optional[bool] = None
    semgrep_scanner_report: Optional[List[dict]] = None
    semgrep_filtered_scanner_report: Optional[List[dict]] = None
    semgrep_vulnerability_found: Optional[bool] = None
    semgrep_filtered_vulnerability_found: Optional[bool] = None

    codeql_successfully_scanned: Optional[bool] = None
    codeql_scanner_report: Optional[List[dict]] = None
    codeql_filtered_scanner_report: Optional[List[dict]] = None
    codeql_vulnerability_found: Optional[bool] = None
    codeql_filtered_vulnerability_found: Optional[bool] = None

    scanners_agree_vulnerable: Optional[bool] = None
    scanners_agree_filtered_vulnerable: Optional[bool] = None
    scanners_agree_non_vulnerable: Optional[bool] = None
    scanners_agree_filtered_non_vulnerable: Optional[bool] = None
    scanners_disagree: Optional[bool] = None
    scanners_filtered_disagree: Optional[bool] = None
    scanners_combined_vulnerable: Optional[bool] = None # true if one or both scanners found a vulnerability
    scanners_combined_filtered_vulnerable: Optional[bool] = None # true if one or both scanners found a vulnerability (after filtering)


class Task(BaseModel):
    id: str
    original_prompt: str
    modified_prompt: Optional[str] = None
    suspected_vulnerabilities: List[str] | str
    language: str

    semgrep_vulnerable_samples: Optional[int] = None
    semgrep_filtered_vulnerable_samples: Optional[int] = None

    codeql_vulnerable_samples: Optional[int] = None
    codeql_filtered_vulnerable_samples: Optional[int] = None

    scanners_agree_vulnerable: Optional[int] = None
    scanners_agree_filtered_vulnerable: Optional[int] = None
    scanners_agree_filtered_non_vulnerable: Optional[int] = None
    scanners_disagree: Optional[int] = None
    scanners_filtered_disagree: Optional[int] = None
    scanners_agree_non_vulnerable: Optional[int] = None
    scanners_combined_vulnerable: Optional[int] = None
    scanners_combined_filtered_vulnerable: Optional[int] = None

    samples: Optional[List[Sample]] = []


class Approach(BaseModel):
    id: str
    description: str
    model: str

    pending_batch_id: Optional[str] = None
    pending_batch_goal: Optional[str] = None

    errors: Optional[Dict[str, List[SampleError]]] = None

    semgrep_vulnerable_percentage: Optional[float] = None
    semgrep_filtered_vulnerable_percentage: Optional[float] = None
    semgrep_sample_vulnerable_percentages: Optional[List[float]] = None
    semgrep_filtered_sample_vulnerable_percentages: Optional[List[float]] = None

    codeql_vulnerable_percentage: Optional[float] = None
    codeql_filtered_vulnerable_percentage: Optional[float] = None
    codeql_sample_vulnerable_percentages: Optional[List[float]] = None
    codeql_filtered_sample_vulnerable_percentages: Optional[List[float]] = None

    scanners_agree_vulnerable_percentage: Optional[float] = None
    scanners_agree_filtered_vulnerable_percentage: Optional[float] = None
    scanners_agree_non_vulnerable_percentage: Optional[float] = None
    scanners_agree_filtered_non_vulnerable_percentage: Optional[float] = None
    scanners_disagree_percentage: Optional[float] = None
    scanners_disagree_filtered_percentage: Optional[float] = None
    scanners_combined_vulnerable_percentage: Optional[float] = None
    scanners_combined_filtered_vulnerable_percentage: Optional[float] = None

    scanners_agree_sample_vulnerable_percentages: Optional[List[float]] = None
    scanners_agree_sample_filtered_vulnerable_percentages: Optional[List[float]] = None
    scanners_disagree_sample_percentages: Optional[List[float]] = None
    scanners_disagree_sample_filtered_percentages: Optional[List[float]] = None
    scanners_agree_sample_non_vulnerable_percentages: Optional[List[float]] = None
    scanners_agree_sample_filtered_non_vulnerable_percentages: Optional[List[float]] = None
    scanners_combined_vulnerable_sample_percentages: Optional[List[float]] = None
    scanners_combined_filtered_vulnerable_sample_percentages: Optional[List[float]] = None

    semgrep_average_vulnerabilities_per_sample: Optional[float] = None
    codeql_average_vulnerabilities_per_sample: Optional[float] = None
    scanners_combined_average_vulnerabilities_per_sample: Optional[float] = None

    semgrep_filtered_average_vulnerabilities_per_sample: Optional[float] = None
    codeql_filtered_average_vulnerabilities_per_sample: Optional[float] = None
    scanners_filtered_combined_average_vulnerabilities_per_sample: Optional[float] = None

    syntax_error_percentage: Optional[float] = None
    samples_with_trivial_code: Optional[float] = None
    avg_ast_height: Optional[float] = None

    syntax_error_percentage: Optional[float] = None
    samples_without_complex_code_percentage: Optional[float] = None
    avg_ast_height: Optional[float] = None

    tasks: List[Task]

    def update_errors(self, step: str, new_errors: List[SampleError], sample_index: int):
        if self.errors is None:
            self.errors = {}

        if step not in self.errors:
            self.errors[step] = []

        # clear any existing errors for this step and sample index
        self.errors[step] = [error for error in self.errors[step] if error.sample_index != sample_index]

        # add errors from the current run
        if new_errors:
            self.errors[step].extend(new_errors)

        # remove duplicates
        self.errors[step] = list(set(self.errors[step]))


class Prompt(BaseModel):
    id: str
    prompt: str
    suspected_vulnerability: str
    language: str
    source: str
    insecure_example: Optional[str] = None
    secure_example: Optional[str] = None


class SemgrepSeverity(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


class CodeqlProblemSeverity(Enum):
    RECOMMENDATION = auto()
    WARNING = auto()
    ERROR = auto()


class SemgrepConfidence(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class CodeqlPrecision(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()


language_extensions = {
    'python': 'py',
    'Java': 'java',
    'C++': 'cpp',
    'C': 'c'
}
