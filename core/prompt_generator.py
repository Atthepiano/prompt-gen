import random
import json
import os
from enum import Enum
from typing import List, Dict, Tuple, Optional

# --- Enums ---

class Tier(Enum):
    TIER_1_CIVILIAN = 1
    TIER_2_INDUSTRIAL = 2
    TIER_3_MILITARY = 3
    TIER_4_ELITE = 4
    TIER_5_LEGENDARY = 5

class ComponentType(Enum):
    WEAPON = "Weapon"
    SHIELD = "Shield"
    ENGINE = "Engine"
    CARGO = "Cargo"

# --- Data & Configuration ---

TIER_DESCRIPTORS = {
    Tier.TIER_1_CIVILIAN: {
        "adjectives": ["Basic", "Rudimentary", "Improvised", "Low-Cost", "Civilian-Grade"],
        "design_language": "Exposed skeleton, rough welding, functional but ugly, mismatched panels.",
        "color_palette": "Rusted orange, dull grey, caution yellow stripes."
    },
    Tier.TIER_2_INDUSTRIAL: {
        "adjectives": ["Standard", "Heavy-Duty", "Mass-Produced", "Reliable", "Reinforced"],
        "design_language": "Blocky, utilitarian, thick frames, modular connection points.",
        "color_palette": "Industrial safety orange, gunmetal grey, white details."
    },
    Tier.TIER_3_MILITARY: {
        "adjectives": ["Advanced", "High-Tech", "Precision", "Elite", "Prototype"],
        "design_language": "Sleek armor, active energy lines, aerodynamic cowlings, hexagonal patterns.",
        "color_palette": "Matte navy blue, glowing neon cyan, polished chrome."
    },
    Tier.TIER_4_ELITE: {
        "adjectives": ["Elite", "Experimental", "Bleeding-Edge", "Secret", "Overclocked"],
        "design_language": "Unstable energy signatures, floating components, forbidden geometry, exposed power cores.",
        "color_palette": "Void purple, unstable crimson, quantum white details."
    },
    Tier.TIER_5_LEGENDARY: {
        "adjectives": ["Legendary", "Precursor", "Monolithic", "Lost-Tech", "Transcendant"],
        "design_language": "Seamless matte-black ceramic, floating geometric shapes, defying gravity, zero visible seams, pulsing silent energy.",
        "color_palette": "Matte black ceramic, blinding white energy, obsidian finish."
    }
}

# --- Manufacturer Loading ---

def load_manufacturers() -> List[Dict]:
    from paths import resource_path
    try:
        with open(resource_path("manufacturers.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

MANUFACTURERS = load_manufacturers()

def get_manufacturer_by_name(name: str) -> Optional[Dict]:
    for m in MANUFACTURERS:
        if m["name"] == name:
            return m
    return None

# --- Structural Variants Data ---
WEAPON_VARIANTS = {
    "Kinetic": ["Standard", "Long-Barrel (Sniper)", "Twin-Linked (Rapid)", "Gatling (Rotary)"],
    "Beam": ["Standard", "Focus Lance (Sniper)", "Prism Array (Scatter)", "Twin-Linked (Rapid)"],
    "Missile": ["Standard Pod", "VLS Array (Vertical)", "Torpedo Tube (Heavy)"],
    "MechaHangar": ["Standard", "Catapult Deck", "Repair Bay"],
}

# --- Base Class ---

class ComponentGenerator:
    def __init__(self, tier: Tier, category: ComponentType, subcategory: str, 
                 primary_color: Optional[str] = None, secondary_color: Optional[str] = None,
                 manufacturer_data: Optional[Dict] = None, variation: Optional[str] = None):
        self.tier = tier
        self.category = category
        self.subcategory = subcategory
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.manufacturer_data = manufacturer_data
        self.variation = variation
        
    def get_tier_data(self):
        return TIER_DESCRIPTORS[self.tier]

    def _get_layout_criteria(self) -> str:
        return """**LAYOUT & FORMAT CRITERIA (CRITICAL):**
The final image must be a clean reference sheet showing exactly four views.
The views must be arranged in a precise 2x2 GRID on the canvas (Aspect Ratio 1:1).
VIEWS MUST BE ISOLATED AND MUST NOT OVERLAP.
Background must be PURE SOLID WHITE (#FFFFFF).

**ABSOLUTELY FORBIDDEN — ZERO TEXT & ZERO ANNOTATIONS:**
The image must contain ZERO rendered text of any kind — no letters, no words, no numbers, no labels, no titles.
Do NOT draw any arrows, callout lines, leader lines, pointers, or annotation marks.
Do NOT add part names, view names, component labels, dimension markings, or any other textual overlay.
The sheet must be purely visual artwork — only the object itself, with no typographic or diagrammatic elements whatsoever."""

    def _get_view_protocol(self) -> str:
        return """VIEW ANGLES PROTOCOL (render visuals only, NO text labels on any view):
The sheet must contain these 4 distinct views of the exact same object, drawn WITHOUT any accompanying text:
1. Front orthographic angle
2. Side orthographic angle
3. Top-down orthographic angle
4. 3/4 isometric perspective angle
Each quadrant shows only the object artwork — no view-name captions, no dimension lines, no annotations."""

    def _get_art_style(self) -> str:
        # Determine palette priority: Manufacturer > Custom > Tier Default
        if self.manufacturer_data:
             palette = self.manufacturer_data["color_palette"]
        elif self.primary_color and self.secondary_color:
            palette = f"{self.primary_color} main body, {self.secondary_color} energy/glow, dark mechanical details."
        else:
            palette = self.get_tier_data()["color_palette"]

        return f"""ART STYLE (Unified PC-98 Cel-Shading):
Retro Japanese PC-98 computer game aesthetic fused with anime cel-shading.
Bold, distinct black outlines on all edges.
Hard-edged block shading across ALL views showing weight and depth. High contrast retro anime look.
Color Palette: {palette}
REMINDER: Absolutely NO text, NO labels, NO arrows, NO annotations anywhere in the image."""

    def _get_design_language(self) -> str:
        base_design = self.get_tier_data()['design_language']
        if self.manufacturer_data:
            corp_design = self.manufacturer_data['design_language']
            return f"{corp_design} Blended with {base_design}"
        return base_design

    def generate_subject_description(self) -> str:
        raise NotImplementedError

    def _get_negative_prompt(self) -> str:
        return """**NEGATIVE / FORBIDDEN ELEMENTS (do NOT generate any of the following):**
- ANY text, letters, words, numbers, labels, titles, captions, watermarks, or signatures
- ANY arrows, callout lines, leader lines, pointers, or annotation marks
- ANY diagrams, dimension lines, measurement markings, or rulers
- ANY UI elements, buttons, borders with text, or info-boxes
The output must be a PURE ILLUSTRATION with absolutely no typographic or diagrammatic overlay."""

    def _get_weapon_negative_prompt(self) -> str:
        return """**WEAPON-SPECIFIC FORBIDDEN ELEMENTS:**
- NO pistol grip, trigger, trigger guard, stock, buttstock, magazine, carry handle, or any ergonomic feature sized for a human hand
- The base/mount of this object is a mechanical hull bracket or rotation ring — NOT a handle to be held"""

    def generate_full_prompt(self) -> str:
        tier_adj = self.get_tier_data()['adjectives'][0]
        
        # Manufacturer Prefix
        subject_name = f"{tier_adj} {self.subcategory} {self.category.value}"
        if self.manufacturer_data:
            subject_name = f"{self.manufacturer_data['name']} {subject_name}"
        
        # Add Variant to Name
        if self.variation and self.variation != "Standard":
            subject_name += f" ({self.variation})"

        header = f"# \n\n`A 2x2 grid illustration (NO TEXT, NO LABELS, NO ARROWS) showing 4 views of a {subject_name}."
        
        return f"""{header}

{self._get_layout_criteria()}

{self._get_negative_prompt()}

{self.generate_subject_description()}

{self._get_view_protocol()}

{self._get_art_style()}`
"""

    def _get_feature_desc_prefix(self) -> str:
        if self.tier == Tier.TIER_1_CIVILIAN: return "Simple"
        if self.tier == Tier.TIER_2_INDUSTRIAL: return "Heavy"
        if self.tier == Tier.TIER_3_MILITARY: return "Advanced"
        if self.tier == Tier.TIER_4_ELITE: return "Experimental"
        if self.tier == Tier.TIER_5_LEGENDARY: return "Monolithic"
        return "Standard"

# --- Subclasses ---

class WeaponGenerator(ComponentGenerator):
    def __init__(self, tier: Tier, subcategory: str, primary_color: str = None, secondary_color: str = None, manufacturer_data: Dict = None, variation: str = None):
        super().__init__(tier, ComponentType.WEAPON, subcategory, primary_color, secondary_color, manufacturer_data, variation)

    def generate_full_prompt(self) -> str:
        tier_adj = self.get_tier_data()['adjectives'][0]
        
        subject_name = f"{tier_adj} {self.subcategory} Ship Weapon Turret"
        if self.manufacturer_data:
            subject_name = f"{self.manufacturer_data['name']} {subject_name}"
        if self.variation and self.variation != "Standard":
            subject_name += f" ({self.variation})"

        header = f"# \n\n`A 2x2 grid illustration (NO TEXT, NO LABELS, NO ARROWS) showing 4 views of a SPACESHIP-MOUNTED {subject_name}."
        
        return f"""{header}

{self._get_layout_criteria()}

{self._get_negative_prompt()}

{self._get_weapon_negative_prompt()}

{self.generate_subject_description()}

{self._get_view_protocol()}

{self._get_art_style()}`
"""

    def _get_variant_desc(self) -> str:
        if not self.variation or "Standard" in self.variation:
            return ""
        
        # Kinetic Variants
        if "Long-Barrel" in self.variation:
            return "This design features an extremely long, reinforced railgun-style barrel for long-range engagement. The barrel length is exaggerated."
        if "Twin-Linked" in self.variation:
            return "This design features TWO parallel weapon barrels/emitters mounted side-by-side (Twin-Linked configuration)."
        if "Gatling" in self.variation:
            return "This design features a rotary multi-barrel gatling mechanism. Massive ammo drum and cooling jackets."
            
        # Beam Variants
        if "Focus Lance" in self.variation:
            return "This design features a massive singular focusing lens structure for sniper-class beam projection."
        if "Prism Array" in self.variation:
            return "This design features a honeycomb-like array of multiple small beam emitter prisms."
            
        # Missile Variants
        if "VLS" in self.variation:
            return "This design is a Vertical Launch System (VLS) array, featuring a grid of missile silo doors flush with the armor."
        if "Torpedo" in self.variation:
            return "This design features a single massive large-bore launch tube for heavy anti-ship torpedoes."

        return ""

    def generate_subject_description(self) -> str:
        tier_data = self.get_tier_data()
        design_lang = self._get_design_language()
        variant_desc = self._get_variant_desc()

        # Subcategory specifics
        if self.subcategory == "Kinetic":
            name = "Kinetic Weapon Module"
            flavor_name = "Shipboard Ballistic Cannon"
            negative = "NO laser beams. NO energy crystals."
            features_pool = ["large-bore rifled barrel with muzzle brake", "automated ammo feed mechanism", "hydraulic recoil buffer assembly", "shell casing ejection chute", "barrel cooling jacket with ventilation slots", "turret rotation ring mount"]
            if self.variation and "Gatling" in self.variation:
                features_pool = ["spinning rotary barrel cluster", "massive belt-fed ammo drum housing", "electric motor cooling shrouds", "centrifugal barrel rotation mechanism"]
            elif self.variation and "Twin-Linked" in self.variation:
                features_pool = ["twin parallel oversized barrels", "synchronized hydraulic recoil frame", "dual-path ammo feed housing"]

        elif self.subcategory == "Beam":
            name = "Beam Weapon Module"
            flavor_name = "Shipboard Directed Energy Cannon"
            negative = "NO solid projectile barrels. NO ammo boxes."
            features_pool = ["large focusing lens assembly", "heat sink fin array", "high-voltage power conduit bundles", "capacitor bank housing", "thermal radiator panels", "turret rotation ring mount"]
            if self.variation and "Prism" in self.variation:
                features_pool = ["honeycomb prism array emitter face", "multi-phase capacitor bank", "refraction crystal housing cluster"]

        elif self.subcategory == "Missile":
            name = "Missile Weapon Module"
            flavor_name = "Shipboard Ordnance Launcher"
            negative = "NO gun barrels. NO continuous beams."
            features_pool = ["missile launch tube cluster", "targeting radar dome", "automated loading mechanism housing", "blast deflection shield plate", "targeting sensor array", "hull attachment mounting bracket"]
            if self.variation and "VLS" in self.variation:
                features_pool = ["flush vertical launch silo grid with armored hatch doors", "blast deflection channel trenches", "top-loading automated hatch array"]
            elif self.variation and "Torpedo" in self.variation:
                features_pool = ["single oversized large-bore torpedo launch tube", "blast reinforced tube housing", "torpedo loading rail mechanism"]

        elif self.subcategory == "MechaHangar":
            name = "Mecha Hangar Bay Module"
            flavor_name = "Mobile Suit Deployment Bay"
            negative = "NO guns. NO weapons. This is a HANGAR MODULE, not a weapon."
            features_pool = ["large armored deployment bay door", "articulated maintenance arm", "fuel supply hose coupling", "warning light strips", "electromagnetic catapult launch rail"]
        else:
            name = "Shipboard Weapon Module"
            flavor_name = "Weapon"
            negative = ""
            features_pool = []

        features = random.sample(features_pool, min(3, len(features_pool)))
        
        desc_prefix = self._get_feature_desc_prefix()
        feature_prose = ", ".join(f"a {desc_prefix.lower()} {f}" for f in features)

        tier_adj = tier_data['adjectives'][0]

        # Mounting context — stated once, concisely
        mounting_line = f"This is a {name} — a weapon system fixed to a spaceship's exterior hull via a mechanical mount. {negative}"
        
        full_description = f"Design language: {tier_data['adjectives'][1]} aesthetic. {design_lang}"
        if variant_desc:
            full_description += f" STRUCTURAL VARIANT: {variant_desc}"

        return f"""SUBJECT DESCRIPTION ({tier_adj} {flavor_name}):
{mounting_line}

{full_description}
The object visually incorporates {feature_prose} — all integrated into the main body as visible design elements (draw these as part of the geometry, do NOT label them with text)."""


class ShieldGenerator(ComponentGenerator):
    def __init__(self, tier: Tier, subcategory: str, primary_color: str = None, secondary_color: str = None, manufacturer_data: Dict = None, variation: str = None):
        super().__init__(tier, ComponentType.SHIELD, subcategory, primary_color, secondary_color, manufacturer_data, variation)

    def generate_subject_description(self) -> str:
        tier_data = self.get_tier_data()
        design_lang = self._get_design_language()
        
        if self.subcategory == "Bubble":
            name = "Omni-Bubble Generator"
            flavor_name = "Spherical Field Emitter"
            negative = "NO dish antennas."
            features_pool = ["spherical core", "ring emitters", "field stabilizers"]
        elif self.subcategory == "Plate":
            name = "Directional Shield Emitter"
            flavor_name = "Deflector Dish"
            negative = "NO spherical cores."
            features_pool = ["projector dish", "capacitor coils", "reinforcement struts"]
        else:
            name = "Shield"
            flavor_name = "Shield"
            negative = ""
            features_pool = []

        features = random.sample(features_pool, min(3, len(features_pool)))
        feature_prose = ", ".join(f"a {f}" for f in features)

        tier_adj = tier_data['adjectives'][0]

        return f"""SUBJECT DESCRIPTION ({tier_adj} {flavor_name}):
This is a {name}. {negative}

This design is a {name} with a {tier_data['adjectives'][1]} aesthetic. {design_lang}
The object visually incorporates {feature_prose} — all integrated into the main body as visible design elements (draw these as part of the geometry, do NOT label them with text)."""

class EngineGenerator(ComponentGenerator):
    def __init__(self, tier: Tier, subcategory: str, primary_color: str = None, secondary_color: str = None, manufacturer_data: Dict = None, variation: str = None):
        super().__init__(tier, ComponentType.ENGINE, subcategory, primary_color, secondary_color, manufacturer_data, variation)

    def generate_subject_description(self) -> str:
        tier_data = self.get_tier_data()
        design_lang = self._get_design_language()
        
        if self.subcategory == "Ion":
            name = "Ion Thruster"
            flavor_name = "Electric Propulsion"
            negative = "NO smoke. NO fire."
            features_pool = ["ion grid", "magnetic rings", "high-voltage cables"]
        elif self.subcategory == "Chemical":
            name = "Chemical Rocket"
            flavor_name = "Combustion Drive"
            negative = "NO electrical glow."
            features_pool = ["combustion nozzle", "fuel pipes", "turbopump housing"]
        elif self.subcategory == "Warp":
            name = "Warp Drive"
            flavor_name = "FTL Engine"
            negative = "NO exhaust output."
            features_pool = ["gravity torus", "singularity containment", "field coils"]
        else: 
            name = "Engine"
            flavor_name = "Engine"
            negative = ""
            features_pool = []

        features = random.sample(features_pool, min(3, len(features_pool)))
        feature_prose = ", ".join(f"a {f}" for f in features)

        tier_adj = tier_data['adjectives'][0]

        return f"""SUBJECT DESCRIPTION ({tier_adj} {flavor_name}):
This is a {name}. {negative}

This design is a {name} with a {tier_data['adjectives'][1]} aesthetic. {design_lang}
The object visually incorporates {feature_prose} — all integrated into the main body as visible design elements (draw these as part of the geometry, do NOT label them with text)."""

class CargoGenerator(ComponentGenerator):
    def __init__(self, tier: Tier, subcategory: str, primary_color: str = None, secondary_color: str = None, manufacturer_data: Dict = None, variation: str = None):
        super().__init__(tier, ComponentType.CARGO, subcategory, primary_color, secondary_color, manufacturer_data, variation)

    def generate_subject_description(self) -> str:
        tier_data = self.get_tier_data()
        design_lang = self._get_design_language()
        
        if self.subcategory == "Standard":
            name = "Standard Container"
            flavor_name = "General Freight Module"
            negative = "NO complex machinery."
            features_pool = ["locking clamps", "crane handles", "stacking guides"]
        elif self.subcategory == "Fluid":
            name = "Fluid Tank"
            flavor_name = "Liquid Storage"
            negative = "NO square corners."
            features_pool = ["cylindrical tank", "pressure valve", "hazard stripes"]
        elif self.subcategory == "Secure":
            name = "Secure Vault"
            flavor_name = "High-Security Storage"
            negative = "NO windows."
            features_pool = ["reinforced door", "keypad lock", "thick walls"]
        else:
            name = "Cargo Module"
            flavor_name = "Cargo"
            negative = ""
            features_pool = []

        features = random.sample(features_pool, min(3, len(features_pool)))
        feature_prose = ", ".join(f"a {f}" for f in features)

        tier_adj = tier_data['adjectives'][0]

        return f"""SUBJECT DESCRIPTION ({tier_adj} {flavor_name}):
This is a {name}. {negative}

This design is a {name} with a {tier_data['adjectives'][1]} aesthetic. {design_lang}
The object visually incorporates {feature_prose} — all integrated into the main body as visible design elements (draw these as part of the geometry, do NOT label them with text)."""

# --- Helpers for UI ---

def get_component_map() -> Dict[str, List[str]]:
    return {
        ComponentType.WEAPON.value: ["Kinetic", "Beam", "Missile", "MechaHangar"],
        ComponentType.SHIELD.value: ["Bubble", "Plate"],
        ComponentType.ENGINE.value: ["Ion", "Chemical", "Warp"],
        ComponentType.CARGO.value: ["Standard", "Fluid", "Secure"]
    }

def get_tier_list() -> List[str]:
    return [t.name for t in Tier]

def get_manufacturer_names() -> List[str]:
    return [m["name"] for m in MANUFACTURERS]

def get_variants_for_subcategory(category: str, subcategory: str) -> List[str]:
    if category == "Weapon" and subcategory in WEAPON_VARIANTS:
        return WEAPON_VARIANTS[subcategory]
    return ["Standard"]

def generate_prompt_by_strings(tier_name: str, category_name: str, subcategory_name: str, 
                               primary_color: str = None, secondary_color: str = None,
                               manufacturer_name: str = None, variation_name: str = None) -> str:
    # Resolve Enum Members
    try:
        tier = Tier[tier_name]
    except KeyError:
        return "Error: Invalid Tier"
    
    # Resolve Category Enum
    category_enum = None
    for c in ComponentType:
        if c.value == category_name:
            category_enum = c
            break
    if not category_enum:
        return "Error: Invalid Category"
    
    # Resolve Manufacturer
    manufacturer_data = None
    if manufacturer_name and manufacturer_name != "None":
        manufacturer_data = get_manufacturer_by_name(manufacturer_name)

    # Instantiate Generator
    if category_enum == ComponentType.WEAPON:
        gen = WeaponGenerator(tier, subcategory_name, primary_color, secondary_color, manufacturer_data, variation_name)
    elif category_enum == ComponentType.SHIELD:
        gen = ShieldGenerator(tier, subcategory_name, primary_color, secondary_color, manufacturer_data, variation_name)
    elif category_enum == ComponentType.ENGINE:
        gen = EngineGenerator(tier, subcategory_name, primary_color, secondary_color, manufacturer_data, variation_name)
    elif category_enum == ComponentType.CARGO:
        gen = CargoGenerator(tier, subcategory_name, primary_color, secondary_color, manufacturer_data, variation_name)
    else:
        return "Error: Unknown Category Generator"
        
    return gen.generate_full_prompt()


# --- Main Execution ---

if __name__ == "__main__":
    test_cases = [
        WeaponGenerator(Tier.TIER_3_MILITARY, "Beam", manufacturer_data=MANUFACTURERS[0] if MANUFACTURERS else None, variation="Twin-Linked (Rapid)"), 
        WeaponGenerator(Tier.TIER_5_LEGENDARY, "Kinetic", primary_color="#222222", secondary_color="#00FFFF", variation="Gatling (Rotary)"), 
        EngineGenerator(Tier.TIER_4_ELITE, "Warp"),
    ]

    output_content = ""
    for generator in test_cases:
        output_content += generator.generate_full_prompt()
        output_content += "\n" + "-"*40 + "\n\n"

    with open("output_test.md", "w", encoding="utf-8") as f:
        f.write(output_content)
    
    print("Successfully generated output_test.md with example prompts.")
