import os
import time

from dotenv import load_dotenv

import utils
from compare_attempts import compare
from filter_config import SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS
from process_one import process_file, BatchInProgressException


def process_all(data_folder_path: str):
    load_dotenv()

    errors = []
    for file in os.listdir(data_folder_path):
        data_file_path = os.path.join(data_folder_path, file)
        # checking if it is a file
        if os.path.isfile(data_file_path):
            print()
            print(f"processing file: {data_file_path}")
            print()
            try:
                process_file(data_file_path, False, SEMGREP_SCAN_RESULT_FILTERS, CODEQL_SCAN_RESULT_FILTERS)
            except BatchInProgressException as e:
                pass
            except Exception as e:
                print(f"Error processing file: {data_file_path}")
                errors.append((data_file_path, e))
                print(e)

    if errors:
        print()
        print("Errors occurred while processing the following files:")
        for error in errors:
            print(error)
        print()


if __name__ == "__main__":
    st = time.time()

    load_dotenv()
    data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))

    process_all(data_folder_path)
    compare(data_folder_path)

    et = time.time()
    print(f"Total execution time: {(et - st):.2f}s")
