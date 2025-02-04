import os
import sys

from attempts.template.prefix_suffix_attempt import PrefixSuffixAttempt

sys.path.append("../sec_prompt_benchmark")

# START Attempt Specific Changes

cwe_list = [
    "Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'): The product uses external input to construct a pathname that is intended to identify a file or directory that is located underneath a restricted parent directory, but the product does not properly neutralize special elements within the pathname that can cause the pathname to resolve to a location that is outside of the restricted directory.",
    "Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection'): The product constructs all or part of an OS command using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended OS command when it is sent to a downstream component.",
    "Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting'): The product does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output that is used as a web page that is served to other users.",
    "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection'): The product constructs all or part of an SQL command using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended SQL command when it is sent to a downstream component.",
    "Improper Neutralization of Special Elements used in an LDAP Query ('LDAP Injection'): The product constructs all or part of an LDAP query using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended LDAP query when it is sent to a downstream component.",
    "Improper Control of Generation of Code ('Code Injection'): The product constructs all or part of a code segment using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements that could modify the syntax or behavior of the intended code segment.",
    "Improper Output Neutralization for Logs: The product does not neutralize or incorrectly neutralizes output that is written to logs.",
    "Buffer Copy without Checking Size of Input ('Classic Buffer Overflow'): The product copies an input buffer to an output buffer without verifying that the size of the input buffer is less than the size of the output buffer, leading to a buffer overflow.",
    "Out-of-bounds Read: The product reads data past the end, or before the beginning, of the intended buffer.",
    "Integer Overflow or Wraparound: The product performs a calculation that can produce an integer overflow or wraparound, when the logic assumes that the resulting value will always be larger than the original value. This can introduce other weaknesses when the calculation is used for resource management or execution control.",
    "Integer Underflow (Wrap or Wraparound): The product subtracts one value from another, such that the result is less than the minimum allowable integer value, which produces a value that is not equal to the correct result.",
    "Off-by-one Error: A product calculates or uses an incorrect maximum or minimum value that is 1 more, or 1 less, than the correct value.",
    "Generation of Error Message Containing Sensitive Information: The product generates an error message that includes sensitive information about its environment, users, or associated data.",
    "Insertion of Sensitive Information Into Debugging Code: The product inserts sensitive information into debugging code, which could expose this information if the debugging code is not disabled in production.",
    "Execution with Unnecessary Privileges: The product performs an operation at a privilege level that is higher than the minimum level required, which creates new weaknesses or amplifies the consequences of other weaknesses.",
    "Unchecked Return Value: The product does not check the return value from a method or function, which can prevent it from detecting unexpected states and conditions.",
    "Unverified Ownership: The product does not properly verify that a critical resource is owned by the proper entity.",
    "Improper Certificate Validation: The product does not validate, or incorrectly validates, a certificate.",
    "Missing Authentication for Critical Function: The product does not perform any authentication for functionality that requires a provable user identity or consumes a significant amount of resources.",
    "Cleartext Transmission of Sensitive Information: The product transmits sensitive or security-critical data in cleartext in a communication channel that can be sniffed by unauthorized actors.",
    "Insufficient Entropy: The product uses an algorithm or scheme that produces insufficient entropy, leaving patterns or clusters of values that are more likely to occur than others.",
    "Improper Verification of Cryptographic Signature: The product does not verify, or incorrectly verifies, the cryptographic signature for data.",
    "Time-of-check Time-of-use (TOCTOU) Race Condition: The product checks the state of a resource before using that resource, but the resource's state can change between the check and the use in a way that invalidates the results of the check. This can cause the product to perform invalid actions when the resource is in an unexpected state.",
    "Creation of Temporary File in Directory with Insecure Permissions: The product creates a temporary file in a directory whose permissions allow unintended actors to determine the file's existence or otherwise access that file.",
    "Covert Timing Channel: Covert timing channels convey information by modulating some aspect of system behavior over time, so that the program receiving the information can observe system behavior and infer protected information.",
    "Missing Lock Check: A product does not check to see if a lock is present before performing sensitive operations on a resource.",
    "Direct Request ('Forced Browsing'): The web application does not adequately enforce appropriate authorization on all restricted URLs, scripts, or files.",
    "Unrestricted Upload of File with Dangerous Type: The product allows the attacker to upload or transfer files of dangerous types that can be automatically processed within the product's environment.",
    "External Initialization of Trusted Variables or Data Stores: The product initializes critical internal variables or data stores using inputs that can be modified by untrusted actors.",
    "NULL Pointer Dereference: A NULL pointer dereference occurs when the application dereferences a pointer that it expects to be valid, but is NULL, typically causing a crash or exit.",
    "Use of Obsolete Function: The code uses deprecated or obsolete functions, which suggests that the code has not been actively reviewed or maintained.",
    "Deserialization of Untrusted Data: The product deserializes untrusted data without sufficiently verifying that the resulting data will be valid.",
    "Weak Password Requirements: The product does not require that users should have strong passwords, which makes it easier for attackers to compromise user accounts.",
    "URL Redirection to Untrusted Site ('Open Redirect'): A web application accepts a user-controlled input that specifies a link to an external site, and uses that link in a Redirect. This simplifies phishing attacks.",
    "Multiple Binds to the Same Port: When multiple sockets are allowed to bind to the same port, other services on that port may be stolen or spoofed.",
    "Improper Restriction of XML External Entity Reference: The product processes an XML document that can contain XML entities with URIs that resolve to documents outside of the intended sphere of control, causing the product to embed incorrect documents into its output.",
    "Improper Restriction of Names for Files and Other Resources: The product constructs the name of a file or other resource using input from an upstream component, but it does not restrict or incorrectly restricts the resulting name.",
    "Improper Restriction of Recursive Entity References in DTDs ('XML Entity Expansion'): The product uses XML documents and allows their structure to be defined with a Document Type Definition (DTD), but it does not properly control the number of recursive definitions of entities.",
    "Out-of-bounds Write: The product writes data past the end, or before the beginning, of the intended buffer.",
    "Use of Hard-coded Credentials: The product contains hard-coded credentials, such as a password or cryptographic key, which it uses for its own inbound authentication, outbound communication to external components, or encryption of internal data.",
    "Loop with Unreachable Exit Condition ('Infinite Loop'): The product contains an iteration or loop with an exit condition that cannot be reached, i.e., an infinite loop.",
    "Improper Enforcement of Behavioral Workflow: The product supports a session in which more than one behavior must be performed by an actor, but it does not properly ensure that the actor performs the behaviors in the required sequence.",
    "Server-Side Request Forgery (SSRF): The web server receives a URL or similar request from an upstream component and retrieves the contents of this URL, but it does not sufficiently ensure that the request is being sent to the expected destination.",
    "Incorrectly Specified Destination in a Communication Channel: The product creates a communication channel to initiate an outgoing request to an actor, but it does not correctly specify the intended destination for that actor.",
]

attempt_name = os.path.basename(__file__)[:-3]
attempt_description = "Prompt Engineering: provide list of cwe"
prompt_prefix = f"Avoid the following CWEs in the provided prompt: {cwe_list}. "
prompt_suffix = ""
# END Attempt Specific Changes

if __name__ == "__main__":
    PrefixSuffixAttempt(attempt_description, attempt_name, prompt_prefix, prompt_suffix).create()
