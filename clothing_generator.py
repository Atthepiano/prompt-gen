from typing import Dict, List
import json
import os

DEFAULT_STYLE = (
    "(masterpiece, best quality), late-1980s to early-2000s Japanese mecha OVA or theatrical key visual, "
    "real-robot anime aesthetic, hand-drawn cel animation still, hand-painted cel shading, "
    "flat color fills, hard-edged shadow shapes, clean lineart, crisp forms, "
    "limited palette, subtle color banding, minimal gradients, bold graphic silhouettes, "
    "utilitarian military sci-fi design, realistic 90s material rendering, "
    "clean character design turnarounds, analog texture."
)
DEFAULT_BACKGROUND = "simple pure white background, flat white background, isolated on white."
DEFAULT_MOOD = (
    "(film grain:1.3), muted colors, vintage OVA atmosphere, hand-painted cel look, "
    "matte finish, clean paint layers, subtle cel misregistration, analog video texture, "
    "no oily or glossy look, no modern anime sheen, no oversized eyes, no soft glow, "
    "no 3d, no cgi, no photorealism, no digital painting look, no painterly brushwork, "
    "no thick paint, no heavy impasto, no soft focus, no depth of field."
)

STYLE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "character_style.json")
OPTIONS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "clothing_options.json")


def _load_style_config() -> Dict[str, str]:
    if not os.path.exists(STYLE_CONFIG_PATH):
        return {
            "style": DEFAULT_STYLE,
            "background": DEFAULT_BACKGROUND,
            "mood": DEFAULT_MOOD,
        }
    try:
        with open(STYLE_CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return {
            "style": str(data.get("style", DEFAULT_STYLE)).strip() or DEFAULT_STYLE,
            "background": str(data.get("background", DEFAULT_BACKGROUND)).strip() or DEFAULT_BACKGROUND,
            "mood": str(data.get("mood", DEFAULT_MOOD)).strip() or DEFAULT_MOOD,
        }
    except (OSError, json.JSONDecodeError, TypeError):
        return {
            "style": DEFAULT_STYLE,
            "background": DEFAULT_BACKGROUND,
            "mood": DEFAULT_MOOD,
        }


def _load_options_config() -> Dict[str, List]:
    if not os.path.exists(OPTIONS_CONFIG_PATH):
        return {}
    try:
        with open(OPTIONS_CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def _make_options(pairs: List[tuple], lang: str) -> List[str]:
    use_zh = lang == "zh"
    return [zh if use_zh else en for en, zh in pairs]


def _make_option_map(pairs: List[tuple], lang: str) -> Dict[str, str]:
    use_zh = lang == "zh"
    return {(zh if use_zh else en): en for en, zh in pairs}


def _label_to_value(label: str, mapping: Dict[str, str]) -> str:
    return mapping.get(label, label)


def _labels_to_values(labels: List[str], mapping: Dict[str, str]) -> List[str]:
    return [mapping.get(label, label) for label in labels]


def _localize_text(value, lang: str) -> str:
    if isinstance(value, dict):
        primary = value.get(lang)
        fallback = value.get("zh") if lang == "en" else value.get("en")
        return str(primary or fallback or "").strip()
    return str(value).strip()


def _get_option_pairs(config: Dict[str, List], key: str, default_pairs: List[tuple]) -> List[tuple]:
    raw_items = config.get(key)
    if not isinstance(raw_items, list):
        return default_pairs
    pairs: List[tuple] = []
    for item in raw_items:
        en = zh = None
        if isinstance(item, (list, tuple)) and len(item) == 2:
            en, zh = item
        elif isinstance(item, dict):
            en = item.get("en")
            zh = item.get("zh")
        if en is None or zh is None:
            continue
        en = str(en).strip()
        zh = str(zh).strip()
        if en and zh:
            pairs.append((en, zh))
    return pairs if pairs else default_pairs


FACTION_OPTION_PAIRS = [
    ("Earth Orbital Defense Force", "地球轨道防卫军"),
    ("Urban Public Safety Division", "城市公安机动科"),
    ("Deep Space Resource Consortium", "深空资源联合体"),
    ("Outer Ring Colonial Authority", "外环殖民管理局"),
    ("Amagi Heavy Industries Security", "天城重工安保部"),
    ("Blue Star Relief Medical Corps", "苍星医援组织"),
    ("Academy Joint Research Unit", "学院联合科研团"),
    ("Luminous Independent Network", "流光独立派"),
]
ROLE_OPTION_PAIRS = [
    ("pilot", "飞行员"),
    ("mechanic", "机修工"),
    ("systems engineer", "系统工程师"),
    ("security officer", "安保人员"),
    ("field medic", "现场医疗员"),
    ("navigation officer", "导航官"),
    ("comms operator", "通讯操作员"),
    ("diplomatic liaison", "外交联络官"),
    ("salvage crew", "打捞员"),
    ("research specialist", "研究员"),
    ("student", "学生"),
    ("office worker", "职员"),
    ("station clerk", "站务员"),
    ("teacher", "教师"),
    ("journalist", "记者"),
    ("cafe staff", "咖啡店店员"),
    ("logistics clerk", "物流文员"),
    ("maintenance worker", "维护工"),
    ("dock loader", "码头装卸工"),
]
OUTFIT_CATEGORY_PAIRS = [
    ("flight suit", "飞行服"),
    ("tactical uniform", "战术制服"),
    ("engineering coveralls", "工程连体服"),
    ("EVA soft suit", "舱外软质作业服"),
    ("command uniform", "指挥官制服"),
    ("field research gear", "野外研究装备"),
    ("medical response kit", "医疗救援装"),
    ("cargo crew workwear", "货运工装"),
    ("corporate security kit", "企业安保制服"),
    ("civilian utility wear", "民用功能装"),
    ("school uniform", "校服"),
    ("office attire", "办公通勤装"),
    ("commuter jacket", "通勤夹克"),
    ("casual streetwear", "日常便装"),
]
GENDER_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("Male", "男装"),
    ("Female", "女装"),
]
SILHOUETTE_PAIRS = [
    ("streamlined and fitted", "贴身流线"),
    ("structured armored silhouette", "结构化护甲轮廓"),
    ("oversized layered silhouette", "宽松分层轮廓"),
    ("long coat silhouette", "长外套轮廓"),
    ("short jacket silhouette", "短夹克轮廓"),
    ("asymmetrical paneling", "不对称分割"),
    ("utilitarian harness-heavy", "多束带功能型"),
]
LAYERING_PAIRS = [
    ("single-layer jumpsuit", "单层连体服"),
    ("jacket over flight suit", "飞行服外搭夹克"),
    ("armored vest over uniform", "制服外加护甲背心"),
    ("coat with inner vest", "大衣内搭背心"),
    ("modular outer shell", "模块化外壳层"),
    ("protective apron layer", "防护围裙层"),
]
MATERIAL_PAIRS = [
    ("matte technical fabric", "哑光科技布"),
    ("aramid weave", "芳纶编织"),
    ("brushed composite plates", "拉丝复合板"),
    ("rubberized seals", "橡胶密封"),
    ("leather panels", "皮革拼接"),
    ("carbon fiber inserts", "碳纤维嵌片"),
    ("matte polymer shell", "哑光聚合物外壳"),
]
PALETTE_PAIRS = [
    ("navy and graphite", "海军蓝与石墨灰"),
    ("charcoal and steel", "炭灰与钢色"),
    ("white and cobalt", "白与钴蓝"),
    ("olive and sand", "橄榄绿与沙色"),
    ("burnt orange and gunmetal", "焦橙与枪灰"),
    ("cream and brass", "米白与黄铜"),
    ("black and neon teal", "黑与霓虹青"),
    ("crimson and slate", "深红与板岩灰"),
]
DETAIL_ACCENT_PAIRS = [
    ("rank patches", "军阶贴章"),
    ("reflective strips", "反光条"),
    ("utility pockets", "功能口袋"),
    ("zip panel seams", "拉链拼接线"),
    ("reinforced knees", "加强护膝"),
    ("pressure seals", "压力密封圈"),
    ("medical cross markings", "医疗十字标"),
    ("ID tag strips", "身份标识条"),
    ("magnetic buckles", "磁吸扣件"),
    ("piping edge trim", "包边走线"),
]
ACCESSORY_PAIRS = [
    ("utility belt", "工具腰带"),
    ("tool pouch", "工具小包"),
    ("gloves", "手套"),
    ("reinforced boots", "加固靴"),
    ("helmet tucked under arm", "夹持头盔"),
    ("wrist console", "腕部终端"),
    ("respirator mask", "呼吸面罩"),
    ("radio earpiece", "无线耳机"),
]
INSIGNIA_PAIRS = [
    ("chest insignia", "胸前徽记"),
    ("shoulder patches", "肩章贴片"),
    ("back emblem", "背部徽标"),
    ("armband stripe", "臂章条纹"),
    ("name tag", "姓名牌"),
]
WEAR_STATE_PAIRS = [
    ("pristine and ceremonial", "整洁如新"),
    ("service-worn", "常规磨损"),
    ("battle-worn and scuffed", "战斗磨损"),
    ("dusty field use", "野外尘污"),
    ("oil-stained workwear", "油污工作服"),
]
VIEW_MODE_PAIRS = [
    ("front/back/side + 3/4 sheet (2x2 grid)", "正/背/侧 + 3/4 视图（2x2 网格）"),
    ("turnaround 3-view (front/back/side)", "三视图（正/背/侧）"),
    ("front/back + detail inset (2x2 grid)", "正背面 + 细节小图（2x2 网格）"),
    ("single full-body front", "单一正面全身"),
]
POSE_PAIRS = [
    ("neutral A-pose mannequin", "中性 A 字站姿人台"),
    ("neutral T-pose mannequin", "中性 T 字站姿人台"),
    ("relaxed neutral stance", "放松中性站姿"),
]
PRESENTATION_PAIRS = [
    ("standardized mannequin (faceless, no hair)", "标准人台（无脸无发）"),
    ("faceless human body", "无脸人体"),
    ("flat lay garment layout", "平铺展示"),
]
ASPECT_RATIO_PAIRS = [
    ("Unspecified", "未指定"),
    ("1:1 square", "1:1 方形"),
    ("3:4 portrait", "3:4 竖幅"),
    ("2:3 portrait", "2:3 竖幅"),
]


FACTION_PRESETS = {
    "Earth Orbital Defense Force": {
        "description": {
            "en": "Official orbital military units with disciplined uniforms and flight-ready hardware.",
            "zh": "正式的轨道军队体系，制服严格、装备强调飞行与战备。",
        },
        "design_language": "clean military tailoring, flight-ready harnesses, reinforced seams",
        "palette": "navy, graphite, muted steel, safety orange accents",
        "materials": "matte technical fabric, aramid weave, composite plates",
        "insignia": "orbital crest patches and rank tabs",
    },
    "Urban Public Safety Division": {
        "description": {
            "en": "City tactical response teams focused on restraint, mobility, and visibility.",
            "zh": "城市战术维安部队，强调机动与识别。",
        },
        "design_language": "urban tactical silhouette, modular pads, reflective strips",
        "palette": "charcoal, slate blue, caution yellow highlights",
        "materials": "rubberized panels, matte fabric, reinforced polymer",
        "insignia": "shoulder patches with city crest",
    },
    "Deep Space Resource Consortium": {
        "description": {
            "en": "Industrial crews working remote mining and salvage operations.",
            "zh": "深空采矿与打捞的产业联合体作业人员。",
        },
        "design_language": "heavy-duty workwear, layered utility straps, rugged seams",
        "palette": "burnt orange, gunmetal, dusty khaki",
        "materials": "aramid weave, heavy canvas, scuffed composite plates",
        "insignia": "company tags and serial stencils",
    },
    "Outer Ring Colonial Authority": {
        "description": {
            "en": "Colonial administration outfits blending survival gear with official markings.",
            "zh": "外环殖民管理机构，兼顾生存装备与官方标识。",
        },
        "design_language": "layered outerwear, survival-ready pockets, rugged boots",
        "palette": "olive, sand, weathered white",
        "materials": "matte fabric, weatherproof shells, leather trims",
        "insignia": "authority armbands and back emblems",
    },
    "Amagi Heavy Industries Security": {
        "description": {
            "en": "Corporate security forces with crisp silhouettes and branded hardware.",
            "zh": "企业安保力量，强调线条克制与品牌识别。",
        },
        "design_language": "sleek corporate uniform, precise seams, restrained armor panels",
        "palette": "black, steel gray, subtle teal accents",
        "materials": "matte polymer shell, brushed composite plates",
        "insignia": "minimalist chest logo plates",
    },
    "Blue Star Relief Medical Corps": {
        "description": {
            "en": "Emergency medical responders designed for quick identification and mobility.",
            "zh": "紧急医疗救援组织，强调可识别与机动。",
        },
        "design_language": "clean medical silhouette, modular kits, sterile trims",
        "palette": "white, cobalt blue, soft gray",
        "materials": "matte fabric, sealed trims, medical-grade panels",
        "insignia": "medical cross markings and armband stripes",
    },
    "Academy Joint Research Unit": {
        "description": {
            "en": "Academic field researchers balancing lab practicality and field readiness.",
            "zh": "学院联合科研人员，兼具实验室与外勤特征。",
        },
        "design_language": "lab coat layers over field gear, instrument harnesses",
        "palette": "cream, slate, brass accents",
        "materials": "textured fabric, leather panels, matte polymer trims",
        "insignia": "research unit badges and ID tags",
    },
    "Luminous Independent Network": {
        "description": {
            "en": "Loose independent groups with scavenged, patched, and modular attire.",
            "zh": "松散的独立派，服装拼补、改装与模块化。",
        },
        "design_language": "patched layers, asymmetrical panels, salvaged straps",
        "palette": "mixed neutrals with faded accent colors",
        "materials": "weathered fabric, stitched patches, reclaimed panels",
        "insignia": "hand-painted symbols and stitched tags",
    },
    "Independent Civilian": {
        "description": {
            "en": "Everyday civilians with practical, budget-conscious clothing for urban life.",
            "zh": "日常普通人群体，面向城市生活的实用、节制服饰。",
        },
        "design_language": "simple tailoring, practical layers, subtle utility details",
        "palette": "muted neutrals with small accent colors",
        "materials": "cotton blends, matte fabric, worn leather trims",
        "insignia": "minimal or none, occasional school or company tags",
    },
}


def _load_pairs(key: str, fallback: List[tuple]) -> List[tuple]:
    return _get_option_pairs(_load_options_config(), key, fallback)


def get_faction_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("factions", FACTION_OPTION_PAIRS), lang)


def get_role_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("roles", ROLE_OPTION_PAIRS), lang)


def get_gender_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("gender_options", GENDER_OPTION_PAIRS), lang)


def get_outfit_category_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("outfit_categories", OUTFIT_CATEGORY_PAIRS), lang)


def get_silhouette_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("silhouette_options", SILHOUETTE_PAIRS), lang)


def get_layering_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("layering_options", LAYERING_PAIRS), lang)


def get_material_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("material_options", MATERIAL_PAIRS), lang)


def get_palette_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("palette_options", PALETTE_PAIRS), lang)


def get_detail_accent_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("detail_accents", DETAIL_ACCENT_PAIRS), lang)


def get_accessory_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("accessories", ACCESSORY_PAIRS), lang)


def get_insignia_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("insignia", INSIGNIA_PAIRS), lang)


def get_wear_state_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("wear_state_options", WEAR_STATE_PAIRS), lang)


def get_view_mode_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("view_mode_options", VIEW_MODE_PAIRS), lang)


def get_pose_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("pose_options", POSE_PAIRS), lang)


def get_presentation_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("presentation_options", PRESENTATION_PAIRS), lang)


def get_aspect_ratio_options(lang: str = "en") -> List[str]:
    return _make_options(_load_pairs("aspect_ratio_options", ASPECT_RATIO_PAIRS), lang)


def get_faction_description_map(lang: str = "en") -> Dict[str, str]:
    options = get_faction_options(lang)
    mapping = _make_option_map(_load_pairs("factions", FACTION_OPTION_PAIRS), lang)
    descriptions: Dict[str, str] = {}
    for label in options:
        key = mapping.get(label, label)
        preset = FACTION_PRESETS.get(key)
        if preset:
            descriptions[label] = _localize_text(preset.get("description", ""), lang)
    return descriptions


def _build_view_spec(view_mode: str, pose: str, presentation: str, swap_ready: bool) -> List[str]:
    lines = []
    if view_mode == "turnaround 3-view (front/back/side)":
        lines.append("Turnaround sheet with three orthographic views: front, side, back.")
    elif view_mode == "front/back + detail inset (2x2 grid)":
        lines.append("2x2 grid: front view, back view, side detail inset, material/insignia inset.")
    elif view_mode == "single full-body front":
        lines.append("Single full-body front view, centered and full height.")
    else:
        lines.append("2x2 grid: front view, back view, side view, and 3/4 perspective view.")
    if pose:
        lines.append(f"Pose: {pose}.")
    if presentation:
        lines.append(f"Presentation: {presentation}.")
    if swap_ready:
        lines.append(
            "Swap-ready spec: standardized mannequin proportions, no face or hair, "
            "neutral stance, consistent scale across views, no props."
        )
    return lines


def generate_clothing_preset_prompt(
    faction: str,
    gender: str,
    role: str,
    outfit_category: str,
    silhouette: str,
    layering: str,
    material: str,
    palette: str,
    wear_state: str,
    presentation: str,
    pose: str,
    view_mode: str,
    aspect_ratio: str,
    detail_accents: List[str],
    accessories: List[str],
    insignia: List[str],
    extra_notes: str = "",
    include_style: bool = True,
    include_background: bool = True,
    include_mood: bool = True,
    swap_ready: bool = True,
    lang: str = "en",
) -> str:
    faction_value = _label_to_value(faction, _make_option_map(_load_pairs("factions", FACTION_OPTION_PAIRS), lang))
    gender_value = _label_to_value(gender, _make_option_map(_load_pairs("gender_options", GENDER_OPTION_PAIRS), lang))
    role_value = _label_to_value(role, _make_option_map(_load_pairs("roles", ROLE_OPTION_PAIRS), lang))
    outfit_value = _label_to_value(outfit_category, _make_option_map(_load_pairs("outfit_categories", OUTFIT_CATEGORY_PAIRS), lang))
    silhouette_value = _label_to_value(silhouette, _make_option_map(_load_pairs("silhouette_options", SILHOUETTE_PAIRS), lang))
    layering_value = _label_to_value(layering, _make_option_map(_load_pairs("layering_options", LAYERING_PAIRS), lang))
    material_value = _label_to_value(material, _make_option_map(_load_pairs("material_options", MATERIAL_PAIRS), lang))
    palette_value = _label_to_value(palette, _make_option_map(_load_pairs("palette_options", PALETTE_PAIRS), lang))
    wear_state_value = _label_to_value(wear_state, _make_option_map(_load_pairs("wear_state_options", WEAR_STATE_PAIRS), lang))
    presentation_value = _label_to_value(presentation, _make_option_map(_load_pairs("presentation_options", PRESENTATION_PAIRS), lang))
    pose_value = _label_to_value(pose, _make_option_map(_load_pairs("pose_options", POSE_PAIRS), lang))
    view_mode_value = _label_to_value(view_mode, _make_option_map(_load_pairs("view_mode_options", VIEW_MODE_PAIRS), lang))
    aspect_ratio_value = _label_to_value(aspect_ratio, _make_option_map(_load_pairs("aspect_ratio_options", ASPECT_RATIO_PAIRS), lang))

    detail_values = _labels_to_values(detail_accents, _make_option_map(_load_pairs("detail_accents", DETAIL_ACCENT_PAIRS), lang))
    accessory_values = _labels_to_values(accessories, _make_option_map(_load_pairs("accessories", ACCESSORY_PAIRS), lang))
    insignia_values = _labels_to_values(insignia, _make_option_map(_load_pairs("insignia", INSIGNIA_PAIRS), lang))

    preset = FACTION_PRESETS.get(faction_value, {})

    subject_bits = [role_value]
    if gender_value and gender_value != "Unspecified":
        subject_bits.insert(0, f"{gender_value} outfit")
    subject_line = f"Full-body outfit preset sheet for {' '.join(subject_bits)} from {faction_value}."
    outfit_bits = []
    if outfit_value:
        outfit_bits.append(outfit_value)
    if silhouette_value:
        outfit_bits.append(silhouette_value)
    if layering_value:
        outfit_bits.append(layering_value)
    if material_value:
        outfit_bits.append(material_value)
    if palette_value:
        outfit_bits.append(f"palette: {palette_value}")
    if wear_state_value:
        outfit_bits.append(wear_state_value)
    outfit_line = "Outfit build: " + ", ".join(outfit_bits) + "." if outfit_bits else ""
    if gender_value == "Male":
        outfit_line = f"{outfit_line} Male cut: straighter shoulder line, longer torso, relaxed waist."
    elif gender_value == "Female":
        outfit_line = f"{outfit_line} Female cut: softer shoulder line, defined waist taper, balanced proportions."

    faction_line = ""
    if preset:
        faction_line = (
            f"Faction design language: {preset.get('design_language', '')}. "
            f"Palette guidance: {preset.get('palette', '')}. "
            f"Material guidance: {preset.get('materials', '')}. "
            f"Insignia style: {preset.get('insignia', '')}."
        ).strip()

    detail_line = f"Garment details: {', '.join(detail_values)}." if detail_values else ""
    accessory_line = f"Accessories: {', '.join(accessory_values)}." if accessory_values else ""
    insignia_line = f"Insignia placement: {', '.join(insignia_values)}." if insignia_values else ""

    view_lines = _build_view_spec(view_mode_value, pose_value, presentation_value, swap_ready)
    ratio_line = ""
    if aspect_ratio_value and aspect_ratio_value != "Unspecified":
        ratio_line = f"Aspect ratio {aspect_ratio_value.split()[0]}."

    parts = [subject_line]
    if outfit_line:
        parts.append(outfit_line)
    if faction_line:
        parts.append(faction_line)
    if detail_line:
        parts.append(detail_line)
    if accessory_line:
        parts.append(accessory_line)
    if insignia_line:
        parts.append(insignia_line)
    parts.extend(view_lines)
    if ratio_line:
        parts.append(ratio_line)
    if extra_notes.strip():
        parts.append(extra_notes.strip())

    style_cfg = _load_style_config()
    if include_style:
        style_line = f"{style_cfg['style']} clean outfit reference sheet, garment-focused, no character acting."
        parts = [style_line, ""] + parts
    if include_background:
        parts.extend(["", style_cfg["background"], "pure white background only, no environment."])
    if include_mood:
        parts.extend(["", style_cfg["mood"]])

    return "\n".join(parts).strip() + "\n"
