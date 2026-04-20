"""向后兼容 shim：真实实现位于 core.mecha_part_generator。"""
from core.mecha_part_generator import *  # noqa: F401,F403
from core.mecha_part_generator import (  # noqa: F401
    MechaPartGenerator,
    MECHA_PART_SUBCATEGORIES,
    MECHA_PART_VARIANTS,
    get_subcategory_options,
    get_subcategory_label_map,
    get_subcategory_keys,
    get_variant_options,
    get_variant_label_map,
    get_tier_options,
    get_tier_label_map,
    generate_mecha_part_prompt_by_strings,
)
