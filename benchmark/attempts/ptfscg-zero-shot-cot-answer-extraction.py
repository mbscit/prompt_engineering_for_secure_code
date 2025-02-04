import sys

from attempts.template.ptfscg_cot_answer_extraction import CoTAnswerExtraction

sys.path.append("../sec_prompt_benchmark")

if __name__ == "__main__":
    CoTAnswerExtraction("data/benchmark/3.5/ptfscg-zero-shot-cot-step-generation.json").create()
