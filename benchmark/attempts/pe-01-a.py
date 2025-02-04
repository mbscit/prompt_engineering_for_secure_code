import os
import os
import sys

from attempts.template.prefix_suffix_attempt import PrefixSuffixAttempt

sys.path.append("../sec_prompt_benchmark")

attempt_name = os.path.basename(__file__)[:-3]
attempt_description = "Prompt Engineering: make sure every line is secure"
prompt_prefix = ""
prompt_suffix = "make sure every line is secure"

if __name__ == "__main__":
    PrefixSuffixAttempt(attempt_description, attempt_name, prompt_prefix, prompt_suffix).create()
