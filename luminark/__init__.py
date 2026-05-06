"""
luminark – LUMINARK Active Governance Layer
Stanfield's Axiom of Perpetuity (SAP) — Production Package

Public API:
    from luminark import SAPGeometry, SAPConstrainedBayesian, SAPEnergy
    from luminark import LyapunovController, NumericalConstitution
    from luminark import SAPPsychiatrist, SAPDiagnosis
    from luminark import LuminarkLiveBridge, ExecutionMode, GovernanceVerdict
    from luminark import Stage8Chamber, Stage5Bifurcation, Stage9Action
    from luminark import VESSEL_OF_GROUNDING_TRAP_AMPLIFIER
"""

from luminark.luminark_live_bridge import (
    ExecutionMode,
    GovernanceResult,
    GovernanceVerdict,
    LuminarkLiveBridge,
)
from luminark.sap_constrained_bayesian import SAPConstrainedBayesian
from luminark.sap_energy import (
    DYNAMO_OF_WILL_ADVANCE_THRESHOLD,
    DYNAMO_OF_WILL_RETREAT_THRESHOLD,
    TRANSPARENCY_DISSOLUTION_ADAPTABILITY_MIN,
    TRANSPARENCY_DISSOLUTION_COHERENCE_MIN,
    TRANSPARENCY_DISSOLUTION_TENSION_MAX,
    VESSEL_OF_GROUNDING_CHAMBER_A,
    VESSEL_OF_GROUNDING_CHAMBER_B,
    VESSEL_OF_GROUNDING_CONSTRUCT,
    VESSEL_OF_GROUNDING_TRAP_AMPLIFIER,
    SAPEnergy,
    SAPEnergyResult,
    Stage5Bifurcation,
    Stage5BifurcationResult,
    Stage8Chamber,
    Stage8TrapResult,
    Stage9Action,
)
from luminark.sap_geometry_engine import (
    ADJACENCY_MATRIX,
    AXIS_SCALES,
    AXIS_WEIGHTS,
    STAGE_CENTROIDS,
    STAGE_METADATA,
    SAPGeometry,
)
from luminark.sap_lyapunov import (
    LyapunovController,
    LyapunovVulnerabilityScanner,
    NumericalConstitution,
    StabilityReport,
)
from luminark.sap_stage_classifier import (
    SAPDiagnosis,
    SAPPsychiatrist,
)

__version__ = "1.0.0"
__author__ = "Richard L. Stanfield"
__org__ = "Meridian Axiom Alignment Technologies (MAAT)"

__all__ = [
    # Geometry
    "SAPGeometry",
    "STAGE_CENTROIDS",
    "STAGE_METADATA",
    "ADJACENCY_MATRIX",
    "AXIS_WEIGHTS",
    "AXIS_SCALES",
    # Bayesian
    "SAPConstrainedBayesian",
    # Energy — canonical sap_energy module
    "SAPEnergy",
    "SAPEnergyResult",
    "Stage8Chamber",
    "Stage8TrapResult",
    "Stage5Bifurcation",
    "Stage5BifurcationResult",
    "Stage9Action",
    "VESSEL_OF_GROUNDING_TRAP_AMPLIFIER",
    "VESSEL_OF_GROUNDING_CHAMBER_A",
    "VESSEL_OF_GROUNDING_CHAMBER_B",
    "VESSEL_OF_GROUNDING_CONSTRUCT",
    "DYNAMO_OF_WILL_ADVANCE_THRESHOLD",
    "DYNAMO_OF_WILL_RETREAT_THRESHOLD",
    "TRANSPARENCY_DISSOLUTION_COHERENCE_MIN",
    "TRANSPARENCY_DISSOLUTION_ADAPTABILITY_MIN",
    "TRANSPARENCY_DISSOLUTION_TENSION_MAX",
    # Lyapunov
    "LyapunovController",
    "LyapunovVulnerabilityScanner",
    "NumericalConstitution",
    "StabilityReport",
    # Psychiatrist
    "SAPPsychiatrist",
    "SAPDiagnosis",
    # Bridge
    "LuminarkLiveBridge",
    "ExecutionMode",
    "GovernanceVerdict",
    "GovernanceResult",
    # Meta
    "__version__",
    "__author__",
    "__org__",
]
