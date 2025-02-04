import os
import sys

from dotenv import load_dotenv

from filters.codeql_scan_result_filters import CodeqlScanResultFilters

sys.path.append("../sec_prompt_benchmark")

import utils


load_dotenv()
data_folder_path = os.path.dirname(
    utils.relative_path_from_root(os.getenv("DATA_FILE_PATH"))
)

# load all tasks from dataset to a map
reports = {}

for file in os.listdir(data_folder_path):
    data_file_path = os.path.join(data_folder_path, file)
    # checking if it is a file
    if os.path.isfile(data_file_path):
        approach = utils.read_approaches_file(data_file_path)
        for task in approach.tasks:
            for sample in task.samples:
                # remove task if no vulnerability is found / task is not vulnerable
                if len(sample.codeql_scanner_report) > 0:
                    for report in sample.codeql_scanner_report:

                        detected_cwes = CodeqlScanResultFilters.get_detected_cwes(report)
                        for detected_cwe in detected_cwes:
                            if detected_cwe not in reports:
                                reports[detected_cwe] = report
                            reports[detected_cwe]["occurrences"] = (
                                reports[detected_cwe].get("occurrences", 0) + 1
                            )


print(f"Number of different reports: {len(reports)}")
for key in reports:
    print(f'"{reports[key]["occurrences"]}","{key}","' + reports[key]["rule"]["fullDescription"]["text"].replace("\"","\'") + f'"')

