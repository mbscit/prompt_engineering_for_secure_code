import csv
import logging
import os

import pandas as pd
import tiktoken
from dotenv import load_dotenv

import utils
from helper.cost_estimation.attempt_run_cost_estimation import get_cost_for_model
from project_types.custom_types import Approach


def get_no_tokens(base, result, encoding):
    input_token_sum = sum(len(encoding.encode(
        f"Review the following answer and find security problems with it: \n```\n{sample.extracted_code}\n```")) for
                          task in base.tasks for
                          sample in task.samples)

    output_token_sum = sum(len(encoding.encode(sample.modified_prompt.removeprefix("Based on the critique: \n"))) for
                           task in result.tasks for
                           sample in task.samples)

    output_token_sum -= sum(len(encoding.encode(f"\nimprove the following answer: \n"
                                                f"```\n{sample.extracted_code}\n```")) for
                            task in base.tasks for
                            sample in task.samples)

    return input_token_sum, output_token_sum


def analyze(base: Approach, result: Approach):
    model = "gpt-3.5-turbo-0125"
    encoding = tiktoken.encoding_for_model(model)
    total_3_5_input_tokens, total_3_5_output_tokens = get_no_tokens(base, result, encoding)
    total_3_5_cost = get_cost_for_model(model, total_3_5_input_tokens, total_3_5_output_tokens)

    model = "gpt-4"
    encoding = tiktoken.encoding_for_model(model)
    total_4_input_tokens, total_4_output_tokens = get_no_tokens(base, result, encoding)
    total_4_cost = get_cost_for_model(model, total_4_input_tokens, total_4_output_tokens)

    model = "gpt-4-turbo"
    encoding = tiktoken.encoding_for_model(model)
    total_4_turbo_input_tokens, total_4_turbo_output_tokens = get_no_tokens(base, result, encoding)
    total_4_turbo_cost = get_cost_for_model(model, total_4_turbo_input_tokens, total_4_turbo_output_tokens)

    model = "gpt-4o"
    encoding = tiktoken.encoding_for_model(model)
    total_4o_input_tokens, total_4o_output_tokens = get_no_tokens(base, result, encoding)
    total_4o_cost = get_cost_for_model(model, total_4o_input_tokens, total_4o_output_tokens)

    model = "gpt-4o"
    encoding = tiktoken.encoding_for_model(model)
    total_4o_input_tokens, total_4o_output_tokens = get_no_tokens(base, result, encoding)
    total_4o_cost = get_cost_for_model(model, total_4o_input_tokens, total_4o_output_tokens)

    model = "gpt-4o-2024-08-06"
    total_4o_2024_08_06_cost = get_cost_for_model(model, total_4o_input_tokens, total_4o_output_tokens)

    model = "gpt-4o-mini"
    encoding = tiktoken.encoding_for_model(model)
    total_4o_mini_input_tokens, total_4o_mini_output_tokens = get_no_tokens(base, result, encoding)
    total_4o_mini_cost = get_cost_for_model(model, total_4o_mini_input_tokens, total_4o_mini_output_tokens)

    results = {
        "GPT-3.5-turbo Cost": total_3_5_cost,
        "GPT-4 Cost": total_4_cost,
        "GPT-4-turbo Cost": total_4_turbo_cost,
        "GPT-4o Cost": total_4o_cost,
        "GPT-4o-2024-08-06 Cost": total_4o_2024_08_06_cost,
        "GPT-4o-mini Cost": total_4o_mini_cost,
    }

    print(results)

    return results


if __name__ == "__main__":

    matrix = []




    sort_column = "Filename"
    matrix.sort(key=lambda row: row[sort_column])


    load_dotenv()
    data_folder_path = os.path.dirname(utils.relative_path_from_root(os.getenv("DATA_FILE_PATH")))

    logging.basicConfig(level=logging.INFO)



    base = utils.read_approaches_file(os.path.join(data_folder_path, "intermediate_steps", "ptfscg-zero-shot-cot-step-generation.json"))
    result = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_cot_answer_extraction.json"))
    results = {"Filename": os.path.basename("ptfscg_cot_answer_extraction.json")}
    results.update(analyze(base, result))
    matrix.append(results)

    base = utils.read_approaches_file(os.path.join(data_folder_path, "pe-01-a.json"))
    result = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_rci-from-baseline-iteration-1.json"))
    results = {"Filename": os.path.basename("ptfscg_rci-from-pe-03-a.json")}
    results.update(analyze(base, result))
    matrix.append(results)

    base = utils.read_approaches_file(os.path.join(data_folder_path, "baseline.json"))
    result = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_rci-from-baseline-iteration-1.json"))
    results = {"Filename": os.path.basename("ptfscg_rci-from-baseline-iteration-1.json")}
    results.update(analyze(base, result))
    matrix.append(results)

    base = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_rci-from-baseline-iteration-1.json"))
    result = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_rci-from-baseline-iteration-2.json"))
    results = {"Filename": os.path.basename("ptfscg_rci-from-baseline-iteration-2.json")}
    results.update(analyze(base, result))
    matrix.append(results)

    base = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_rci-from-baseline-iteration-2.json"))
    result = utils.read_approaches_file(os.path.join(data_folder_path, "ptfscg_rci-from-baseline-iteration-3.json"))
    analyze(base, result)
    results = {"Filename": os.path.basename("ptfscg_rci-from-baseline-iteration-3.json")}
    results.update(analyze(base, result))
    matrix.append(results)

    print_matrix = pd.DataFrame.from_records(
        matrix,
        columns=[
            "Filename",
            "GPT-3.5-turbo Cost",
            "GPT-4 Cost",
            "GPT-4-turbo Cost",
            "GPT-4o Cost",
            "GPT-4o-2024-08-06 Cost",
            "GPT-4o-mini Cost"
        ],
    ).to_string(index=False, header=True)

    print(print_matrix)

    with open("rci_creation_cost_estimation.csv", "w+") as output:
        if matrix:
            csvWriter = csv.DictWriter(output, matrix[0].keys(), quoting=csv.QUOTE_ALL)
            csvWriter.writeheader()
            csvWriter.writerows(matrix)