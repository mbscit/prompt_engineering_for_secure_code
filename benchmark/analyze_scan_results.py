import ast
import copy
import os
import statistics
import warnings
from typing import List, Callable

from dotenv import load_dotenv

import utils
from filter_config import SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS
from project_types.custom_types import Approach, Task, Sample


def analyze(approach: Approach, semgrep_result_filters: List[Callable[[Task, Sample, dict], bool]] = None,
            codeql_result_filters: List[Callable[[Task, Sample, dict], bool]] = None):
    if semgrep_result_filters is None:
        semgrep_result_filters = []
    if codeql_result_filters is None:
        codeql_result_filters = []
    tasks: List[Task] = approach.tasks

    if not tasks:
        print(f"No tasks in approach {approach.id}")

        approach.semgrep_vulnerable_percentage = 0
        approach.semgrep_filtered_vulnerable_percentage = 0
        approach.semgrep_sample_vulnerable_percentages = []
        approach.semgrep_filtered_sample_vulnerable_percentages = []

        approach.codeql_vulnerable_percentage = 0
        approach.codeql_filtered_vulnerable_percentage = 0
        approach.codeql_sample_vulnerable_percentages = []
        approach.codeql_filtered_sample_vulnerable_percentages = []

        approach.scanners_agree_vulnerable_percentage = 0
        approach.scanners_agree_filtered_vulnerable_percentage = 0
        approach.scanners_agree_non_vulnerable_percentage = 0
        approach.scanners_agree_filtered_non_vulnerable_percentage = 0
        approach.scanners_disagree_percentage = 0
        approach.scanners_disagree_filtered_percentage = 0

        approach.scanners_agree_sample_vulnerable_percentages = []
        approach.scanners_agree_sample_filtered_vulnerable_percentages = []
        approach.scanners_agree_sample_non_vulnerable_percentages = []
        approach.scanners_agree_sample_filtered_non_vulnerable_percentages = []
        approach.scanners_disagree_sample_percentages = []
        approach.scanners_disagree_sample_filtered_percentages = []

        approach.semgrep_average_vulnerabilities_per_sample = 0
        approach.codeql_average_vulnerabilities_per_sample = 0
        approach.scanners_combined_average_vulnerabilities_per_sample = 0

        approach.semgrep_filtered_average_vulnerabilities_per_sample = 0
        approach.codeql_filtered_average_vulnerabilities_per_sample = 0
        approach.scanners_filtered_combined_average_vulnerabilities_per_sample = 0
    else:

        utils.validate_task_integrity(tasks, ["id", "samples"])
        utils.validate_sample_integrity(tasks, ["semgrep_successfully_scanned", "codeql_successfully_scanned"])

        ast_height_sum = 0
        num_syntax_errors = 0
        num_samples_without_complex_code = 0
        for task in tasks:
            # set bool vulnerability_found and filtered_vulnerability_found for each sample
            # and store filtered reports in sample.filtered_scanner_report
            for sample in task.samples:

                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", category=SyntaxWarning)
                        tree = ast.parse(sample.extracted_code)
                        tree_height = utils.get_ast_height(tree)
                        ast_height_sum += tree_height
                        if tree_height < 3:
                            num_samples_without_complex_code += 1
                except SyntaxError:
                    num_syntax_errors += 1

                semgrep_filtered_reports = copy.deepcopy(sample.semgrep_scanner_report)
                for scan_result_filter in semgrep_result_filters:
                    semgrep_filtered_reports = [result for result in semgrep_filtered_reports if
                                                scan_result_filter(task, sample, result)]

                sample.semgrep_filtered_scanner_report = semgrep_filtered_reports

                sample.semgrep_vulnerability_found = len(sample.semgrep_scanner_report) > 0
                sample.semgrep_filtered_vulnerability_found = len(semgrep_filtered_reports) > 0

                codeql_filtered_reports = copy.deepcopy(sample.codeql_scanner_report)
                for scan_result_filter in codeql_result_filters:
                    codeql_filtered_reports = [result for result in codeql_filtered_reports if
                                               scan_result_filter(task, sample, result)]

                sample.codeql_filtered_scanner_report = codeql_filtered_reports

                sample.codeql_vulnerability_found = len(sample.codeql_scanner_report) > 0
                sample.codeql_filtered_vulnerability_found = len(codeql_filtered_reports) > 0

                sample.scanners_agree_vulnerable = False
                sample.scanners_agree_filtered_vulnerable = False
                sample.scanners_agree_non_vulnerable = False
                sample.scanners_agree_filtered_non_vulnerable = False
                sample.scanners_disagree = False
                sample.scanners_filtered_disagree = False
                sample.scanners_combined_vulnerable = False
                sample.scanners_combined_filtered_vulnerable = False

                if sample.codeql_vulnerability_found and sample.semgrep_vulnerability_found:
                    sample.scanners_agree_vulnerable = True
                elif not sample.codeql_vulnerability_found and not sample.semgrep_vulnerability_found:
                    sample.scanners_agree_non_vulnerable = True
                else:
                    sample.scanners_disagree = True

                if sample.codeql_filtered_vulnerability_found and sample.semgrep_filtered_vulnerability_found:
                    sample.scanners_agree_filtered_vulnerable = True
                elif not sample.codeql_filtered_vulnerability_found and not sample.semgrep_filtered_vulnerability_found:
                    sample.scanners_agree_filtered_non_vulnerable = True
                else:
                    sample.scanners_filtered_disagree = True

                if sample.scanners_agree_vulnerable or sample.scanners_disagree:
                    sample.scanners_combined_vulnerable = True
                if sample.scanners_agree_filtered_vulnerable or sample.scanners_filtered_disagree:
                    sample.scanners_combined_filtered_vulnerable = True

            # count vulnerable_samples and filtered_vulnerable_samples for each task
            task.semgrep_vulnerable_samples = len(
                [sample for sample in task.samples if sample.semgrep_vulnerability_found])
            task.semgrep_filtered_vulnerable_samples = len(
                [sample for sample in task.samples if sample.semgrep_filtered_vulnerability_found])

            task.codeql_vulnerable_samples = len(
                [sample for sample in task.samples if sample.codeql_vulnerability_found])
            task.codeql_filtered_vulnerable_samples = len(
                [sample for sample in task.samples if sample.codeql_filtered_vulnerability_found])

            task.scanners_agree_vulnerable = len(
                [sample for sample in task.samples if sample.scanners_agree_vulnerable])
            task.scanners_agree_filtered_vulnerable = len(
                [sample for sample in task.samples if sample.scanners_agree_filtered_vulnerable])

            task.scanners_agree_non_vulnerable = len(
                [sample for sample in task.samples if sample.scanners_agree_non_vulnerable])
            task.scanners_agree_filtered_non_vulnerable = len(
                [sample for sample in task.samples if sample.scanners_agree_filtered_non_vulnerable])

            task.scanners_disagree = len(
                [sample for sample in task.samples if sample.scanners_disagree])
            task.scanners_filtered_disagree = len(
                [sample for sample in task.samples if sample.scanners_filtered_disagree])

            task.scanners_combined_vulnerable = len(
                [sample for sample in task.samples if sample.scanners_combined_vulnerable])
            task.scanners_combined_filtered_vulnerable = len(
                [sample for sample in task.samples if sample.scanners_combined_filtered_vulnerable])

        total_samples = sum(len(task.samples) for task in tasks)

        approach.avg_ast_height = ast_height_sum / (total_samples - num_syntax_errors)
        approach.syntax_error_percentage = (num_syntax_errors / total_samples) * 100 if total_samples > 0 else 0
        approach.samples_with_trivial_code = (num_samples_without_complex_code / total_samples) * 100

        total_semgrep_vulnerable_samples = sum(task.semgrep_vulnerable_samples for task in tasks)
        total_semgrep_filtered_vulnerable_samples = sum(task.semgrep_filtered_vulnerable_samples for task in tasks)

        total_codeql_vulnerable_samples = sum(task.codeql_vulnerable_samples for task in tasks)
        total_codeql_filtered_vulnerable_samples = sum(task.codeql_filtered_vulnerable_samples for task in tasks)

        total_agree_vulnerable_samples = sum(task.scanners_agree_vulnerable for task in tasks)
        total_agree_filtered_vulnerable_samples = sum(task.scanners_agree_filtered_vulnerable for task in tasks)
        total_agree_non_vulnerable_samples = sum(task.scanners_agree_non_vulnerable for task in tasks)
        total_agree_filtered_non_vulnerable_samples = sum(task.scanners_agree_filtered_non_vulnerable for task in tasks)
        total_disagree_samples = sum(task.scanners_disagree for task in tasks)
        total_filtered_disagree_samples = sum(task.scanners_filtered_disagree for task in tasks)
        total_combined_vulnerable_samples = sum(task.scanners_combined_vulnerable for task in tasks)
        total_combined_filtered_vulnerable_samples = sum(task.scanners_combined_filtered_vulnerable for task in tasks)

        approach.semgrep_vulnerable_percentage = (
                                                         total_semgrep_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.semgrep_filtered_vulnerable_percentage = (
                                                                  total_semgrep_filtered_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.codeql_vulnerable_percentage = (
                                                        total_codeql_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.codeql_filtered_vulnerable_percentage = (
                                                                 total_codeql_filtered_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0

        approach.scanners_agree_vulnerable_percentage = (
                                                                total_agree_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.scanners_agree_filtered_vulnerable_percentage = (
                                                                         total_agree_filtered_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0

        approach.scanners_agree_non_vulnerable_percentage = (
                                                                    total_agree_non_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.scanners_agree_filtered_non_vulnerable_percentage = (
                                                                             total_agree_filtered_non_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0

        approach.scanners_disagree_percentage = (
                                                        total_disagree_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.scanners_disagree_filtered_percentage = (
                                                                 total_filtered_disagree_samples / total_samples) * 100 if total_samples > 0 else 0

        approach.scanners_combined_vulnerable_percentage = (
                                                                   total_combined_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0
        approach.scanners_combined_filtered_vulnerable_percentage = (
                                                                            total_combined_filtered_vulnerable_samples / total_samples) * 100 if total_samples > 0 else 0

        semgrep_sample_vulnerable_percentages = []
        semgrep_sample_filtered_vulnerable_percentages = []

        codeql_sample_vulnerable_percentages = []
        codeql_sample_filtered_vulnerable_percentages = []

        scanners_agree_sample_vulnerable_percentages = []
        scanners_agree_sample_filtered_vulnerable_percentages = []
        scanners_agree_sample_non_vulnerable_percentages = []
        scanners_agree_sample_filtered_non_vulnerable_percentages = []
        scanners_disagree_sample_percentages = []
        scanners_disagree_sample_filtered_percentages = []
        scanners_combined_vulnerable_sample_percentages = []
        scanners_combined_filtered_vulnerable_sample_percentages = []

        # assuming samples in all tasks have the same length
        # since validate_sample_integrity checks it
        for i in range(len(tasks[0].samples)):
            # check sample at index i for every task and save result in sample_*_percentages array
            semgrep_vulnerable_samples_at_index = [task.samples[i].semgrep_vulnerability_found for task in tasks]
            semgrep_filtered_vulnerable_samples_at_index = [task.samples[i].semgrep_filtered_vulnerability_found for
                                                            task in
                                                            tasks]
            vulnerable_percentage = (sum(semgrep_vulnerable_samples_at_index) / len(
                semgrep_vulnerable_samples_at_index)) * 100 if semgrep_vulnerable_samples_at_index else 0
            semgrep_filtered_vulnerable_percentage = (sum(semgrep_filtered_vulnerable_samples_at_index) / len(
                semgrep_filtered_vulnerable_samples_at_index)) * 100 if semgrep_filtered_vulnerable_samples_at_index else 0
            semgrep_sample_vulnerable_percentages.append(vulnerable_percentage)
            semgrep_sample_filtered_vulnerable_percentages.append(semgrep_filtered_vulnerable_percentage)

            codeql_vulnerable_samples_at_index = [task.samples[i].codeql_vulnerability_found for task in tasks]
            codeql_filtered_vulnerable_samples_at_index = [task.samples[i].codeql_filtered_vulnerability_found for task
                                                           in
                                                           tasks]
            codeql_vulnerable_percentage = (sum(codeql_vulnerable_samples_at_index) / len(
                codeql_vulnerable_samples_at_index)) * 100 if codeql_vulnerable_samples_at_index else 0
            codeql_filtered_vulnerable_percentage = (sum(codeql_filtered_vulnerable_samples_at_index) / len(
                codeql_filtered_vulnerable_samples_at_index)) * 100 if codeql_filtered_vulnerable_samples_at_index else 0
            codeql_sample_vulnerable_percentages.append(codeql_vulnerable_percentage)
            codeql_sample_filtered_vulnerable_percentages.append(codeql_filtered_vulnerable_percentage)

            scanners_agree_vulnerable_samples_at_index = [task.samples[i].scanners_agree_vulnerable for task in tasks]
            scanners_agree_filtered_vulnerable_samples_at_index = [task.samples[i].scanners_agree_filtered_vulnerable
                                                                   for
                                                                   task in
                                                                   tasks]
            scanners_agree_vulnerable_percentage = (sum(scanners_agree_vulnerable_samples_at_index) / len(
                scanners_agree_vulnerable_samples_at_index)) * 100 if scanners_agree_vulnerable_samples_at_index else 0
            scanners_agree_filtered_vulnerable_percentage = (
                                                                    sum(scanners_agree_filtered_vulnerable_samples_at_index) / len(
                                                                scanners_agree_filtered_vulnerable_samples_at_index)) * 100 if scanners_agree_filtered_vulnerable_samples_at_index else 0
            scanners_agree_sample_vulnerable_percentages.append(scanners_agree_vulnerable_percentage)
            scanners_agree_sample_filtered_vulnerable_percentages.append(scanners_agree_filtered_vulnerable_percentage)

            scanners_agree_non_vulnerable_samples_at_index = [task.samples[i].scanners_agree_non_vulnerable for task in
                                                              tasks]
            scanners_agree_filtered_non_vulnerable_samples_at_index = [
                task.samples[i].scanners_agree_filtered_non_vulnerable
                for task in
                tasks]
            scanners_agree_non_vulnerable_percentage = (sum(scanners_agree_non_vulnerable_samples_at_index) / len(
                scanners_agree_non_vulnerable_samples_at_index)) * 100 if scanners_agree_non_vulnerable_samples_at_index else 0
            scanners_agree_filtered_non_vulnerable_percentage = (
                                                                        sum(scanners_agree_filtered_non_vulnerable_samples_at_index) / len(
                                                                    scanners_agree_filtered_non_vulnerable_samples_at_index)) * 100 if scanners_agree_filtered_non_vulnerable_samples_at_index else 0
            scanners_agree_sample_non_vulnerable_percentages.append(scanners_agree_non_vulnerable_percentage)
            scanners_agree_sample_filtered_non_vulnerable_percentages.append(
                scanners_agree_filtered_non_vulnerable_percentage)

            scanners_disagree_samples_at_index = [task.samples[i].scanners_disagree for task in tasks]
            scanners_disagree_filtered_vulnerable_samples_at_index = [task.samples[i].scanners_filtered_disagree for
                                                                      task in
                                                                      tasks]
            scanners_disagree_sample_percentage = (sum(scanners_disagree_samples_at_index) / len(
                scanners_disagree_samples_at_index)) * 100 if scanners_disagree_samples_at_index else 0
            scanners_disagree_sample_filtered_percentage = (
                                                                   sum(scanners_disagree_filtered_vulnerable_samples_at_index) / len(
                                                               scanners_disagree_filtered_vulnerable_samples_at_index)) * 100 if scanners_disagree_filtered_vulnerable_samples_at_index else 0
            scanners_disagree_sample_percentages.append(scanners_disagree_sample_percentage)
            scanners_disagree_sample_filtered_percentages.append(scanners_disagree_sample_filtered_percentage)

            scanners_combined_vulnerable_samples_at_index = [task.samples[i].scanners_combined_vulnerable for task in
                                                             tasks]
            scanners_combined_vulnerable_filtered_vulnerable_samples_at_index = [
                task.samples[i].scanners_combined_filtered_vulnerable for
                task in
                tasks]
            scanners_combined_vulnerable_sample_percentage = (sum(scanners_combined_vulnerable_samples_at_index) / len(
                scanners_combined_vulnerable_samples_at_index)) * 100 if scanners_combined_vulnerable_samples_at_index else 0
            scanners_combined_vulnerable_sample_filtered_percentage = (
                                                                              sum(scanners_combined_vulnerable_filtered_vulnerable_samples_at_index) / len(
                                                                          scanners_combined_vulnerable_filtered_vulnerable_samples_at_index)) * 100 if scanners_combined_vulnerable_filtered_vulnerable_samples_at_index else 0
            scanners_combined_vulnerable_sample_percentages.append(scanners_combined_vulnerable_sample_percentage)
            scanners_combined_filtered_vulnerable_sample_percentages.append(
                scanners_combined_vulnerable_sample_filtered_percentage)

        approach.semgrep_sample_vulnerable_percentages = semgrep_sample_vulnerable_percentages
        approach.semgrep_filtered_sample_vulnerable_percentages = semgrep_sample_filtered_vulnerable_percentages

        approach.codeql_sample_vulnerable_percentages = codeql_sample_vulnerable_percentages
        approach.codeql_filtered_sample_vulnerable_percentages = codeql_sample_filtered_vulnerable_percentages

        approach.scanners_agree_sample_vulnerable_percentages = scanners_agree_sample_vulnerable_percentages
        approach.scanners_agree_sample_filtered_vulnerable_percentages = scanners_agree_sample_filtered_vulnerable_percentages
        approach.scanners_agree_sample_non_vulnerable_percentages = scanners_agree_sample_non_vulnerable_percentages
        approach.scanners_agree_sample_filtered_non_vulnerable_percentages = scanners_agree_sample_filtered_non_vulnerable_percentages
        approach.scanners_disagree_sample_percentages = scanners_disagree_sample_percentages
        approach.scanners_disagree_sample_filtered_percentages = scanners_disagree_sample_filtered_percentages
        approach.scanners_combined_vulnerable_sample_percentages = scanners_combined_vulnerable_sample_percentages
        approach.scanners_combined_filtered_vulnerable_sample_percentages = scanners_combined_filtered_vulnerable_sample_percentages

        approach.semgrep_average_vulnerabilities_per_sample = sum(
            [len(sample.semgrep_scanner_report) for task in tasks for sample in task.samples]) / sum(
            [len(task.samples) for task in tasks])
        approach.codeql_average_vulnerabilities_per_sample = sum(
            [len(sample.codeql_scanner_report) for task in tasks for sample in task.samples]) / sum(
            [len(task.samples) for task in tasks])

        approach.scanners_combined_average_vulnerabilities_per_sample = sum(
            [(len(sample.semgrep_scanner_report) + len(sample.codeql_scanner_report)) / 2 for task in tasks for sample in
             task.samples]) / sum([len(task.samples) for task in tasks])

        approach.semgrep_filtered_average_vulnerabilities_per_sample = sum(
            [len(sample.semgrep_filtered_scanner_report) for task in tasks for sample in task.samples]) / sum(
            [len(task.samples) for task in tasks])
        approach.codeql_filtered_average_vulnerabilities_per_sample = sum(
            [len(sample.codeql_filtered_scanner_report) for task in tasks for sample in task.samples]) / sum(
            [len(task.samples) for task in tasks])

        approach.scanners_filtered_combined_average_vulnerabilities_per_sample = sum(
            [(len(sample.semgrep_filtered_scanner_report) + len(sample.codeql_filtered_scanner_report)) / 2 for task in tasks for sample in
             task.samples]) / sum([len(task.samples) for task in tasks])

        print("Summary:")

        print()

        print(f"Total Tasks: {len(tasks)}")
        print(f"Total Samples: {total_samples}")
        print(f"Semgrep Vulnerable Samples: {approach.semgrep_vulnerable_percentage:.1f}%")
        print(f"Codeql Vulnerable Samples: {approach.codeql_vulnerable_percentage:.1f}%")
        print(f"Scanners Agree Vulnerable Samples: {approach.scanners_agree_vulnerable_percentage:.1f}%")
        print(f"Scanners Disagree Vulnerable Samples: {approach.scanners_disagree_percentage:.1f}%")
        print(f"Scanners Combined Vulnerable Samples: {approach.scanners_combined_vulnerable_percentage:.1f}%")

        print(f"Codeql Average Vulnerabilities per Sample: {approach.codeql_average_vulnerabilities_per_sample}"),
        print(f"Semgrep Average Vulnerabilities per Sample: {approach.semgrep_average_vulnerabilities_per_sample}"),
        print(
            f"Scanners Combined Average Vulnerabilities per Sample: {approach.scanners_combined_average_vulnerabilities_per_sample}")

        print()
        print(f"Semgrep Filtered Vulnerable Samples: {approach.semgrep_filtered_vulnerable_percentage:.1f}%")
        print(f"Codeql Filtered Vulnerable Samples: {approach.codeql_filtered_vulnerable_percentage:.1f}%")
        print(
            f"Scanners Agree Filtered Vulnerable Samples: {approach.scanners_agree_filtered_vulnerable_percentage:.1f}%")
        print(
            f"Scanners Agree Filtered Vulnerable Samples: {approach.scanners_agree_filtered_vulnerable_percentage:.1f}%")
        print(f"Scanners Disagree Filtered Vulnerable Samples: {approach.scanners_disagree_filtered_percentage:.1f}%")
        print(
            f"Scanners Combined Filtered Vulnerable Samples: {approach.scanners_combined_filtered_vulnerable_percentage:.1f}%")

        print(f"Codeql Filtered Average Vulnerabilities per Sample: {approach.codeql_filtered_average_vulnerabilities_per_sample}"),
        print(f"Semgrep Filtered Average Vulnerabilities per Sample: {approach.semgrep_filtered_average_vulnerabilities_per_sample}"),
        print(
            f"Scanners Filtered Combined Average Vulnerabilities per Sample: {approach.scanners_filtered_combined_average_vulnerabilities_per_sample}")

        print()

        print()

        print("Sample Vulnerable Percentages:")
        print(f"Semgrep Min Vulnerable Percentage: {min(semgrep_sample_vulnerable_percentages):.1f}%")
        print(f"Codeql Min Vulnerable Percentage: {min(codeql_sample_vulnerable_percentages):.1f}%")
        print(f"Scanners Agree Min Vulnerable Percentage: {min(scanners_agree_sample_vulnerable_percentages):.1f}%")
        print(f"Scanners Disagree Min Percentage: {min(scanners_disagree_sample_percentages):.1f}%")
        print(
            f"Scanners Combined Vulnerable Min Percentage: {min(scanners_combined_vulnerable_sample_percentages):.1f}%")
        print()
        print(f"Semgrep Median Vulnerable Percentage: {statistics.median(semgrep_sample_vulnerable_percentages):.1f}%")
        print(f"Codeql Median Vulnerable Percentage: {statistics.median(codeql_sample_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Agree Median Vulnerable Percentage: {statistics.median(scanners_agree_sample_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Disagree Median Percentage: {statistics.median(scanners_disagree_sample_percentages):.1f}%")
        print(
            f"Scanners Combined Median Vulnerable Percentage: {statistics.median(scanners_combined_vulnerable_sample_percentages):.1f}%")
        print()
        print(f"Semgrep Average Vulnerable Percentage: {statistics.mean(semgrep_sample_vulnerable_percentages):.1f}%")
        print(f"Codeql Average Vulnerable Percentage: {statistics.mean(codeql_sample_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Agree Average Vulnerable Percentage: {statistics.mean(scanners_agree_sample_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Disagree Average Percentage: {statistics.mean(scanners_disagree_sample_percentages):.1f}%")
        print(
            f"Scanners Combined Average Vulnerable Percentage: {statistics.mean(scanners_combined_vulnerable_sample_percentages):.1f}%")
        print()
        print(f"Semgrep Max Vulnerable Percentage: {max(semgrep_sample_vulnerable_percentages):.1f}%")
        print(f"Codeql Max Vulnerable Percentage: {max(codeql_sample_vulnerable_percentages):.1f}%")
        print(f"Scanners Agree Max Vulnerable Percentage: {max(scanners_agree_sample_vulnerable_percentages):.1f}%")
        print(f"Scanners Disagree Max Percentage: {max(scanners_disagree_sample_percentages):.1f}%")
        print(
            f"Scanners Combined Max Vulnerable Percentage: {max(scanners_combined_vulnerable_sample_percentages):.1f}%")

        print()
        print()

        print("Filtered Percentages:")
        print(f"Semgrep Min Filtered Percentage: {min(semgrep_sample_filtered_vulnerable_percentages):.1f}%")
        print(f"Codeql Min Filtered Percentage: {min(codeql_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Agree Vulnerable Min Filtered Percentage: {min(scanners_agree_sample_filtered_vulnerable_percentages):.1f}%")
        print(f"Scanners Disagree Min Filtered Percentage: {min(scanners_disagree_sample_filtered_percentages):.1f}%")
        print(
            f"Scanners Combined Vulnerable Min Filtered Percentage: {min(scanners_combined_filtered_vulnerable_sample_percentages):.1f}%")
        print()
        print(
            f"Semgrep Median Filtered Percentage: {statistics.median(semgrep_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Codeql Median Filtered Percentage: {statistics.median(codeql_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Agree Vulnerable Median Filtered Percentage: {statistics.median(scanners_agree_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Disagree Median Filtered Percentage: {statistics.median(scanners_disagree_sample_filtered_percentages):.1f}%")
        print(
            f"Scanners Combined Vulnerable Median Filtered Percentage: {statistics.median(scanners_combined_filtered_vulnerable_sample_percentages):.1f}%")
        print()
        print(
            f"Semgrep Average Filtered Percentage: {statistics.mean(semgrep_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Codeql Average Filtered Percentage: {statistics.mean(codeql_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Agree Average Vulnerable Filtered Percentage: {statistics.mean(scanners_agree_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Disagree Average Filtered Percentage: {statistics.mean(scanners_disagree_sample_filtered_percentages):.1f}%")
        print(
            f"Scanners Combined Vulnerable Average Filtered Percentage: {statistics.mean(scanners_combined_filtered_vulnerable_sample_percentages):.1f}%")
        print()
        print(f"Semgrep Max Filtered Percentage: {max(semgrep_sample_filtered_vulnerable_percentages):.1f}%")
        print(f"Codeql Max Filtered Percentage: {max(codeql_sample_filtered_vulnerable_percentages):.1f}%")
        print(
            f"Scanners Agree Vulnerable Max Filtered Percentage: {max(scanners_agree_sample_filtered_vulnerable_percentages):.1f}%")
        print(f"Scanners Disagree Max Filtered Percentage: {max(scanners_disagree_sample_filtered_percentages):.1f}%")
        print(
            f"Scanners Combined Vulnerable Max Filtered Percentage: {max(scanners_combined_filtered_vulnerable_sample_percentages):.1f}%")

        print()

        print(f"Average AST height {approach.avg_ast_height}")
        print(f"Samples with trivial Code {approach.samples_with_trivial_code}")
        print(f"Samples with Syntax Errors {approach.syntax_error_percentage}")


if __name__ == "__main__":
    load_dotenv()
    data_file_path = utils.relative_path_from_root(os.getenv('DATA_FILE_PATH'))
    approach = utils.read_approaches_file(data_file_path)

    print(f"Analyzing: {data_file_path}")
    print()

    analyze(approach, SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS)

    utils.write_approaches_file(data_file_path, approach)
