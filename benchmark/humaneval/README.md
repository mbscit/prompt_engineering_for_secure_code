# HumanEval Usage

To use the HumanEval Benchmark with existing attempt scripts, use the HumanEval dataset, which is already converted and ready to use from the file `datasets/HumanEval.json`.
(Or create you own dataset using the script `create_dataset_from_humaneval.py`)

The only alteration to the prompts is the prefix `Complete the following code, and output the complete program: \n`

### Generating Samples
1. set `DATASET_FILE_PATH` to `datasets/HumanEval/HumanEval.json` in the `.env` file
1. run the desired attempt scripts and process them according to our [usage instructions](../README.md)
1. convert the attempt data files to the format that HumanEval expects using `humaneval_sample_file_from_attempt.py`


### Evaluating Samples
1. install HumanEval using their [instructions](https://github.com/openai/human-eval).
1. copy the resulting `.jsonl` files from the conversion step to the `data` folder in HumanEval
1. evaluate the file with `evaluate_functional_correctness <your-file>.jsonl`
