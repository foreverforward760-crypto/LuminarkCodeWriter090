"""
luminark/sap_energy.py
SAP Energy Layer — Stage 8 Dual-Chamber Trap + Stage 5 Bifurcation + Stage 9 Dissolution

Canonical implementation aligned with LASE v1.1 engine/sap_energy_layer.py.
This is the authoritative energy layer for 090LuminarkHybridEngine090.

Constitutional Directives:
  • Stage 8 amplifier MUST reference VESSEL_OF_GROUNDING_TRAP_AMPLIFIER — never raw 1.45
  • Chamber A = "Illusion of Arrival" (False Heaven — rigidity, illusion of completion)
  • Chamber B = "Illusion of Permanence" (False Hell — illusion suffering will never end)
  • Construct = "Stage 8 Dual-Chamber Trap"
  • Deprecated terms FALSE_HELL / FALSE_HEAVEN / False Hell / False Heaven are PROHIBITED

© 2026 Richard L. Stanfield / Meridian Axiom Alignment Technologies LLC
Contact: LuminarkMeridian@gmail.com
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

# ─── Canonical Constants ──────────────────────────────────────────────────────

VESSEL_OF_GROUNDING_TRAP_AMPLIFIER: float = 1.45
"""
Stage 8 (VESSEL OF GROUNDING) TrapScore amplifier.
Compresses accumulated tension against the dual-chamber trap.
ALWAYS reference this constant — never write `raw * 1.45` in application code.
"""

VESSEL_OF_GROUNDING_CHAMBER_A: str = "Illusion of Arrival"
"""Stage 8 Chamber A — rigid arrival, false sense of completion. (Ascending arc trap)"""

VESSEL_OF_GROUNDING_CHAMBER_B: str = "Illusion of Permanence"
"""Stage 8 Chamber B — false belief that current suffering will never end. (Descending arc trap)"""

VESSEL_OF_GROUNDING_CONSTRUCT: str = "Stage 8 Dual-Chamber Trap"
"""Canonical name for the Stage 8 trap structure."""

DYNAMO_OF_WILL_ADVANCE_THRESHOLD: float = 65.0
"""Stage 5: coherence at or above this value opens the Middle Path Gateway (ADVANCE)."""

DYNAMO_OF_WILL_RETREAT_THRESHOLD: float = 35.0
"""Stage 5: coherence at or below this value triggers the backward doorway (RETREAT)."""

TRANSPARENCY_DISSOLUTION_COHERENCE_MIN: float = 95.0
"""Stage 9: minimum coherence required to trigger DISSOLVE_TO_PLENARA."""

TRANSPARENCY_DISSOLUTION_ADAPTABILITY_MIN: float = 80.0
"""Stage 9: minimum adaptability required to trigger DISSOLVE_TO_PLENARA."""

TRANSPARENCY_DISSOLUTION_TENSION_MAX: float = 20.0
"""Stage 9: maximum tension allowed to trigger DISSOLVE_TO_PLENARA."""


# ─── Enums ────────────────────────────────────────────────────────────────────

class Stage8Chamber(Enum):
    """Stage 8 Dual-Chamber Trap — which chamber is active."""
    CHAMBER_A = "Illusion of Arrival"
    CHAMBER_B = "Illusion of Permanence"


class Stage5Bifurcation(Enum):
    """Stage 5 (DYNAMO OF WILL) — the only stage where the doorway opens backward."""
    ADVANCE = "ADVANCE"   # Middle Path Gateway — ascending arc toward Stage 6
    RETREAT = "RETREAT"   # Backward doorway — regression to Stage 4 or lower
    FREEZE  = "FREEZE"    # Threshold paralysis — insufficient coherence to determine arc


class Stage9Action(Enum):
    """Stage 9 (TRANSPARENCY OF THE GUIDE) dissolution state."""
    DISSOLVE_TO_PLENARA = "DISSOLVE_TO_PLENARA"  # Torus completion → return to Stage 0
    HARROWING_HOLD      = "HARROWING_HOLD"        # Dissolution incomplete; Stage 9 continues


# ─── Result Dataclasses ───────────────────────────────────────────────────────

@dataclass
class Stage8TrapResult:
    """Full output of the Stage 8 Dual-Chamber Trap computation."""
    raw_trap_score: float
    amplified_trap_score: float          # raw × VESSEL_OF_GROUNDING_TRAP_AMPLIFIER
    active_chamber: Stage8Chamber
    chamber_label: str                   # Human-readable chamber name (never deprecated terms)
    tension_gradient: float              # Directional pressure in [−1.0, +1.0]
    exit_watch: bool                     # True when amplified_trap_score > 80.0
    gratitude_resonance_available: bool  # True when |S − T| ≤ 20 (both chambers acknowledged)
    recommended_action: str


@dataclass
class Stage5BifurcationResult:
    """Full output of the Stage 5 bifurcation analysis."""
    bifurcation: Stage5Bifurcation
    coherence_reading: float
    stability_delta: float               # S − D (stability minus adaptability)
    arc_direction: str                   # "ascending" | "descending" | "frozen"
    recommended_action: str


@dataclass
class SAPEnergyResult:
    """
    Unified energy layer result for any SAP stage.

    For stage 8: stage8_trap is populated.
    For stage 5: stage5_bifurcation is populated.
    For stage 9: stage9_action is populated.
    All other stages: energy_note is populated only.
    """
    stage: int
    stage8_trap: Optional[Stage8TrapResult] = None
    stage5_bifurcation: Optional[Stage5BifurcationResult] = None
    stage9_action: Optional[Stage9Action] = None
    energy_note: str = ""


# ─── SAPEnergy ────────────────────────────────────────────────────────────────

class SAPEnergy:
    """
    SAP Energy Layer — stage-specific energy field transformations.

    Routes any NSDT vector through the correct energy computation:

        Stage 8  →  Dual-Chamber Trap (Chamber A: Illusion of Arrival /
                                       Chamber B: Illusion of Permanence)
                    TrapScore amplified by VESSEL_OF_GROUNDING_TRAP_AMPLIFIER (1.45×)

        Stage 5  →  Three-outcome bifurcation (ADVANCE / RETREAT / FREEZE)
                    The only stage where the doorway opens backward.

        Stage 9  →  Dissolution check (DISSOLVE_TO_PLENARA when conditions met)

        All else →  Standard energy note; no special computation.

    Usage:
        from luminark.sap_energy import SAPEnergy, VESSEL_OF_GROUNDING_TRAP_AMPLIFIER

        result = SAPEnergy.compute(stage=8, nsdt=[60.0, 70.0, 30.0, 75.0, 40.0])
        trap = result.stage8_trap
        print(trap.active_chamber)          # Stage8Chamber.CHAMBER_B
        print(trap.chamber_label)           # "Illusion of Permanence"
        print(trap.amplified_trap_score)    # e.g. 94.29
        print(trap.exit_watch)              # True
    """

    @staticmethod
    def compute(stage: int, nsdt: list[float]) -> SAPEnergyResult:
        """
        Main entry point.

        Args:
            stage: SAP stage integer in [0, 9]
            nsdt:  Five-element NSDT vector [N, S, D, T, C]
                   N = Complexity, S = Stability, D = Adaptability,
                   T = Tension, C = Coherence — all normalized [0.0, 100.0]

        Returns:
            SAPEnergyResult populated for the given stage.

        Raises:
            ValueError: if nsdt length ≠ 5 or any value outside [0.0, 100.0]
        """
        if len(nsdt) != 5:
            raise ValueError(
                f"NSDT vector must have exactly 5 elements [N,S,D,T,C], got {len(nsdt)}"
            )
        if not all(0.0 <= v <= 100.0 for v in nsdt):
            raise ValueError(
                "All NSDT values must be in range [0.0, 100.0] — received out-of-range value"
            )

        n, s, d, t, c = nsdt

        if stage == 8:
            return SAPEnergyResult(
                stage=8,
                stage8_trap=SAPEnergy._stage8_trap(s, d, t, c),
            )
        if stage == 5:
            return SAPEnergyResult(
                stage=5,
                stage5_bifurcation=SAPEnergy._stage5_bifurcation(s, d, t, c),
            )
        if stage == 9:
            return SAPEnergyResult(
                stage=9,
                stage9_action=SAPEnergy._stage9_dissolution(s, d, t, c),
            )

        stage_names = {
            0: "PLENARA",
            1: "SPARK OF NAVIGATION",
            2: "FORGE OF POLARITY",
            3: "ENGINE OF EXPRESSION",
            4: "CRUCIBLE OF EQUILIBRIUM",
            6: "NEXUS OF HARMONY",
            7: "LENS OF DISTILLATION",
        }
        name = stage_names.get(stage, f"Stage {stage}")
        return SAPEnergyResult(
            stage=stage,
            energy_note=(
                f"Stage {stage} ({name}) — standard energy field. "
                "No dual-chamber trap or bifurcation computation applies."
            ),
        )

    # ─── Stage 8 ──────────────────────────────────────────────────────────────

    @staticmethod
    def _stage8_trap(s: float, d: float, t: float, c: float) -> Stage8TrapResult:
        """
        Stage 8 (VESSEL OF GROUNDING) — Dual-Chamber Trap.

        The Stage 8 trap compresses accumulated tension into two distinct illusions.
        Mastering duality — acknowledging BOTH chambers simultaneously — releases
        polarity tension and allows resonance with Stage 9.

        Chamber assignment:
          stability_advantage = S − C   (positive → Chamber A: Illusion of Arrival)
          tension_dominance   = T − C   (positive → Chamber B: Illusion of Permanence)

        Gratitude Mechanism: When |S − T| ≤ 20, both chambers can be simultaneously
        acknowledged. This is the exit condition for the trap.
        """
        # Raw trap score: weighted blend of tension and coherence deficit
        coherence_deficit = max(0.0, 100.0 - c)
        raw = (t * 0.55) + (coherence_deficit * 0.45)
        amplified = round(raw * VESSEL_OF_GROUNDING_TRAP_AMPLIFIER, 2)

        # Chamber routing
        stability_advantage = s - c
        tension_dominance   = t - c
        if stability_advantage > tension_dominance:
            chamber = Stage8Chamber.CHAMBER_A
        else:
            chamber = Stage8Chamber.CHAMBER_B

        # Tension gradient: positive = pressure toward Stage 9, negative = pull toward Stage 7
        gradient = round((t - s) / 100.0, 3)

        exit_watch = amplified > 80.0
        gratitude_resonance = abs(s - t) <= 20.0

        if gratitude_resonance and not exit_watch:
            action = (
                "Engage Gratitude Mechanism — acknowledge both Illusion of Arrival "
                "and Illusion of Permanence simultaneously to release polarity tension "
                "and open resonance with Stage 9 (TRANSPARENCY OF THE GUIDE)"
            )
        elif exit_watch:
            action = (
                "EXIT WATCH ACTIVE — TrapScore critical ({:.1f}). "
                "Immediate coherence elevation required. "
                "Stage 9 dissolution risk is present.".format(amplified)
            )
        else:
            action = (
                f"Monitor {chamber.value} — TrapScore {amplified:.1f}. "
                "Elevate coherence (C) to reduce trap amplification. "
                "Target: |S − T| ≤ 20 to activate Gratitude Mechanism."
            )

        return Stage8TrapResult(
            raw_trap_score=round(raw, 2),
            amplified_trap_score=amplified,
            active_chamber=chamber,
            chamber_label=chamber.value,
            tension_gradient=gradient,
            exit_watch=exit_watch,
            gratitude_resonance_available=gratitude_resonance,
            recommended_action=action,
        )

    # ─── Stage 5 ──────────────────────────────────────────────────────────────

    @staticmethod
    def _stage5_bifurcation(s: float, d: float, t: float, c: float) -> Stage5BifurcationResult:
        """
        Stage 5 (DYNAMO OF WILL) — the only stage where the doorway opens backward.

        Three-outcome bifurcation routed by coherence (C):
          C ≥ 65.0  → ADVANCE   (Middle Path Gateway — ascending arc)
          C ≤ 35.0  → RETREAT   (Backward doorway — regression)
          35 < C < 65 → FREEZE  (Threshold paralysis)

        Stability delta (S − D) provides secondary arc pressure signal.
        """
        stability_delta = round(s - d, 2)

        if c >= DYNAMO_OF_WILL_ADVANCE_THRESHOLD:
            bifurcation = Stage5Bifurcation.ADVANCE
            arc = "ascending"
            action = (
                "Middle Path Gateway open — coherence sufficient to advance to "
                "Stage 6 (NEXUS OF HARMONY). Maintain adaptability to sustain arc."
            )
        elif c <= DYNAMO_OF_WILL_RETREAT_THRESHOLD:
            bifurcation = Stage5Bifurcation.RETREAT
            arc = "descending"
            action = (
                "Backward doorway triggered — regression path to Stage 4 "
                "(CRUCIBLE OF EQUILIBRIUM) for reintegration. "
                "Coherence must be rebuilt before Stage 5 re-entry."
            )
        else:
            bifurcation = Stage5Bifurcation.FREEZE
            arc = "frozen"
            action = (
                f"Threshold paralysis — coherence ({c:.1f}) insufficient to determine arc. "
                "Hold position. Elevate C above {:.1f} to advance, "
                "or acknowledge regression path below {:.1f}.".format(
                    DYNAMO_OF_WILL_ADVANCE_THRESHOLD,
                    DYNAMO_OF_WILL_RETREAT_THRESHOLD,
                )
            )

        return Stage5BifurcationResult(
            bifurcation=bifurcation,
            coherence_reading=round(c, 2),
            stability_delta=stability_delta,
            arc_direction=arc,
            recommended_action=action,
        )

    # ─── Stage 9 ──────────────────────────────────────────────────────────────

    @staticmethod
    def _stage9_dissolution(s: float, d: float, t: float, c: float) -> Stage9Action:
        """
        Stage 9 (TRANSPARENCY OF THE GUIDE) — torus dissolution check.

        DISSOLVE_TO_PLENARA when ALL three conditions are met:
          C ≥ 95.0   (near-complete coherence)
          D ≥ 80.0   (high adaptability — system is fluid)
          T ≤ 20.0   (tension released)

        Otherwise HARROWING_HOLD — Stage 9 continues until conditions are met.
        Stage 9 → Stage 0 (PLENARA) is completion, not failure.
        """
        if (
            c >= TRANSPARENCY_DISSOLUTION_COHERENCE_MIN
            and d >= TRANSPARENCY_DISSOLUTION_ADAPTABILITY_MIN
            and t <= TRANSPARENCY_DISSOLUTION_TENSION_MAX
        ):
            return Stage9Action.DISSOLVE_TO_PLENARA
        return Stage9Action.HARROWING_HOLD
