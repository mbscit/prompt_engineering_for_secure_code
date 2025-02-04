# CWE Resources
This directory contains resources for filters based on CWE (Common Weakness Enumeration) information.

## cwe_infos.py
Provides functions that return specific information about a CWE, such as recommended mappings or related CWEs

## Structures
The files in the structure directory store compacted information about CWEs. \
They are used in cwe_infos.py, since this is faster than parsing the whole XML.

## Data
The data directory contains Version 4.14 of the CWE-1000 research view. \
These files are not used directly, so updating them will require updating the structures. \

## Updating the Structures
When mitre publishes a new version of CWE-1000, cwe-1000.xml can be updated accordingly. \
If there is a new schema version, the path must be updated in `cwe_utils.py` on this line:
```python
    xsd_path = utils.relative_path_from_root('cwe_resources/data/cwe_schema_v7.1.xsd')
```
After inserting the new version of cwe-1000.xml, the structures can be updated by running the following command:
```bash
    python3 update_structures.py
```
