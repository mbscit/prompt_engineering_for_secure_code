# Secure Prompt Benchmark

This benchmark is intended to evaluate the impact of different prompt strategies on the security of generated code.

The tool is relying on the scanners [Semgrep][4] and [CodeQL][5] to evaluate the security of the generated code.
Due to the limitations of these scanners, the absolute number of vulnerabilities is inaccurate.
The relative difference between techniques is still a good indicator of the effectiveness of the prompt strategy.

The `dataset/benchmark.json` dataset consists of data from LLMSecEval [\[1\]](#1) and SecurityEval [\[2\]](#2).

## Install Requirements

* Install Git LFS: <https://git-lfs.com/>
* Install CodeQL CLI: <https://docs.github.com/code-security/codeql-cli>
* Install semgrep: `python3 -m pip install semgrep`
* For more accurate scan results: `semgrep login`
* Install requirements: `pip install -r requirements.txt`
* Set OpenAI API key: `export OPENAI_API_KEY=<YOURKEY>`

## Attempts

The prompt strategies are implemented in the scripts contained in the `attempts/` directory.  
New prompt strategies can be implemented by using an abstract base class from `attempts/template/`.  
The attempt scripts generate a JSON file in the directory of `DATA_FILE_PATH`, with the same filename as the attempt python script (with the .json ending).  

## Configuration

The configuration is stored in the `.env` file.  

The `DATA_FILE_PATH` is used to point to an attempt json.  
File-based scripts, like `process_one.py` work on this file.  
Directory-based scripts, like `process_all.py` and `compare_attempts.py` ignore the filename, and work on the directory containing the file.  

The `DATASET_FILE_PATH` is used by the attempt scripts as the source for prompts.

The `MODEL_FOR_NEW_ATTEMPTS` is used by the attempt scripts to determine the model used for generating and extracting the response.
Iterative attempt scripts, based on the `AbsIterationAttempt` class, also use the `MODEL_FOR_ITERATIVE_ATTEMPTS` model for prompt enhancements.

The `BATCH_THRESHOLD` is used to determine if the prompt completion and code extraction should be done using the [Batch API][6] (saving 50% of costs, but taking up to 24 Hours) or using the regular Completion API. The quality of the answers is not affected by the Batch API.

`SAMPLES_PER_TASK` is used to determine the number of samples to be generated for each task when running `process_one.py` or `process_all.py`.

## Filter Configuration

The "filtered" metrics are calculated based on the configuration in the `filter_config.py` file.  
These filters are applied to the results of the scanners, and the filtered scan results are stored in the attempt json file under "semgrep_filtered_scanner_report" and "codeql_filtered_scanner_report".  
The filters are re-applied without the need for a re-scan when using the `process_one.py` or `process_all.py` scripts.

## Usage

After ensuring the desired configuration, new attempt json files can be created using the scripts in `attempts/`.
The `process_one.py` script can then be used to generate the code and evaluate it using the scanners.
The `process_all.py` script can be used to generate and evaluate all attempts in a directory sequentially.
The `compare_attempts.py` script is producing a csv file with metrics for all attempts in a directory.

## Functionality Benchmark
Apart from security, the prompt modifications might impact functionality as well. To help evaluate the impact on functionality, the HumanEval dataset [\[3\]](#3) is already converted and ready to use from the file `datasets/HumanEval.json`.
Instructions on how to generate and convert samples are available in `humaneval/README.md`.


## References
<a id="1">[1]</a>
C. Tony, M. Mutas, N. Díaz Ferreyra, and R. Scandariato, "LLMSecEval: A Dataset of Natural Language Prompts for Security Evaluations," in 2023 IEEE/ACM 20th International Conference on Mining Software Repositories (MSR), 2023. DOI: 10.5281/zenodo.7565965. Available: https://github.com/tuhh-softsec/LLMSecEval  
<a id="2">[2]</a>
M. L. Siddiq and J. C. S. Santos, "SecurityEval Dataset: Mining Vulnerability Examples to Evaluate Machine Learning-Based Code Generation Techniques," Proceedings of the 1st International Workshop on Mining Software Repositories Applications for Privacy and Security (MSR4P&S ’22), Nov. 2022, doi: 10.1145/3549035.3561184. Available: https://github.com/s2e-lab/SecurityEval  
<a id="3">[3]</a>
M. Chen, J. Tworek, H. Jun, et al., „Evaluating
large language models trained on code“, ArXiv, vol. abs/2107.03374, 2021. Available: https://api.semanticscholar.org/CorpusID:235755472
<!-- links -->
[4]: https://semgrep.dev/
[5]: https://codeql.github.com/
[6]: https://platform.openai.com/docs/guides/batch
