"""Spaceship (full vessel) prompt generator.

Generates a 2x2 four-view reference sheet prompt for a complete spaceship of a
given archetype (fighter / corvette / frigate / cruiser / battleship / carrier /
freighter / industrial). Reuses ComponentGenerator's layout / view / art style
helpers; defines its own subject description with archetype-driven silhouette
and an optional designer signature.

Carrier archetype is the only class that exposes a modular mecha hangar bay,
which keeps the rest of the fleet decoupled from the mecha system.
"""
import json
import random
from typing import Dict, List, Optional

from paths import resource_path
from . import prompt_generator as pg
from . import mecha_generator as mg


ARCHETYPES_PATH = resource_path("ship_archetypes.json")


def load_archetypes() -> List[Dict]:
    try:
        with open(ARCHETYPES_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return list(data.get("archetypes", []))
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


ARCHETYPES = load_archetypes()
ARCHETYPE_BY_NAME: Dict[str, Dict] = {a["name"]: a for a in ARCHETYPES}


def get_archetype_names() -> List[str]:
    return [a["name"] for a in ARCHETYPES]


def get_archetype(name: str) -> Optional[Dict]:
    return ARCHETYPE_BY_NAME.get(name)


SHIP_VARIANTS = [
    "Standard",
    "Block-II Refit",
    "Civilian Variant",
    "Pirate Conversion",
    "Stealth Variant",
]


def _variant_descriptor(variation: Optional[str]) -> str:
    if not variation or variation == "Standard":
        return ""
    if variation == "Block-II Refit":
        return ("STRUCTURAL VARIANT: Block-II refit — additional bolted-on armor "
                "panels, upgraded sensor mast, visible mid-life modernization seams.")
    if variation == "Civilian Variant":
        return ("STRUCTURAL VARIANT: Civilian conversion — turrets removed or "
                "faired over, additional cargo blisters and viewport rows added, "
                "civilian livery panel layout.")
    if variation == "Pirate Conversion":
        return ("STRUCTURAL VARIANT: Pirate conversion — mismatched salvaged "
                "armor patches, jury-rigged extra weapon mounts welded on, "
                "asymmetric bolt-on hull modifications and exposed cabling.")
    if variation == "Stealth Variant":
        return ("STRUCTURAL VARIANT: Stealth configuration — flush faceted radar-"
                "absorbent paneling, recessed vents, no protruding antennas, "
                "minimal external greebles.")
    return ""


class ShipGenerator(pg.ComponentGenerator):
    def __init__(
        self,
        tier: pg.Tier,
        archetype_name: str,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        manufacturer_data: Optional[Dict] = None,
        variation: Optional[str] = None,
        designers: Optional[List[Dict]] = None,
    ):
        super().__init__(
            tier,
            pg.ComponentType.WEAPON,  # placeholder — overridden in generate_full_prompt
            archetype_name,
            primary_color,
            secondary_color,
            manufacturer_data,
            variation,
        )
        self.designers = designers or []
        self.archetype = get_archetype(archetype_name) or {}

    def _get_ship_negative_prompt(self) -> str:
        base = ("**SHIP-SPECIFIC FORBIDDEN ELEMENTS:**\n"
                "- NO crew figures, NO pilots, NO scale-figure silhouettes next to the ship.\n"
                "- NO planetary background, NO stars, NO nebulae, NO ground terrain — pure white background only.\n"
                "- NO motion lines, NO engine exhaust trails, NO weapon fire effects.\n"
                "- NO panel separator lines or grid borders drawn between the four views.\n"
                "- NO blueprint overlays, NO dimension markings, NO callout arrows.\n"
                "- NO ocean, NO water, NO sea spray, NO waterline — this is a vessel that operates in vacuum, not on a fluid surface.\n"
                "- The command structure is a piece of armored equipment, NOT shaped like an animal or human face — NO face features (eyes, mouth, lips, brows), NO crowning antenna 'horns' arranged like ears, NO viewport patterns shaped like a face.")
        if self.archetype.get("carries_mecha"):
            base += (
                "\n\n**ANTI-FLAT-DECK CARRIER NEGATIVE (CRITICAL — READ CAREFULLY):**\n"
                "This vessel must NOT take the form of a horizontally-flat carrier platform. Specifically forbidden forms:\n"
                "- NO flat horizontal top deck running the length of the hull\n"
                "- NO angled landing deck of any kind\n"
                "- NO ski-jump bow, NO arrestor wires, NO catapult tracks running across a top deck surface\n"
                "- NO offset 'island' superstructure perched on the edge of a flat deck\n"
                "- NO aircraft, jets, planes, helicopters, or piloted machines parked or visible on a top surface\n"
                "- NO vehicles launched from above — all launch operations exit FORWARD out the bow\n"
                "- The overall silhouette must read as a vertically-thick armored hull, NOT a horizontally-flat platform\n"
                "- The command structure is integrated INTO the dorsal hull as a low-profile stepped armored block, NOT perched on top as a separate tower, and NOT shaped like an animal or human head / face\n"
                "Correct form: a vertically-thick armored hull with a longitudinal forward launch channel exiting out the bow, modular hangar sponsons on the flanks, integrated low-profile dorsal command block, and an exposed rear engine framework cradle."
            )
        return base

    def _designer_signature_line(self) -> str:
        if not self.designers:
            return ""
        names = ", ".join(d["name"] for d in self.designers)
        sigs = "  ".join(d.get("signature", "").strip() for d in self.designers if d.get("signature"))
        sigs = sigs.strip()
        line = (f"DESIGNER SIGNATURE — DRIVE THE SILHOUETTE FROM THIS: "
                f"This vessel is designed by {names}, and the entire silhouette, hull "
                f"proportions, bridge tower style, and engine block treatment must follow "
                f"that designer's distinctive visual vocabulary as described below.\n"
                f"Designer vocabulary: {sigs}")
        return line

    def generate_subject_description(self) -> str:
        arche = self.archetype
        tier_data = self.get_tier_data()
        tier_adj = tier_data["adjectives"][0]
        tier_secondary = tier_data["adjectives"][1] if len(tier_data["adjectives"]) > 1 else tier_adj
        design_lang = self._get_design_language()

        role = arche.get("role", "spacecraft")
        silhouette = arche.get("silhouette", "")
        scale_note = arche.get("scale_note", "")
        pool = list(arche.get("features_pool", []))
        features = random.sample(pool, min(4, len(pool))) if pool else []
        feature_prose = "; ".join(features)

        designer_line = self._designer_signature_line()
        variant_line = _variant_descriptor(self.variation)

        carrier_line = ""
        if arche.get("carries_mecha"):
            carrier_line = (
                "CARRIER CONFIGURATION (critical silhouette directive): "
                "This vessel is shaped as a vertically-thick armored hull oriented along its long "
                "axis, NOT as a horizontally-flat platform. The forward third of the hull splits "
                "into a wide longitudinal launch channel running fore-to-aft along the centerline "
                "— the catapult tunnel exits face-first out the bow opening. Two large outboard "
                "hangar sponsons run parallel along the flanks of the hull, attached as modular "
                "bolted-on extensions. The dorsal command block is a low-profile stepped armored "
                "structure integrated FLUSH into the dorsal spine amidships, with horizontal "
                "viewport bands — it is NOT perched on top as a separate tower, NOT shaped like an "
                "animal or human face, and has no facial features (no eyes, mouth, lips, or brow). "
                "The rear is an exposed engine framework "
                "cradle holding multiple large thruster bells. Do NOT draw any piloted machines "
                "inside or around the ship — only the carrier infrastructure itself."
            )

        lines = [
            f"SUBJECT DESCRIPTION ({tier_adj} {role}):",
            (f"This is a complete spaceship — a {tier_secondary} {role}. "
             "The vessel is shown as a clean reference sheet, fully isolated."),
            f"Silhouette: {silhouette}.",
        ]
        if scale_note:
            lines.append(f"Scale: {scale_note}.")
        if designer_line:
            lines.append(designer_line)
        lines.append(f"Design language: {design_lang}")
        if variant_line:
            lines.append(variant_line)
        if carrier_line:
            lines.append(carrier_line)
        if feature_prose:
            lines.append(
                "Visible structural features (drawn as part of the geometry, NOT labeled "
                f"with text): {feature_prose}."
            )
        return "\n".join(lines)

    def generate_full_prompt(self) -> str:
        tier_adj = self.get_tier_data()["adjectives"][0]
        archetype_name = self.archetype.get("name", self.subcategory)

        subject_name = f"{tier_adj} {archetype_name}-class spaceship"
        if self.manufacturer_data:
            subject_name = f"{self.manufacturer_data['name']} {subject_name}"
        if self.variation and self.variation != "Standard":
            subject_name += f" ({self.variation})"
        if self.designers:
            subject_name += f" — designed by {', '.join(d['name'] for d in self.designers)}"

        header = (f"# \n\n`A 2x2 grid illustration (NO TEXT, NO LABELS, NO ARROWS, "
                  f"NO PANEL SEPARATOR LINES) showing 4 views of a {subject_name}.")

        return f"""{header}

{self._get_layout_criteria()}

{self._get_negative_prompt()}

{self._get_ship_negative_prompt()}

{self.generate_subject_description()}

{self._get_view_protocol()}

{self._get_art_style()}`
"""


# --- UI helpers ---

def get_archetype_list() -> List[str]:
    return get_archetype_names()


def get_variant_list() -> List[str]:
    return list(SHIP_VARIANTS)


def get_designer_options(lang: str = "en") -> List[str]:
    """Ships filter the designer pool to ship-capable designers only.
    Capital-ship specialists (Miyatake) and dual-scope designers (Kawamori,
    Ishigaki) appear; pure humanoid-mecha designers are hidden."""
    return mg.get_designer_options(lang, scope="ship")


def get_designer_label_map(lang: str = "en") -> Dict[str, str]:
    return mg.get_designer_label_map(lang, scope="ship")


def generate_ship_prompt_by_strings(
    tier_name: str,
    archetype_name: str,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    manufacturer_name: Optional[str] = None,
    variation_name: Optional[str] = None,
    designer_names: Optional[List[str]] = None,
) -> str:
    try:
        tier = pg.Tier[tier_name]
    except KeyError:
        return "Error: Invalid Tier"

    if archetype_name not in ARCHETYPE_BY_NAME:
        return f"Error: Unknown ship archetype '{archetype_name}'"

    manufacturer_data = None
    if manufacturer_name and manufacturer_name not in (None, "None", "None / Generic"):
        manufacturer_data = pg.get_manufacturer_by_name(manufacturer_name)

    designers = []
    for n in designer_names or []:
        d = mg.get_designer_by_name(n)
        if d:
            designers.append(d)

    gen = ShipGenerator(
        tier=tier,
        archetype_name=archetype_name,
        primary_color=primary_color,
        secondary_color=secondary_color,
        manufacturer_data=manufacturer_data,
        variation=variation_name,
        designers=designers,
    )
    return gen.generate_full_prompt()


if __name__ == "__main__":
    out = generate_ship_prompt_by_strings(
        "TIER_3_MILITARY",
        "Carrier",
        manufacturer_name="Vector Dynamics",
        variation_name="Block-II Refit",
        designer_names=["Kazutaka Miyatake"],
    )
    print(out)
