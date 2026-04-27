"""Spaceship (full vessel) prompt generator.

Generates a 2x2 four-view reference sheet prompt for a complete spaceship of a
given archetype (fighter / corvette / frigate / cruiser / battleship / carrier /
freighter / industrial). Reuses ComponentGenerator's layout / view helpers but
overrides the art style with a 1985-1995 Japanese mecha OVA capital-ship
aesthetic, and injects two universal directives (three-act composition + surface
detail density) that drive the difference between a "toy block" and a real
capital-ship illustration.

Carrier archetype is the only class that exposes a modular mecha hangar bay,
which keeps the rest of the fleet decoupled from the mecha system.
"""
import json
import logging
import os
import random
import sys
from typing import Dict, List, Optional

from paths import resource_path
from . import prompt_generator as pg
from . import mecha_generator as mg


log = logging.getLogger(__name__)

ARCHETYPES_PATH = resource_path("ship_archetypes.json")


def _emit_load_error(msg: str) -> None:
    """Surface a data-load failure on every available channel.

    This runs at import time, BEFORE init_app_logging() configures handlers,
    so we also write directly to stderr — otherwise the failure would be
    silently swallowed and the UI would crash later with a confusing
    `Index 0 out of range` from an empty Combobox.
    """
    log.error(msg)
    try:
        sys.stderr.write("[ship_generator] " + msg + "\n")
        sys.stderr.flush()
    except Exception:
        pass


def _load_data() -> Dict:
    if not os.path.exists(ARCHETYPES_PATH):
        _emit_load_error(
            "ship_archetypes.json NOT FOUND at %s — UI will start with an "
            "empty archetype list. Restore the file from the repo root."
            % ARCHETYPES_PATH
        )
        return {"archetypes": [], "variants": []}
    try:
        with open(ARCHETYPES_PATH, "r", encoding="utf-8-sig") as fh:
            text = fh.read()
    except OSError as e:
        _emit_load_error(
            "Failed to read ship_archetypes.json (%s): %s" % (ARCHETYPES_PATH, e)
        )
        return {"archetypes": [], "variants": []}

    # Use raw_decode so any trailing whitespace or stray bytes after the
    # first complete JSON value are silently ignored. Python 3.14's strict
    # json.load() rejects trailing data, which previously bit this project
    # when an editor saved a stray newline past the closing brace.
    try:
        data, _end = json.JSONDecoder().raw_decode(text.lstrip())
    except json.JSONDecodeError as e:
        _emit_load_error(
            "ship_archetypes.json is not valid JSON (%s): %s" % (ARCHETYPES_PATH, e)
        )
        return {"archetypes": [], "variants": []}

    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"archetypes": data, "variants": []}
    _emit_load_error(
        "ship_archetypes.json has unexpected top-level type %s — expected dict or list"
        % type(data).__name__
    )
    return {"archetypes": [], "variants": []}


def load_archetypes() -> List[Dict]:
    return list(_load_data().get("archetypes", []))


def load_variants() -> List[Dict]:
    return list(_load_data().get("variants", []))


ARCHETYPES = load_archetypes()
if not ARCHETYPES:
    _emit_load_error(
        "ARCHETYPES is empty after load — downstream Combobox.current(0) "
        "calls will fail. Check ship_archetypes.json for parse errors above."
    )
ARCHETYPE_BY_NAME: Dict[str, Dict] = {a["name"]: a for a in ARCHETYPES}

VARIANTS = load_variants()
if not VARIANTS:
    VARIANTS = [
        {"id": "Standard", "name_en": "Standard", "name_zh": "标准型", "descriptor": ""},
    ]

SHIP_VARIANTS: List[str] = [v["id"] for v in VARIANTS]
VARIANT_BY_ID: Dict[str, Dict] = {v["id"]: v for v in VARIANTS}


# --- Archetype helpers ---

def get_archetype_names() -> List[str]:
    return [a["name"] for a in ARCHETYPES]


def get_archetype(name: str) -> Optional[Dict]:
    return ARCHETYPE_BY_NAME.get(name)


def get_archetype_list(lang: str = "en") -> List[str]:
    if lang == "zh":
        return [a.get("name_zh") or a["name"] for a in ARCHETYPES]
    return [a["name"] for a in ARCHETYPES]


def get_archetype_label_map(lang: str = "en") -> Dict[str, str]:
    if lang == "zh":
        return {(a.get("name_zh") or a["name"]): a["name"] for a in ARCHETYPES}
    return {a["name"]: a["name"] for a in ARCHETYPES}


# --- Variant helpers ---

def get_variant_list(lang: str = "en") -> List[str]:
    if lang == "zh":
        return [v.get("name_zh") or v["name_en"] for v in VARIANTS]
    return [v["name_en"] for v in VARIANTS]


def get_variant_label_map(lang: str = "en") -> Dict[str, str]:
    if lang == "zh":
        return {(v.get("name_zh") or v["name_en"]): v["id"] for v in VARIANTS}
    return {v["name_en"]: v["id"] for v in VARIANTS}


def _variant_descriptor(variation_id: Optional[str]) -> str:
    if not variation_id or variation_id == "Standard":
        return ""
    v = VARIANT_BY_ID.get(variation_id)
    return v.get("descriptor", "") if v else ""


# --- Carrier directives (single source of truth) ---

_CARRIER_DIRECTIVE = (
    "CARRIER CONFIGURATION (critical silhouette directive): "
    "vertically-thick armored hull oriented along its long axis. The forward third "
    "splits into a wide longitudinal launch channel running fore-to-aft along the "
    "centerline, exiting face-first out the bow opening. Two outboard hangar sponsons "
    "run parallel along the flanks as modular bolted-on extensions. The dorsal command "
    "block is a low-profile stepped armored structure integrated FLUSH into the dorsal "
    "spine amidships with horizontal viewport bands — NOT a separate tower, NOT shaped "
    "like an animal or human face. The rear is an armored aft engine block — a thick "
    "armored mounting plate housing multiple large thruster bells partially recessed "
    "into the armor, with internal framework only glimpsed through armor cutouts and "
    "access panels (NOT an exposed scaffolding rig). Do NOT draw any piloted machines "
    "inside or around the ship — only the carrier infrastructure itself."
)

_CARRIER_NEGATIVE = (
    "**ANTI-FLAT-DECK CARRIER NEGATIVE (CRITICAL):**\n"
    "This vessel must NOT take the form of a horizontally-flat carrier platform. Forbidden:\n"
    "- NO flat horizontal top deck, NO angled landing deck, NO ski-jump bow\n"
    "- NO arrestor wires, NO catapult tracks running across a top deck surface\n"
    "- NO offset 'island' superstructure perched on the edge of a flat deck\n"
    "- NO aircraft, jets, planes, helicopters, or piloted machines parked on a top surface\n"
    "- NO vehicles launched from above — all launches exit FORWARD out the bow\n"
    "- NO command tower shaped like an animal or human head/face"
)


# --- Universal capital-ship directives ---

_THREE_ACT_COMPOSITION = (
    "THREE-ACT MECHA-DESIGN COMPOSITION (mandatory — this is the load-bearing "
    "structural rule for capital-class vessels):\n"
    "The hull MUST read as three clearly differentiated longitudinal acts along "
    "its long axis, NOT as a single uniform extruded block and NOT as a smooth "
    "tapered cigar shape. Each act must be visually distinct from its neighbors "
    "in silhouette, surface treatment, and detail vocabulary.\n"
    "  Act 1 — FORWARD ATTACK MODULE (front third): an aggressive, visually "
    "pointed, splayed, or chisel-faced prow carrying the heaviest concentration "
    "of weapons, sensors, or launch infrastructure. This act sets the vessel's "
    "'face' and must be the most directional element of the silhouette.\n"
    "  Act 2 — CENTRAL COMMAND CITADEL (middle third): a vertically-stacked, "
    "multi-tier armored superstructure that is visually denser and taller than "
    "the bow or stern, bristling with antenna masts, sensor dishes, and "
    "secondary turrets. This act sets the vessel's 'character' and is the "
    "primary visual focal point.\n"
    "  Act 3 — ARMORED AFT ENGINE BLOCK (back third): a thick armored mounting "
    "plate housing multiple large thruster bells, with the bells PARTIALLY "
    "RECESSED into the armor (NOT hung off open girders, NOT mounted on naked "
    "trusses). Internal structural framework, conduit runs, and engine "
    "greebling are PARTIALLY VISIBLE through armor cutouts, access panels, "
    "and inspection windows — they are glimpsed THROUGH the armor, never "
    "fully exposed on the outside. This act must read as a fortified armored "
    "engine module that conveys raw mechanical power — NOT as an open "
    "scaffolding rig, NOT as an oil-derrick framework, NOT as exposed steel "
    "trusswork."
)

_SURFACE_DENSITY_DIRECTIVE = (
    "SURFACE DETAIL DENSITY (mandatory — this is what separates a capital-ship "
    "illustration from a toy mockup):\n"
    "  - HUNDREDS of small lighted viewports, portholes, and access hatches "
    "scattered densely across the entire hull surface. Each viewport must be "
    "sized as a human-scale crew port — they act as the implicit scale "
    "reference that makes the vessel read as 500 to 2000 meters long.\n"
    "  - Every large armor face MUST be subdivided by visible panel-line work "
    "into smaller sub-panels with clear seam lines and rivet courses — "
    "absolutely NO smooth featureless slab surfaces.\n"
    "  - Antenna mast forests, parabolic dish clusters, and sensor arrays "
    "bristling from the dorsal spine and command citadel.\n"
    "  - Recessed conduit channels, panel seams, and inset cable trays at the "
    "joints between major hull modules — detail lives WITHIN the armor "
    "envelope, NOT as external scaffolding hung off the outside.\n"
    "  - Stenciled hull numbers, painted unit identification markings, and "
    "warning chevron stripes around hatches and weapon mounts, used as accent-"
    "color punctuation against the primary hull tone.\n"
    "  - 'Symmetric base + asymmetric overlay' rule: the primary hull volume "
    "is strictly left/right symmetric, but small bolted-on modules, antenna "
    "mounts, patch panels, and equipment pods are intentionally placed "
    "asymmetrically to give the vessel a lived-in production history rather "
    "than a clean factory-fresh look.\n"
    "  - Hull length-to-height ratio MUST be at least 4:1 — the vessel is a "
    "long capital ship, not a stubby toy block."
)

_OVA_ART_STYLE_HEADER = "ART STYLE (Late-1980s to Mid-1990s Japanese Mecha OVA Capital-Ship Aesthetic):"
_OVA_ART_STYLE_BODY = (
    "Hand-painted anime production cel artwork in the visual tradition of "
    "capital-ship illustration by Kazutaka Miyatake, Shoji Kawamori, and "
    "Junya Ishigaki during the 1985-1995 OVA era. NOT modern 3D rendering, "
    "NOT video-game UI flat shading, NOT chibi or toy aesthetic, NOT "
    "photorealistic.\n"
    "Hard-edged cel-shaded shadow boundaries — one or two flat shadow tones "
    "per surface — combined with subtle airbrushed gradient transitions "
    "within the largest armor faces to give the metal weight and curvature.\n"
    "Bold black ink linework on all silhouette edges; finer ink work for "
    "panel lines, rivet courses, plate seams, and surface greebles. Line "
    "weight varies — heavier on the silhouette, finer on internal detail.\n"
    "Color rhythm (this is the OVA capital-ship signature):\n"
    "  - PRIMARY hull tone (~70% of surface area): warm grey, pale blue-grey, "
    "off-white, or muted olive — the calm dominant color.\n"
    "  - SECONDARY structural tone (~25%): a darker recess color used inside "
    "engine bells, panel recesses, shadow zones beneath overhanging armor, "
    "and within the armor cutouts of the aft engine block.\n"
    "  - ACCENT warning color (~5% — used SPARINGLY): a single saturated red, "
    "orange, or yellow used only for warning stripes, stenciled hull numbers, "
    "hazard chevrons around hatches and weapon mounts, and one or two small "
    "detail callouts. The accent must read as warning paint or unit insignia, "
    "NOT as primary livery."
)
_OVA_ART_STYLE_REMINDER = (
    "REMINDER: Absolutely NO text, NO labels, NO arrows, NO annotations "
    "anywhere in the image. NO modern 3D render aesthetic, NO toy-like "
    "proportions, NO smooth featureless armor faces."
)


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
        # ComponentType is unused by the ship pipeline (generate_full_prompt is
        # fully overridden), but the parent constructor requires a value.
        super().__init__(
            tier,
            pg.ComponentType.WEAPON,
            archetype_name,
            primary_color,
            secondary_color,
            manufacturer_data,
            variation,
        )
        self.designers = designers or []
        self.archetype = get_archetype(archetype_name) or {}

    def _is_capital_class(self) -> bool:
        """Three-act composition + 4:1 length clause apply to anything large
        enough to support a stacked superstructure. Single-pilot fighters are
        excluded since they have no command citadel."""
        return self.archetype.get("id") != "fighter"

    def _get_ship_negative_prompt(self) -> str:
        base = (
            "**SHIP-SPECIFIC FORBIDDEN ELEMENTS:**\n"
            "- NO crew figures, NO pilots, NO scale-figure silhouettes next to the ship.\n"
            "- NO planetary background, NO stars, NO nebulae, NO ground terrain — pure white background only.\n"
            "- NO motion lines, NO engine exhaust trails, NO weapon fire effects.\n"
            "- NO panel separator lines or grid borders drawn between the four views.\n"
            "- NO blueprint overlays, NO dimension markings, NO callout arrows.\n"
            "- NO ocean, NO water, NO sea spray, NO waterline — this is a vessel that operates in vacuum, not on a fluid surface.\n"
            "- The command structure is a piece of armored equipment, NOT shaped like an animal or human face — NO face features (eyes, mouth, lips, brows), NO crowning antenna 'horns' arranged like ears, NO viewport patterns shaped like a face.\n"
            "- NO toy-like proportions, NO chibi shapes, NO smooth featureless armor slabs, NO single-color flat panels, NO sparse uncluttered surfaces — the vessel must read as a dense capital-ship illustration, not as a plastic model or game-asset placeholder.\n"
            "- NO modern photorealistic 3D render aesthetic, NO PBR material shaders, NO ray-traced reflections — this is hand-painted anime cel art.\n"
            "- **ANTI-SCAFFOLDING REAR-ENGINE NEGATIVE (CRITICAL):** the rear engine section must NOT be drawn as an open scaffolding rig, oil-derrick framework, exposed steel trusswork, or skeletal cradle of girders holding the thrusters in space. The thruster bells are PARTIALLY RECESSED into a thick armored aft engine block; framework is only glimpsed THROUGH armor cutouts and access panels, never hung externally on naked beams."
        )
        if self.archetype.get("carries_mecha"):
            base += "\n\n" + _CARRIER_NEGATIVE
        return base

    def _get_three_act_composition(self) -> str:
        return _THREE_ACT_COMPOSITION if self._is_capital_class() else ""

    def _get_surface_density_directive(self) -> str:
        if self._is_capital_class():
            return _SURFACE_DENSITY_DIRECTIVE
        # Strip the 4:1 clause for single-pilot fighters.
        return "\n".join(
            line for line in _SURFACE_DENSITY_DIRECTIVE.splitlines()
            if "length-to-height" not in line and "capital ship" not in line
        )

    def _get_art_style(self) -> str:
        """Ship-specific override of the parent's PC-98 art style. Targets the
        late-1980s to mid-1990s Japanese mecha OVA capital-ship illustration
        idiom rather than retro game UI. Designer names only — no work titles."""
        if self.manufacturer_data:
            palette = self.manufacturer_data["color_palette"]
        elif self.primary_color and self.secondary_color:
            palette = (
                f"{self.primary_color} dominant hull tone, "
                f"{self.secondary_color} accent and warning markings, "
                "dark mechanical recess details."
            )
        else:
            palette = self.get_tier_data()["color_palette"]
        palette_line = f"Color Palette: {palette}"
        return "\n".join([
            _OVA_ART_STYLE_HEADER,
            _OVA_ART_STYLE_BODY,
            palette_line,
            _OVA_ART_STYLE_REMINDER,
        ])

    def _designer_signature_line(self) -> str:
        if not self.designers:
            return ""
        names = ", ".join(d["name"] for d in self.designers)
        sigs = "  ".join(d.get("signature", "").strip() for d in self.designers if d.get("signature"))
        sigs = sigs.strip()
        line = (
            f"DESIGNER SIGNATURE — DRIVE THE SILHOUETTE FROM THIS: "
            f"This vessel is designed by {names}, and the entire silhouette, hull "
            f"proportions, bridge tower style, and engine block treatment must follow "
            f"that designer's distinctive visual vocabulary as described below.\n"
            f"Designer vocabulary: {sigs}"
        )
        return line

    def generate_subject_description(self) -> str:
        arche = self.archetype
        tier_data = self.get_tier_data()
        tier_adj = tier_data["adjectives"][0]
        tier_secondary = tier_data["adjectives"][1] if len(tier_data["adjectives"]) > 1 else tier_adj
        design_lang = self._get_design_language()

        role = arche.get("role", "spacecraft")
        unique_anchor = arche.get("unique_anchor", "")
        silhouette = arche.get("silhouette", "")
        scale_note = arche.get("scale_note", "")
        pool = list(arche.get("features_pool", []))
        features = random.sample(pool, min(4, len(pool))) if pool else []
        feature_prose = "; ".join(features)

        designer_line = self._designer_signature_line()
        variant_line = _variant_descriptor(self.variation)

        lines = [
            f"SUBJECT DESCRIPTION ({tier_adj} {role}):",
            (f"This is a complete spaceship — a {tier_secondary} {role}. "
             "The vessel is shown as a clean reference sheet, fully isolated."),
        ]
        if unique_anchor:
            lines.append(f"Defining visual anchor (must dominate the silhouette): {unique_anchor}.")
        if silhouette:
            lines.append(f"Silhouette: {silhouette}.")
        if scale_note:
            lines.append(f"Scale: {scale_note}.")
        if designer_line:
            lines.append(designer_line)
        lines.append(f"Design language: {design_lang}")
        if variant_line:
            lines.append(variant_line)
        if arche.get("carries_mecha"):
            lines.append(_CARRIER_DIRECTIVE)
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

        header = (
            f"# \n\n`A 2x2 grid illustration (NO TEXT, NO LABELS, NO ARROWS, "
            f"NO PANEL SEPARATOR LINES) showing 4 views of a {subject_name}."
        )

        sections = [
            header,
            self._get_layout_criteria(),
            self._get_negative_prompt(),
            self._get_ship_negative_prompt(),
            self.generate_subject_description(),
            self._get_three_act_composition(),
            self._get_surface_density_directive(),
            self._get_view_protocol(),
            self._get_art_style() + "`",
        ]
        return "\n\n".join(s for s in sections if s) + "\n"


# --- UI helpers ---

def get_designer_options(lang: str = "en") -> List[str]:
    """Filter designer pool to ship-capable designers only."""
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
