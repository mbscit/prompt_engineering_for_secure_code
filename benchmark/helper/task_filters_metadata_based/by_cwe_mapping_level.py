import logging
import sys
from typing import List

from cwe_resources.cwe_infos import get_mapping_level, get_suggested_mappings
from cwe_resources.structures.enum.usage import UsageEnumeration
from helper.task_filters_metadata_based.abs_get_prompt_ids_by import GetIDsBy
from project_types.custom_types import Prompt

sys.path.append("../sec_prompt_benchmark")


class ByCWEMappingLevel(GetIDsBy):

    def __init__(self, allowed_mapping_levels: List[UsageEnumeration], include_suggested_mappings: bool = False):
        self.allowed_mapping_levels = allowed_mapping_levels
        self.include_suggested_mappings = include_suggested_mappings

    def condition(self, prompt) -> bool:
        if self.include_suggested_mappings:
            mappings = get_suggested_mappings(prompt.suspected_vulnerability)
            mappings.append(prompt.suspected_vulnerability)
            for suggested_mapping in mappings:
                mapping_level = get_mapping_level(suggested_mapping)
                if mapping_level in self.allowed_mapping_levels:
                    return True
        else:
            mapping_level = get_mapping_level(prompt.suspected_vulnerability)
            return mapping_level in self.allowed_mapping_levels


if __name__ == "__main__":
    ByCWEMappingLevel([UsageEnumeration.ALLOWED]).filtered_from_dataset(print_ids=True)
