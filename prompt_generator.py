"""向后兼容 shim：真实实现已搬到 core.prompt_generator。"""
from core.prompt_generator import *  # noqa: F401,F403
from core.prompt_generator import (  # noqa: F401
    Tier,
    ComponentType,
    MANUFACTURERS,
    load_manufacturers,
    get_manufacturer_by_name,
    get_component_map,
    get_tier_list,
    get_manufacturer_names,
    get_variants_for_subcategory,
    generate_prompt_by_strings,
)
