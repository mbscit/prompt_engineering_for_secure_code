import os
import sys

from attempts.template.prefix_suffix_attempt import PrefixSuffixAttempt

sys.path.append("../sec_prompt_benchmark")

attempt_name = os.path.basename(__file__)[:-3]
attempt_description = "Prompt Engineering: request comments"
prompt_prefix = ""
prompt_suffix = " put comments in the code explaining the security measures taken"

if __name__ == "__main__":
    PrefixSuffixAttempt(attempt_description, attempt_name, prompt_prefix, prompt_suffix).create()
