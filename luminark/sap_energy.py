"""
luminark/sap_energy.py — CodeWriter re-export shim
────────────────────────────────────────────────────
All SAP energy layer symbols are sourced from the canonical luminark package
(LASE v1.1+). This module re-exports them so existing CodeWriter internal
imports of the form `from luminark.sap_energy import ...` continue to work
without modification.

To update constants or logic, edit:
    LASE repo → core/luminark/sap_energy_layer.py

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC
"""

# Re-export everything from the canonical source
from luminark.sap_energy_layer import (
    SAPStage,
    VESSEL_OF_GROUNDING_TRAP_AMPLIFIER,
    VESSEL_OF_GROUNDING_CHAMBER_A,
    VESSEL_OF_GROUNDING_CHAMBER_B,
    VESSEL_OF_GROUNDING_CONSTRUCT,
    TRAP_ENERGY_NONE,
    TRAP_ENERGY_LOW,
    TRAP_ENERGY_MODERATE,
    TRAP_ENERGY_HIGH,
    TRAP_ENERGY_MAXIMUM,
    Stage8TrapResult,
    Stage5BifurcationResult,
    EvaluationResult,
    evaluate_vessel_of_grounding_trap,
    evaluate_dynamo_of_will_bifurcation,
    trap_energy,
    evaluate_trap,
)

# Legacy aliases — preserved for any CodeWriter internal code that used
# the old sap_energy.py names from the HybridEngine session
SAPEnergyResult    = EvaluationResult   # unified result type
Stage8Chamber      = None               # deprecated — use chamber_active field
Stage5Bifurcation  = None               # deprecated — use path field
Stage9Action       = None               # deprecated — use evaluate_trap(stage=9)

__all__ = [
    "SAPStage",
    "VESSEL_OF_GROUNDING_TRAP_AMPLIFIER",
    "VESSEL_OF_GROUNDING_CHAMBER_A",
    "VESSEL_OF_GROUNDING_CHAMBER_B",
    "VESSEL_OF_GROUNDING_CONSTRUCT",
    "TRAP_ENERGY_NONE",
    "TRAP_ENERGY_LOW",
    "TRAP_ENERGY_MODERATE",
    "TRAP_ENERGY_HIGH",
    "TRAP_ENERGY_MAXIMUM",
    "Stage8TrapResult",
    "Stage5BifurcationResult",
    "EvaluationResult",
    "SAPEnergyResult",
    "evaluate_vessel_of_grounding_trap",
    "evaluate_dynamo_of_will_bifurcation",
    "trap_energy",
    "evaluate_trap",
]
