"""向后兼容 shim：真实实现位于 core.ship_generator。"""
from core.ship_generator import *  # noqa: F401,F403
from core.ship_generator import (  # noqa: F401
    ShipGenerator,
    ARCHETYPES,
    SHIP_VARIANTS,
    load_archetypes,
    get_archetype_names,
    get_archetype,
    get_archetype_list,
    get_variant_list,
    get_designer_options,
    get_designer_label_map,
    generate_ship_prompt_by_strings,
)
