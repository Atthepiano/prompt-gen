"""Mecha-mounted equipment / parts generator.

Generates a 2x2 four-view reference sheet prompt for an individual piece of
mecha equipment (hand-held weapon, shield, shoulder-mounted weapon, etc.).
Mirrors core.prompt_generator.WeaponGenerator (the ship-mounted weapon flow)
but the subject is sized for a humanoid mecha and mounted via a hand grip,
forearm clamp, or shoulder hardpoint instead of a hull bracket.

Currently only weapons / shields are implemented. The category set is fixed
(two-handed, one-handed, one-hand shield, shoulder-mounted) per the game's
slot model; structural variants per category mirror the ship-weapon variants.
"""
import random
from typing import Dict, List, Optional

from . import prompt_generator as pg
from .prompt_generator import (
    Tier,
    ComponentGenerator,
    ComponentType,
    TIER_DESCRIPTORS,
    get_manufacturer_by_name,
)


# Mecha-equipment subcategories (mount type drives silhouette).
# key, en label, zh label
MECHA_PART_SUBCATEGORIES: List[tuple] = [
    ("TwoHand",  "Two-Handed Weapon",      "双手武器"),
    ("OneHand",  "One-Handed Weapon",      "单手武器"),
    ("Shield",   "One-Hand Shield",        "单手盾"),
    ("Shoulder", "Shoulder-Mounted Weapon", "肩部武器"),
]


# Structural variants per subcategory (form-factor choices).
# Mirrors ship WEAPON_VARIANTS in spirit. key, en label, zh label.
MECHA_PART_VARIANTS: Dict[str, List[tuple]] = {
    "TwoHand": [
        ("Standard",     "Standard Rifle",       "标准步枪"),
        ("LongBarrel",   "Long-Barrel (Sniper)", "长管（狙击）"),
        ("Bazooka",      "Bazooka (Rocket)",     "火箭筒"),
        ("BeamRifle",    "Beam Rifle",           "光束步枪"),
        ("BeamCannon",   "Beam Cannon (Heavy)",  "光束加农（重型）"),
        ("Gatling",      "Gatling (Rotary)",     "加特林（转管）"),
    ],
    "OneHand": [
        ("Standard",     "Standard Pistol",      "标准手枪"),
        ("MachinePistol","Machine Pistol",       "冲锋手枪"),
        ("BeamPistol",   "Beam Pistol",          "光束手枪"),
        ("BeamSaber",    "Beam Saber (Melee)",   "光束军刀（近战）"),
        ("HeatBlade",    "Heat Blade (Melee)",   "热能短剑（近战）"),
        ("Tomahawk",     "Tomahawk Axe (Melee)", "战斧（近战）"),
    ],
    "Shield": [
        ("Standard",     "Standard Plate Shield", "标准板盾"),
        ("Tower",        "Tower Shield (Heavy)",  "塔盾（重型）"),
        ("Buckler",      "Buckler (Light)",       "圆盾（轻型）"),
        ("BeamShield",   "Beam Shield (Emitter)", "光束护盾（发射型）"),
        ("ArmedShield",  "Armed Shield (Built-in Gun)", "武装盾（内置炮）"),
    ],
    "Shoulder": [
        ("Standard",     "Standard Missile Pod",  "标准导弹荚舱"),
        ("VLS",          "VLS Cluster",           "垂直发射阵列"),
        ("BeamCannon",   "Shoulder Beam Cannon",  "肩载光束炮"),
        ("Gatling",      "Shoulder Gatling",      "肩载加特林"),
        ("BinderClaw",   "Binder Claw (Folding)", "折叠绑定爪"),
    ],
}


# ---- Bilingual label helpers ----

_SUBCAT_KEY_TO_LABELS = {k: {"en": en, "zh": zh} for (k, en, zh) in MECHA_PART_SUBCATEGORIES}


def _label(entry_zh_en: tuple, lang: str) -> str:
    """entry_zh_en is (key, en, zh). Return bilingual display label.
    EN mode: 'Two-Handed Weapon'. ZH mode: '双手武器 (Two-Handed Weapon)'."""
    _key, en, zh = entry_zh_en
    if lang == "zh":
        return f"{zh} ({en})" if en and en != zh else zh
    return en


def get_subcategory_options(lang: str = "en") -> List[str]:
    return [_label(e, lang) for e in MECHA_PART_SUBCATEGORIES]


def get_subcategory_label_map(lang: str = "en") -> Dict[str, str]:
    return {_label(e, lang): e[0] for e in MECHA_PART_SUBCATEGORIES}


def get_subcategory_keys() -> List[str]:
    return [e[0] for e in MECHA_PART_SUBCATEGORIES]


def get_variant_options(subcat_key: str, lang: str = "en") -> List[str]:
    return [_label(e, lang) for e in MECHA_PART_VARIANTS.get(subcat_key, [])]


def get_variant_label_map(subcat_key: str, lang: str = "en") -> Dict[str, str]:
    return {_label(e, lang): e[0] for e in MECHA_PART_VARIANTS.get(subcat_key, [])}


def get_tier_options(lang: str = "en") -> List[str]:
    """Mirror mecha_generator's bilingual tier label format."""
    out = []
    for t in Tier:
        en = t.name
        if lang == "zh":
            zh = _TIER_ZH.get(t.name, t.name)
            out.append(f"{zh} ({en})")
        else:
            out.append(en)
    return out


def get_tier_label_map(lang: str = "en") -> Dict[str, str]:
    out: Dict[str, str] = {}
    for t in Tier:
        en = t.name
        if lang == "zh":
            zh = _TIER_ZH.get(t.name, t.name)
            label = f"{zh} ({en})"
        else:
            label = en
        out[label] = en
    return out


_TIER_ZH = {
    "TIER_1_CIVILIAN":   "民用级",
    "TIER_2_INDUSTRIAL": "工业级",
    "TIER_3_MILITARY":   "军用级",
    "TIER_4_ELITE":      "精英级",
    "TIER_5_LEGENDARY":  "传说级",
}


# ---- Generator ----

class MechaPartGenerator(ComponentGenerator):
    """Generator for an individual mecha-mounted weapon, shield, or shoulder pod.

    Reuses ComponentGenerator's layout / view / art-style scaffolding.  The
    subject description differs from the ship-weapon flow in that the mounting
    context is a humanoid mecha hand / forearm / shoulder hardpoint, sized for
    a 15–20m machine rather than a hull bracket.
    """

    def __init__(self, tier: Tier, subcategory: str,
                 primary_color: Optional[str] = None,
                 secondary_color: Optional[str] = None,
                 manufacturer_data: Optional[Dict] = None,
                 variation: Optional[str] = None):
        super().__init__(tier, ComponentType.WEAPON, subcategory,
                         primary_color, secondary_color,
                         manufacturer_data, variation)

    # ----- mount / category metadata -----

    def _mount_label(self) -> str:
        if self.subcategory == "TwoHand":
            return "TWO-HANDED MECHA-HELD"
        if self.subcategory == "OneHand":
            return "ONE-HANDED MECHA-HELD"
        if self.subcategory == "Shield":
            return "FOREARM-MOUNTED MECHA SHIELD"
        if self.subcategory == "Shoulder":
            return "SHOULDER-HARDPOINT MECHA"
        return "MECHA-MOUNTED"

    def _mount_clause(self) -> str:
        """Where on the mecha this part attaches — drives the visible mount geometry."""
        if self.subcategory == "TwoHand":
            return ("This object is a hand-held weapon designed for a humanoid mecha to grip with BOTH manipulator hands. "
                    "It MUST have a clearly visible vertical pistol grip with a trigger guard sized for a mecha gauntlet, "
                    "PLUS a forward auxiliary grip, and a rear stock or counterweight.")
        if self.subcategory == "OneHand":
            return ("This object is a hand-held weapon designed for a humanoid mecha to wield in ONE manipulator hand. "
                    "It MUST have a clearly visible single vertical pistol grip with a trigger guard sized for a mecha gauntlet. "
                    "Compact body — short overall length so it balances in one hand.")
        if self.subcategory == "Shield":
            return ("This object is a shield designed to mount on the FOREARM of a humanoid mecha. "
                    "The reverse face MUST show forearm clamp brackets, latching rails, and an inner hand grip bar — the way a mecha forearm slots into the back. "
                    "The face is a flat or curved armor plate sized to cover a mecha's torso when raised.")
        if self.subcategory == "Shoulder":
            return ("This object is a weapon pod designed to bolt onto the SHOULDER hardpoint of a humanoid mecha. "
                    "It MUST show a clearly visible shoulder mounting bracket / hardpoint pylon on the underside — the bolt-on interface that clamps to the mecha's pauldron. "
                    "There is NO hand grip and NO trigger; the pod is fired remotely by the pilot.")
        return "This object mounts to a humanoid mecha."

    def _category_negative(self) -> str:
        """Per-mount restrictions to keep the silhouette honest."""
        if self.subcategory == "Shield":
            return ("- NO trigger, NO firing barrel as the dominant feature (this is a SHIELD)\n"
                    "- NO pistol grip on the front face — grip and clamps are on the REVERSE face only")
        if self.subcategory == "Shoulder":
            return ("- NO pistol grip, NO trigger, NO ergonomic hand-hold of any kind\n"
                    "- NO hull-mount rotation ring (this is a shoulder pod, not a ship turret)")
        if self.subcategory in ("TwoHand", "OneHand"):
            return ("- NO hull-mount rotation ring or turret base (this is HAND-HELD, not turret-mounted)\n"
                    "- The grip / trigger / stock MUST read as ergonomic for a mecha manipulator hand")
        return ""

    # ----- variant flavor -----

    def _get_variant_desc(self) -> str:
        v = self.variation or ""
        if not v or v == "Standard":
            return ""

        # Two-handed
        if v == "LongBarrel":
            return ("This design features an extremely long, reinforced railgun-style barrel for long-range engagement. "
                    "Barrel length is exaggerated, with a forward bipod or counterweight near the muzzle.")
        if v == "Bazooka":
            return ("This design is a shoulder-fired rocket launcher: a single fat smoothbore tube with a rear blast cone, "
                    "shoulder rest pad, and an external magazine of stubby rockets clipped to the side.")
        if v == "BeamRifle":
            return ("This design is an energy rifle: a slim rectilinear casing with a forward focusing emitter, "
                    "external power-cable conduit, and exposed heat-radiator fins along the receiver.")
        if v == "BeamCannon":
            return ("This design is an oversized energy cannon: a thick segmented barrel with a wide muzzle bell, "
                    "external capacitor housing along the top, and a heavy power feed cable trailing from the rear.")
        if v == "Gatling":
            return ("This design features a rotary multi-barrel gatling mechanism with a massive ammo drum slung under the receiver "
                    "and exposed cooling shrouds around the barrel cluster.")

        # One-handed
        if v == "MachinePistol":
            return ("This design is a compact automatic pistol with a stubby barrel, a curved box magazine in the grip well, "
                    "and a forward foregrip for stabilization.")
        if v == "BeamPistol":
            return ("This design is a compact energy sidearm: a stubby focusing emitter at the front, a vented heat-sink top strap, "
                    "and an exposed energy cell housed in the grip.")
        if v == "BeamSaber":
            return ("This design is a melee energy sword hilt: a cylindrical handle with a knuckle-guard ring, "
                    "a forward emitter aperture, and an inert beam blade rendered as a thin elongated translucent prism (clearly NOT a solid metal blade).")
        if v == "HeatBlade":
            return ("This design is a melee heat dagger: a short triangular solid blade with a glowing heated edge line, "
                    "a knuckle-guard, and a wrapped grip handle.")
        if v == "Tomahawk":
            return ("This design is a melee battle axe: a single broad axe head on a short reinforced haft, "
                    "with a back spike and a wrapped grip.")

        # Shield
        if v == "Tower":
            return ("This design is an oversized tower shield: a tall rectangular armored plate with reinforcing ribs, "
                    "a chunky armor lip, and double forearm clamp rails on the reverse face.")
        if v == "Buckler":
            return ("This design is a small lightweight buckler: a compact round or hexagonal plate sized just to cover a forearm, "
                    "with a single central forearm clamp and a slim profile.")
        if v == "BeamShield":
            return ("This design is a beam shield emitter: the front face is a small emitter unit (NOT a solid plate); the active beam barrier is rendered as a flat translucent rectangular field projected forward from the emitter face. "
                    "The reverse shows a single forearm clamp and a power feed conduit.")
        if v == "ArmedShield":
            return ("This design is an armed shield: a standard plate shield with a built-in gun barrel or missile tube emerging from the front face, "
                    "ammo housing built into the shield body, plus the standard forearm clamps on the reverse.")

        # Shoulder
        if v == "VLS":
            return ("This design is a vertical-launch missile cluster: a flat-topped pod with a grid of square missile silo doors flush with the top surface, "
                    "and a clearly visible shoulder-bracket hardpoint underneath.")
        if v == "BeamCannon":
            return ("This design is a shoulder-mounted energy cannon: a single fat barrel pivoting on a shoulder yoke, "
                    "with an external capacitor pack and a power conduit feeding back into the shoulder bracket.")
        if v == "Gatling":
            return ("This design is a shoulder-mounted rotary gatling: a multi-barrel cluster on a slewing yoke with an underslung ammo drum, "
                    "all bolted to a shoulder hardpoint bracket.")
        if v == "BinderClaw":
            return ("This design is a folding binder pod: a hinged armored shroud that clamshells over the shoulder, "
                    "with an inner array of small missile tubes or sub-emitters revealed when open. Show it in the partially-open configuration.")

        return ""

    # ----- subject description (final assembled) -----

    def generate_subject_description(self) -> str:
        tier_data = self.get_tier_data()
        design_lang = self._get_design_language()
        variant_desc = self._get_variant_desc()

        # Per-subcategory base flavor + features pool.
        # Variant choice may override the features pool with a more specific one.
        if self.subcategory == "TwoHand":
            name = "Two-Handed Mecha Weapon"
            flavor_name = "Mecha-Held Heavy Arm"
            base_negative = "NO hull bracket. NO turret ring. This is a hand-held weapon scaled for a humanoid mecha."
            features_pool = [
                "vertical pistol grip with oversized trigger guard sized for a mecha gauntlet",
                "forward auxiliary grip on the underside of the barrel",
                "shoulder stock or rear counterweight",
                "side-mounted box magazine",
                "iron-sight or top-mounted optic rail",
                "barrel cooling jacket with ventilation slots",
            ]
            v = self.variation
            if v == "Bazooka":
                features_pool = [
                    "single fat smoothbore launch tube",
                    "rear blast cone / venturi exhaust",
                    "shoulder rest pad",
                    "side magazine of stubby rockets",
                    "vertical pistol grip with trigger guard",
                ]
            elif v in ("BeamRifle", "BeamCannon"):
                features_pool = [
                    "forward focusing emitter aperture",
                    "external power-cable conduit feeding the receiver",
                    "exposed heat-radiator fins along the casing",
                    "vertical pistol grip with trigger guard",
                    "top-mounted scope or sensor block",
                ]
                if v == "BeamCannon":
                    features_pool.append("oversized capacitor housing along the spine")
                    features_pool.append("wide muzzle bell")
            elif v == "Gatling":
                features_pool = [
                    "rotary multi-barrel cluster",
                    "underslung ammo drum housing",
                    "electric motor cooling shrouds at the breech",
                    "vertical pistol grip with trigger guard",
                    "forward auxiliary grip",
                ]

        elif self.subcategory == "OneHand":
            name = "One-Handed Mecha Weapon"
            flavor_name = "Mecha-Held Sidearm"
            base_negative = "NO hull bracket. NO turret ring. NO two-handed forward grip. Compact, single-grip weapon."
            features_pool = [
                "single vertical pistol grip with oversized trigger guard sized for a mecha gauntlet",
                "compact short barrel",
                "iron-sight rib along the top",
                "side-mounted box magazine in the grip well",
                "ejection port on the receiver flank",
            ]
            v = self.variation
            if v == "MachinePistol":
                features_pool = [
                    "stubby automatic-fire barrel",
                    "curved box magazine seated in the grip well",
                    "forward foregrip stub",
                    "vertical pistol grip with trigger guard",
                ]
            elif v == "BeamPistol":
                features_pool = [
                    "compact forward focusing emitter",
                    "vented heat-sink top strap",
                    "exposed energy-cell pack housed in the grip",
                    "vertical pistol grip with trigger guard",
                ]
            elif v == "BeamSaber":
                features_pool = [
                    "cylindrical hilt body",
                    "knuckle-guard ring around the grip",
                    "forward emitter aperture",
                    "thin elongated translucent prism rendered as the active beam blade",
                    "vent slots along the hilt for heat dissipation",
                ]
                base_negative = "NO solid metal sword blade — the blade portion is a translucent energy beam emitted from the hilt. NO hull bracket."
            elif v == "HeatBlade":
                features_pool = [
                    "short triangular solid metal blade",
                    "glowing heated edge line along one side of the blade",
                    "knuckle-guard around the grip",
                    "wrapped grip handle",
                ]
                base_negative = "NO firing barrel. NO trigger. This is a melee blade."
            elif v == "Tomahawk":
                features_pool = [
                    "single broad axe head",
                    "back-spike opposite the cutting edge",
                    "short reinforced haft",
                    "wrapped grip section on the haft",
                ]
                base_negative = "NO firing barrel. NO trigger. This is a melee axe."

        elif self.subcategory == "Shield":
            name = "Mecha Forearm Shield"
            flavor_name = "Mecha Defensive Plate"
            base_negative = "NO pistol grip on the FRONT face. The protective surface is the front; clamps and grip are on the reverse."
            features_pool = [
                "flat or gently curved front armor plate",
                "reinforcing ribs running along the length of the plate",
                "chunky armor lip around the perimeter",
                "two parallel forearm clamp rails on the reverse face",
                "central inner hand grip bar on the reverse face",
                "latching mechanism / hinge cluster on the reverse",
            ]
            v = self.variation
            if v == "Tower":
                features_pool = [
                    "tall rectangular armored plate face",
                    "thick reinforcing central spine rib",
                    "chunky perimeter armor lip",
                    "double forearm clamp rails on the reverse face",
                    "inner hand grip bar on the reverse",
                ]
            elif v == "Buckler":
                features_pool = [
                    "compact round or hexagonal plate",
                    "single central forearm clamp on the reverse face",
                    "slim low-profile cross-section",
                    "small inner hand grip on the reverse",
                ]
            elif v == "BeamShield":
                features_pool = [
                    "small forward emitter unit instead of a solid plate front face",
                    "flat translucent rectangular beam-barrier field projected forward from the emitter",
                    "single forearm clamp on the reverse face",
                    "external power-feed conduit on the reverse",
                ]
                base_negative = "The defensive face is NOT a solid plate — it is a translucent projected energy field. NO pistol grip on the front."
            elif v == "ArmedShield":
                features_pool = [
                    "front armor plate face",
                    "built-in gun barrel or missile launch tube emerging from the front face",
                    "internal ammo housing built into the shield body",
                    "two forearm clamp rails on the reverse face",
                    "inner hand grip bar on the reverse",
                ]

        elif self.subcategory == "Shoulder":
            name = "Mecha Shoulder Hardpoint Pod"
            flavor_name = "Mecha Shoulder-Mounted Module"
            base_negative = "NO pistol grip. NO trigger. NO hand-hold. This is a remote-fired shoulder pod."
            features_pool = [
                "shoulder mounting bracket / hardpoint pylon on the underside",
                "bolt-on clamp interface that mates to a mecha pauldron",
                "external sensor or aiming unit",
                "armored outer cowling",
                "service-access panel on the side",
            ]
            v = self.variation
            if v == "VLS":
                features_pool = [
                    "flat-topped pod profile",
                    "grid of square missile silo doors flush with the top surface",
                    "blast deflection channels between silo rows",
                    "shoulder mounting bracket on the underside",
                ]
            elif v == "BeamCannon":
                features_pool = [
                    "single fat barrel on a slewing shoulder yoke",
                    "external capacitor pack along the spine",
                    "power conduit feeding back into the shoulder bracket",
                    "wide muzzle bell at the barrel front",
                    "shoulder mounting bracket on the underside",
                ]
            elif v == "Gatling":
                features_pool = [
                    "rotary multi-barrel cluster on a slewing shoulder yoke",
                    "underslung ammo drum housing",
                    "electric motor cooling shrouds at the breech",
                    "shoulder mounting bracket on the underside",
                ]
            elif v == "BinderClaw":
                features_pool = [
                    "hinged armored clamshell shroud",
                    "inner array of small missile tubes or sub-emitters revealed in the open position",
                    "central pivot hinge along the spine",
                    "shoulder mounting bracket on the underside",
                    "shown in the partially-open configuration",
                ]
        else:
            name = "Mecha Equipment"
            flavor_name = "Mecha Equipment"
            base_negative = ""
            features_pool = []

        features = random.sample(features_pool, min(3, len(features_pool)))
        desc_prefix = self._get_feature_desc_prefix()
        feature_prose = ", ".join(f"a {desc_prefix.lower()} {f}" for f in features)

        tier_adj = tier_data['adjectives'][0]

        mounting_line = f"This is a {name} — {self._mount_clause()} {base_negative}"

        full_description = f"Design language: {tier_data['adjectives'][1]} aesthetic. {design_lang}"
        if variant_desc:
            full_description += f" STRUCTURAL VARIANT: {variant_desc}"

        return f"""SUBJECT DESCRIPTION ({tier_adj} {flavor_name}):
{mounting_line}

{full_description}
The object visually incorporates {feature_prose} — all integrated into the main body as visible design elements (draw these as part of the geometry, do NOT label them with text).

SCALE NOTE: This is a piece of equipment for a 15–20 meter humanoid mecha. The grip / clamp / hardpoint MUST read as sized for a mecha manipulator (oversized compared to a human-scale weapon)."""

    # ----- mecha-equipment specific negatives -----

    def _get_mecha_part_negative_prompt(self) -> str:
        cat_neg = self._category_negative()
        block = "**MECHA-EQUIPMENT-SPECIFIC FORBIDDEN ELEMENTS:**\n"
        block += "- NO human-scale ergonomics (no fingertip-sized triggers, no human-hand grip wraps); all controls are sized for a mecha manipulator gauntlet\n"
        block += "- NO mecha body, NO mecha arm, NO mecha torso, NO pilot figure, NO display stand — render the equipment OBJECT IN ISOLATION, floating against the white background\n"
        block += "- NO hull-mount rotation ring or ship turret base\n"
        if cat_neg:
            block += cat_neg + "\n"
        return block

    def generate_full_prompt(self) -> str:
        tier_adj = self.get_tier_data()['adjectives'][0]

        # Subject name (en label of subcategory + variant for the header)
        sub_en = _SUBCAT_KEY_TO_LABELS.get(self.subcategory, {}).get("en", self.subcategory)
        subject_name = f"{tier_adj} {sub_en}"
        if self.manufacturer_data:
            subject_name = f"{self.manufacturer_data['name']} {subject_name}"
        if self.variation and self.variation != "Standard":
            # Find variant en label
            variants = MECHA_PART_VARIANTS.get(self.subcategory, [])
            v_en = next((en for (k, en, _zh) in variants if k == self.variation), self.variation)
            subject_name += f" ({v_en})"

        mount_label = self._mount_label()
        header = (f"# \n\n`A 2x2 grid illustration (NO TEXT, NO LABELS, NO ARROWS) "
                  f"showing 4 views of a {mount_label} {subject_name}.")

        return f"""{header}

{self._get_layout_criteria()}

{self._get_negative_prompt()}

{self._get_mecha_part_negative_prompt()}

{self.generate_subject_description()}

{self._get_view_protocol()}

{self._get_art_style()}`
"""


# ---- Public string-driven entry point (mirrors pg.generate_prompt_by_strings) ----

def generate_mecha_part_prompt_by_strings(
    tier_name: str,
    subcategory_key: str,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    manufacturer_name: Optional[str] = None,
    variation_key: Optional[str] = None,
) -> str:
    try:
        tier = Tier[tier_name]
    except KeyError:
        return "Error: Invalid Tier"

    if subcategory_key not in {k for (k, _en, _zh) in MECHA_PART_SUBCATEGORIES}:
        return f"Error: Invalid Mecha-Part Subcategory: {subcategory_key}"

    manufacturer_data = None
    if manufacturer_name and manufacturer_name != "None":
        manufacturer_data = get_manufacturer_by_name(manufacturer_name)

    gen = MechaPartGenerator(
        tier=tier,
        subcategory=subcategory_key,
        primary_color=primary_color,
        secondary_color=secondary_color,
        manufacturer_data=manufacturer_data,
        variation=variation_key,
    )
    return gen.generate_full_prompt()
