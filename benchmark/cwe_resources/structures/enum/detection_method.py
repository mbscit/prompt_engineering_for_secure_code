from enum import Enum


class DetectionMethodEnumeration(Enum):
    AUTOMATED_ANALYSIS = "Automated Analysis"
    AUTOMATED_DYNAMIC_ANALYSIS = "Automated Dynamic Analysis"
    AUTOMATED_STATIC_ANALYSIS = "Automated Static Analysis"
    AUTOMATED_STATIC_ANALYSIS___SOURCE_CODE = "Automated Static Analysis - Source Code"
    AUTOMATED_STATIC_ANALYSIS___BINARY_OR_BYTECODE = "Automated Static Analysis - Binary or Bytecode"
    FUZZING = "Fuzzing"
    MANUAL_ANALYSIS = "Manual Analysis"
    MANUAL_DYNAMIC_ANALYSIS = "Manual Dynamic Analysis"
    MANUAL_STATIC_ANALYSIS = "Manual Static Analysis"
    MANUAL_STATIC_ANALYSIS___SOURCE_CODE = "Manual Static Analysis - Source Code"
    MANUAL_STATIC_ANALYSIS___BINARY_OR_BYTECODE = "Manual Static Analysis - Binary or Bytecode"
    WHITE_BOX = "White Box"
    BLACK_BOX = "Black Box"
    ARCHITECTURE_OR_DESIGN_REVIEW = "Architecture or Design Review"
    DYNAMIC_ANALYSIS_WITH_MANUAL_RESULTS_INTERPRETATION = "Dynamic Analysis with Manual Results Interpretation"
    DYNAMIC_ANALYSIS_WITH_AUTOMATED_RESULTS_INTERPRETATION = "Dynamic Analysis with Automated Results Interpretation"
    FORMAL_VERIFICATION = "Formal Verification"
    SIMULATION___EMULATION = "Simulation / Emulation"
    OTHER = "Other"
