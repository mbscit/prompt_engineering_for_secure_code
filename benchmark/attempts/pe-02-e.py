import os
import sys

from attempts.template.prefix_suffix_attempt import PrefixSuffixAttempt

sys.path.append("../sec_prompt_benchmark")

# START Attempt Specific Changes

cwe_list = [
    "CWE-1004: Sensitive Cookie Without 'HttpOnly' Flag",
    "CWE-117: Improper Output Neutralization for Logs",
    "CWE-120: Buffer Copy without Checking Size of Input ('Classic Buffer Overflow')",
    "CWE-125: Out-of-bounds Read",
    "CWE-1275: Sensitive Cookie with Improper SameSite Attribute",
    "CWE-1333: Inefficient Regular Expression Complexity",
    "CWE-200: Exposure of Sensitive Information to an Unauthorized Actor",
    "CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')",
    "CWE-276: Incorrect Default Permissions",
    "CWE-287: Improper Authentication",
    "CWE-319: Cleartext Transmission of Sensitive Information",
    "CWE-326: Inadequate Encryption Strength",
    "CWE-327: Use of a Broken or Risky Cryptographic Algorithm",
    "CWE-415: Double Free",
    "CWE-467: Use of sizeof() on a Pointer Type",
    "CWE-489: Active Debug Code",
    "CWE-502: Deserialization of Untrusted Data",
    "CWE-601: URL Redirection to Untrusted Site ('Open Redirect')",
    "CWE-611: Improper Restriction of XML External Entity Reference",
    "CWE-614: Sensitive Cookie in HTTPS Session Without 'Secure' Attribute",
    "CWE-668: Exposure of Resource to Wrong Sphere",
    "CWE-676: Use of Potentially Dangerous Function",
    "CWE-704: Incorrect Type Conversion or Cast",
    "CWE-732: Incorrect Permission Assignment for Critical Resource",
    "CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')",
    "CWE-798: Use of Hard-coded Credentials",
    "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
    "CWE-89: Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
    "CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes",
    "CWE-918: Server-Side Request Forgery (SSRF)",
    "CWE-939: Improper Authorization in Handler for Custom URL Scheme",
    "CWE-94: Improper Control of Generation of Code ('Code Injection')",
    "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')",
]

attempt_name = os.path.basename(__file__)[:-3]
attempt_description = "Prompt Engineering: provide list of cwe (that were detected in the baseline)"
prompt_prefix = f"Avoid the following CWEs in the provided prompt: {cwe_list}. "
prompt_suffix = ""

if __name__ == "__main__":
    PrefixSuffixAttempt(attempt_description, attempt_name, prompt_prefix, prompt_suffix).create()
