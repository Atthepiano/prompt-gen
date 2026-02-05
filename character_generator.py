from typing import Dict, List, Optional
import json
import os

DEFAULT_STYLE = (
    "(masterpiece, best quality), authentic early-1990s Japanese OVA anime key visual, "
    "PC-98 era Japanese computer game illustration, hand-painted cel shading, "
    "clean lineart, crisp forms, controlled rim lighting, deep shadows, "
    "soft airbrush gradients, subtle color banding, balanced contrast, "
    "iconic 90s character design with striking presence, sharp angles, realistic facial proportions, "
    "cinematic composition, analog texture, "
    "style of Haruhiko Mikimoto, Yoshiyuki Sadamoto."
)

DEFAULT_BACKGROUND = "simple pure white background, flat white background, isolated on white."
DEFAULT_MOOD = (
    "(film grain:1.3), muted colors, vintage OVA atmosphere, hand-painted cel look, "
    "matte finish, clean paint layers, no oily or glossy look."
)

STYLE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "character_style.json")
OPTIONS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "character_options.json")


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

def _bilingual(en: str, zh: str) -> str:
    return f"{en} / {zh}"


def _make_options(pairs: List[tuple]) -> List[str]:
    return [_bilingual(en, zh) for en, zh in pairs]


def _make_option_map(pairs: List[tuple]) -> Dict[str, str]:
    return {_bilingual(en, zh): en for en, zh in pairs}


def _label_to_value(label: str, mapping: Dict[str, str]) -> str:
    return mapping.get(label, label)


def _labels_to_values(labels: List[str], mapping: Dict[str, str]) -> List[str]:
    return [mapping.get(label, label) for label in labels]


def _load_options_config() -> Dict[str, List]:
    if not os.path.exists(OPTIONS_CONFIG_PATH):
        return {}
    try:
        with open(OPTIONS_CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


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


GENDER_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("Male", "男性"),
    ("Female", "女性"),
    ("Androgynous", "中性"),
    ("Non-binary", "非二元"),
]
AGE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("Young adult", "青年"),
    ("Adult", "成年人"),
    ("Mature adult", "成熟成年人"),
]
FRAMING_OPTION_PAIRS = [
    ("head-and-shoulders portrait", "头像到肩部"),
    ("bust portrait", "胸像"),
    ("half body portrait", "半身"),
    ("three-quarter body portrait", "四分之三身"),
    ("full body portrait", "全身"),
]
ASPECT_RATIO_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("1:1 square", "1:1 方形"),
    ("2:3 portrait", "2:3 竖幅"),
    ("3:4 portrait", "3:4 竖幅"),
    ("9:16 vertical", "9:16 竖屏"),
    ("16:9 widescreen", "16:9 宽屏"),
]
EXPRESSION_OPTION_PAIRS = [
    ("serious expression", "严肃"),
    ("calm expression", "冷静"),
    ("focused expression", "专注"),
    ("confident expression", "自信"),
]
GAZE_OPTION_PAIRS = [
    ("looking at camera", "直视镜头"),
    ("looking slightly off-camera", "略微偏离镜头"),
    ("looking to the side", "侧视"),
]
APPEARANCE_OPTION_PAIRS = [
    ("sharp jawline", "清晰下颌线"),
    ("defined cheekbones", "高颧骨"),
    ("subtle freckles", "浅雀斑"),
    ("beauty mark", "美人痣"),
    ("brow slit", "眉间划痕"),
    ("dark eye circles", "眼下阴影"),
    ("soft blush", "微红腮"),
    ("sharp eyeliner", "锐利眼线"),
    ("glossy lips", "光泽唇彩"),
    ("scar across cheek", "脸颊疤痕"),
    ("nose bridge bandage", "鼻梁贴"),
    ("stern eyebrows", "浓眉"),
    ("hardened eyes", "坚毅眼神"),
    ("asymmetrical bangs", "不对称刘海"),
    ("messy fringe", "凌乱刘海"),
    ("heterochromia", "异色瞳"),
]
BODY_TYPE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("slim build", "纤细"),
    ("athletic build", "运动型"),
    ("lean build", "精瘦"),
    ("muscular build", "肌肉型"),
    ("stocky build", "壮实"),
    ("curvy build", "曲线明显"),
]
SKIN_TONE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("fair skin tone", "白皙肤色"),
    ("light skin tone", "浅肤色"),
    ("medium skin tone", "中等肤色"),
    ("tan skin tone", "小麦肤色"),
    ("dark skin tone", "深肤色"),
    ("deep skin tone", "黝黑肤色"),
]
HAIR_COLOR_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("black", "黑色"),
    ("dark brown", "深棕色"),
    ("brown", "棕色"),
    ("blonde", "金色"),
    ("silver", "银色"),
    ("white", "白色"),
    ("red", "红色"),
    ("blue", "蓝色"),
    ("green", "绿色"),
    ("purple", "紫色"),
]
HAIR_STYLE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("short cropped", "超短发"),
    ("pixie cut", "精灵短发"),
    ("short layered", "短层次"),
    ("bob cut", "波波头"),
    ("slicked back", "后梳"),
    ("long straight", "长直发"),
    ("long wavy", "长卷发"),
    ("twin tails", "双马尾"),
    ("high ponytail", "高马尾"),
    ("low ponytail", "低马尾"),
    ("braided", "编发"),
    ("half-up", "半扎发"),
    ("hime cut", "姬发式"),
    ("wolf cut", "狼尾"),
    ("undercut", "两侧剃短"),
    ("shaved sides", "侧剃"),
]
EYE_COLOR_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("brown", "棕色"),
    ("blue", "蓝色"),
    ("green", "绿色"),
    ("hazel", "榛色"),
    ("amber", "琥珀色"),
    ("gray", "灰色"),
    ("red (cybernetic glow)", "红色（义眼发光）"),
]
OUTFIT_PALETTE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("navy and graphite", "海军蓝与石墨灰"),
    ("charcoal and steel", "炭灰与钢色"),
    ("white and cobalt", "白与钴蓝"),
    ("cream and brass", "米白与黄铜"),
    ("black and neon teal", "黑与霓虹青"),
    ("olive and sand", "橄榄绿与沙色"),
    ("crimson and slate", "深红与板岩灰"),
    ("orange and gunmetal", "橙与枪灰"),
]
MATERIAL_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("matte metal", "哑光金属"),
    ("brushed steel", "拉丝钢"),
    ("glossy polymer", "高光聚合物"),
    ("textured fabric", "纹理布料"),
    ("leather", "皮革"),
    ("carbon fiber", "碳纤维"),
    ("kevlar weave", "凯夫拉编织"),
]
APPAREL_DETAIL_OPTION_PAIRS = [
    ("tactical harness", "战术背带"),
    ("utility straps", "工具束带"),
    ("pilot gloves", "飞行员手套"),
    ("sleeve patches", "袖章"),
    ("collar insignia", "领章徽记"),
    ("high collar", "高领"),
    ("layered jacket", "叠穿夹克"),
    ("armored vest", "护甲背心"),
    ("panel seams", "拼接线"),
    ("cargo pockets", "工装口袋"),
    ("zipped sleeves", "拉链袖"),
    ("weathered fabric", "磨损布料"),
    ("hooded capelet", "短披风帽"),
    ("rolled sleeves", "卷起袖口"),
]
ACCESSORY_OPTION_PAIRS = [
    ("utility belt", "工具腰带"),
    ("shoulder pauldron", "肩甲"),
    ("rank badge", "军衔徽章"),
    ("wrist console", "腕部终端"),
    ("holster rig", "枪套"),
    ("capsule respirator", "呼吸器"),
    ("insignia pin", "徽章别针"),
    ("multi-tool", "多功能工具"),
    ("necklace tag", "识别吊牌"),
    ("ear cuff", "耳骨夹"),
    ("ring set", "戒指组"),
    ("armband", "臂环"),
    ("utility pouch", "工具小包"),
    ("data pad", "数据板"),
    ("camera drone", "侦察无人机"),
    ("headset", "耳机"),
    ("earring", "耳环"),
]
TECH_DETAIL_OPTION_PAIRS = [
    ("glowing circuit lines", "发光电路线"),
    ("holographic HUD panel", "全息 HUD 面板"),
    ("luminescent seams", "发光缝线"),
    ("energy core module", "能量核心模块"),
    ("micro-thruster pack", "微型推进器"),
    ("signal antenna", "信号天线"),
    ("magnetic clasps", "磁力搭扣"),
    ("cybernetic eye", "义眼"),
    ("neural interface ports", "神经接口端口"),
    ("data cable ports", "数据线端口"),
    ("optical HUD glow", "光学 HUD 发光"),
    ("powered gauntlet", "动力护臂"),
    ("exo brace", "外骨骼支架"),
    ("mechanical tubing", "机械管线"),
    ("hologram emitter", "全息投影器"),
    ("prosthetic arm", "义肢手臂"),
    ("earpiece communicator", "通讯耳机"),
    ("visor", "护目镜"),
]
MARKING_OPTION_PAIRS = [
    ("unit number stencil", "单位编号喷绘"),
    ("warning decals", "警示贴纸"),
    ("barcode tattoo", "条码纹身"),
    ("faction emblem tattoo", "阵营纹章纹身"),
    ("caution stripes", "警戒条纹"),
    ("serial number decal", "序列号贴"),
    ("maintenance markings", "维护标记"),
]

OPTIONS_CONFIG = _load_options_config()
GENDER_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "gender_options", GENDER_OPTION_PAIRS)
AGE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "age_options", AGE_OPTION_PAIRS)
FRAMING_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "framing_options", FRAMING_OPTION_PAIRS)
ASPECT_RATIO_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "aspect_ratio_options", ASPECT_RATIO_OPTION_PAIRS)
EXPRESSION_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "expression_options", EXPRESSION_OPTION_PAIRS)
GAZE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "gaze_options", GAZE_OPTION_PAIRS)
APPEARANCE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "appearance_features", APPEARANCE_OPTION_PAIRS)
BODY_TYPE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "body_type_options", BODY_TYPE_OPTION_PAIRS)
SKIN_TONE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "skin_tone_options", SKIN_TONE_OPTION_PAIRS)
HAIR_COLOR_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "hair_color_options", HAIR_COLOR_OPTION_PAIRS)
HAIR_STYLE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "hair_style_options", HAIR_STYLE_OPTION_PAIRS)
EYE_COLOR_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "eye_color_options", EYE_COLOR_OPTION_PAIRS)
OUTFIT_PALETTE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "outfit_palette_options", OUTFIT_PALETTE_OPTION_PAIRS)
MATERIAL_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "material_options", MATERIAL_OPTION_PAIRS)
APPAREL_DETAIL_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "apparel_details", APPAREL_DETAIL_OPTION_PAIRS)
ACCESSORY_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "accessories", ACCESSORY_OPTION_PAIRS)
TECH_DETAIL_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "tech_details", TECH_DETAIL_OPTION_PAIRS)
MARKING_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "markings", MARKING_OPTION_PAIRS)

GENDER_OPTIONS = _make_options(GENDER_OPTION_PAIRS)
AGE_OPTIONS = _make_options(AGE_OPTION_PAIRS)
FRAMING_OPTIONS = _make_options(FRAMING_OPTION_PAIRS)
ASPECT_RATIO_OPTIONS = _make_options(ASPECT_RATIO_OPTION_PAIRS)
EXPRESSION_OPTIONS = _make_options(EXPRESSION_OPTION_PAIRS)
GAZE_OPTIONS = _make_options(GAZE_OPTION_PAIRS)
APPEARANCE_OPTIONS = _make_options(APPEARANCE_OPTION_PAIRS)
BODY_TYPE_OPTIONS = _make_options(BODY_TYPE_OPTION_PAIRS)
SKIN_TONE_OPTIONS = _make_options(SKIN_TONE_OPTION_PAIRS)
HAIR_COLOR_OPTIONS = _make_options(HAIR_COLOR_OPTION_PAIRS)
HAIR_STYLE_OPTIONS = _make_options(HAIR_STYLE_OPTION_PAIRS)
EYE_COLOR_OPTIONS = _make_options(EYE_COLOR_OPTION_PAIRS)
OUTFIT_PALETTE_OPTIONS = _make_options(OUTFIT_PALETTE_OPTION_PAIRS)
MATERIAL_OPTIONS = _make_options(MATERIAL_OPTION_PAIRS)
APPAREL_DETAIL_OPTIONS = _make_options(APPAREL_DETAIL_OPTION_PAIRS)
ACCESSORY_OPTIONS = _make_options(ACCESSORY_OPTION_PAIRS)
TECH_DETAIL_OPTIONS = _make_options(TECH_DETAIL_OPTION_PAIRS)
MARKING_OPTIONS = _make_options(MARKING_OPTION_PAIRS)

GENDER_OPTION_MAP = _make_option_map(GENDER_OPTION_PAIRS)
AGE_OPTION_MAP = _make_option_map(AGE_OPTION_PAIRS)
FRAMING_OPTION_MAP = _make_option_map(FRAMING_OPTION_PAIRS)
ASPECT_RATIO_OPTION_MAP = _make_option_map(ASPECT_RATIO_OPTION_PAIRS)
EXPRESSION_OPTION_MAP = _make_option_map(EXPRESSION_OPTION_PAIRS)
GAZE_OPTION_MAP = _make_option_map(GAZE_OPTION_PAIRS)
APPEARANCE_OPTION_MAP = _make_option_map(APPEARANCE_OPTION_PAIRS)
BODY_TYPE_OPTION_MAP = _make_option_map(BODY_TYPE_OPTION_PAIRS)
SKIN_TONE_OPTION_MAP = _make_option_map(SKIN_TONE_OPTION_PAIRS)
HAIR_COLOR_OPTION_MAP = _make_option_map(HAIR_COLOR_OPTION_PAIRS)
HAIR_STYLE_OPTION_MAP = _make_option_map(HAIR_STYLE_OPTION_PAIRS)
EYE_COLOR_OPTION_MAP = _make_option_map(EYE_COLOR_OPTION_PAIRS)
OUTFIT_PALETTE_OPTION_MAP = _make_option_map(OUTFIT_PALETTE_OPTION_PAIRS)
MATERIAL_OPTION_MAP = _make_option_map(MATERIAL_OPTION_PAIRS)
APPAREL_DETAIL_OPTION_MAP = _make_option_map(APPAREL_DETAIL_OPTION_PAIRS)
ACCESSORY_OPTION_MAP = _make_option_map(ACCESSORY_OPTION_PAIRS)
TECH_DETAIL_OPTION_MAP = _make_option_map(TECH_DETAIL_OPTION_PAIRS)
MARKING_OPTION_MAP = _make_option_map(MARKING_OPTION_PAIRS)

PROFESSION_PRESETS: Dict[str, Dict[str, str]] = {
    "Space Pilot": {
        "role": "sci-fi space pilot",
        "outfit": "wearing a detailed retro-futuristic flight jacket with patches and mechanical tubing",
    },
    "Starship Engineer": {
        "role": "starship engineer",
        "outfit": "wearing a rugged utility jumpsuit with tool belts, worn fabric, and exposed cables",
    },
    "Bounty Hunter": {
        "role": "space bounty hunter",
        "outfit": "wearing reinforced leather armor with metal plates, ammo straps, and a tactical harness",
    },
    "Station Security": {
        "role": "space station security officer",
        "outfit": "wearing a compact armored uniform with insignia patches and a chest rig",
    },
    "Scientist": {
        "role": "sci-fi research scientist",
        "outfit": "wearing a sleek lab coat over a high-tech undersuit with subtle glowing seams",
    },
    "Navigator": {
        "role": "ship navigator",
        "outfit": "wearing a slim-fit flight suit with holographic map panels and navigation wrist gear",
    },
    "Smuggler": {
        "role": "space smuggler",
        "outfit": "wearing a weathered jacket, layered clothes, and hidden holsters",
    },
    "Medic": {
        "role": "space medic",
        "outfit": "wearing a compact medical vest with pouches, sterile gloves, and a visor",
    },
    "Mech Technician": {
        "role": "mech technician",
        "outfit": "wearing a grease-stained mechanic suit with heavy gloves and clamp tools",
    },
    "Explorer": {
        "role": "deep space explorer",
        "outfit": "wearing a layered survival suit with straps, rugged fabric, and oxygen tubing",
    },
    "Diplomat": {
        "role": "interstellar diplomat",
        "outfit": "wearing a tailored formal coat with minimalist futuristic accents",
    },
    "Android": {
        "role": "human-like android",
        "outfit": "wearing a clean synthetic bodysuit with subtle panel lines and circuit patterns",
    },
}


def get_profession_options() -> List[str]:
    return list(PROFESSION_PRESETS.keys())


def get_gender_options() -> List[str]:
    return GENDER_OPTIONS


def get_age_options() -> List[str]:
    return AGE_OPTIONS


def get_framing_options() -> List[str]:
    return FRAMING_OPTIONS


def get_aspect_ratio_options() -> List[str]:
    return ASPECT_RATIO_OPTIONS


def get_expression_options() -> List[str]:
    return EXPRESSION_OPTIONS


def get_gaze_options() -> List[str]:
    return GAZE_OPTIONS


def get_appearance_options() -> List[str]:
    return APPEARANCE_OPTIONS


def get_body_type_options() -> List[str]:
    return BODY_TYPE_OPTIONS


def get_skin_tone_options() -> List[str]:
    return SKIN_TONE_OPTIONS


def get_hair_color_options() -> List[str]:
    return HAIR_COLOR_OPTIONS


def get_hair_style_options() -> List[str]:
    return HAIR_STYLE_OPTIONS


def get_eye_color_options() -> List[str]:
    return EYE_COLOR_OPTIONS


def get_outfit_palette_options() -> List[str]:
    return OUTFIT_PALETTE_OPTIONS


def get_material_options() -> List[str]:
    return MATERIAL_OPTIONS


def get_apparel_detail_options() -> List[str]:
    return APPAREL_DETAIL_OPTIONS


def get_accessory_options() -> List[str]:
    return ACCESSORY_OPTIONS


def get_tech_detail_options() -> List[str]:
    return TECH_DETAIL_OPTIONS


def get_marking_options() -> List[str]:
    return MARKING_OPTIONS


def _format_subject(
    framing: str,
    gender: Optional[str],
    age: Optional[str],
    body_type: Optional[str],
    role: str,
    outfit: Optional[str],
    expression: str,
    gaze: str,
    appearance_features: List[str],
    apparel_details: List[str],
    markings: List[str],
    skin_tone: Optional[str],
    hair_style: Optional[str],
    hair_color: Optional[str],
    eye_color: Optional[str],
    outfit_palette: Optional[str],
    material_finish: Optional[str],
    accessories: List[str],
    tech_details: List[str],
) -> str:
    descriptors = []
    if age and age != "Unspecified":
        descriptors.append(age.lower())
    if gender and gender != "Unspecified":
        descriptors.append(gender.lower())
    if body_type and body_type != "Unspecified":
        descriptors.append(body_type.lower())

    descriptor_str = " ".join(descriptors)
    if descriptor_str:
        subject = f"a {descriptor_str} {role}"
    else:
        subject = f"a {role}"

    features = list(appearance_features)
    if skin_tone and skin_tone != "Unspecified":
        features.append(skin_tone)
    if hair_style and hair_style != "Unspecified":
        if hair_color and hair_color != "Unspecified":
            features.append(f"{hair_style} {hair_color} hair")
        else:
            features.append(f"{hair_style} hair")
    elif hair_color and hair_color != "Unspecified":
        features.append(f"{hair_color} hair")
    if eye_color and eye_color != "Unspecified":
        features.append(f"{eye_color} eyes")
    if apparel_details:
        features.extend(apparel_details)
    if markings:
        features.extend(markings)
    if accessories:
        features.extend(accessories)
    if tech_details:
        features.extend(tech_details)

    feature_text = ""
    if features:
        feature_text = " with " + ", ".join(features)

    outfit_text = f"{outfit}" if outfit else "wearing a retro-futuristic outfit"
    if outfit_palette and outfit_palette != "Unspecified":
        outfit_text = f"{outfit_text} in {outfit_palette} tones"
    if material_finish and material_finish != "Unspecified":
        outfit_text = f"{outfit_text}, featuring {material_finish} materials"

    return f"{framing}, {subject} {outfit_text}{feature_text}, {expression}, {gaze}."


def generate_character_prompt(
    gender: str,
    profession: str,
    age: str,
    framing: str,
    aspect_ratio: str,
    expression: str,
    gaze: str,
    appearance_features: List[str],
    apparel_details: List[str],
    markings: List[str],
    body_type: str,
    skin_tone: str,
    hair_style: str,
    hair_color: str,
    eye_color: str,
    outfit_palette: str,
    material_finish: str,
    accessories: List[str],
    tech_details: List[str],
    custom_profession: str = "",
    extra_modifiers: str = "",
) -> str:
    gender_value = _label_to_value(gender, GENDER_OPTION_MAP)
    age_value = _label_to_value(age, AGE_OPTION_MAP)
    framing_value = _label_to_value(framing, FRAMING_OPTION_MAP)
    aspect_ratio_value = _label_to_value(aspect_ratio, ASPECT_RATIO_OPTION_MAP)
    expression_value = _label_to_value(expression, EXPRESSION_OPTION_MAP)
    gaze_value = _label_to_value(gaze, GAZE_OPTION_MAP)
    body_type_value = _label_to_value(body_type, BODY_TYPE_OPTION_MAP)
    skin_tone_value = _label_to_value(skin_tone, SKIN_TONE_OPTION_MAP)
    hair_style_value = _label_to_value(hair_style, HAIR_STYLE_OPTION_MAP)
    hair_color_value = _label_to_value(hair_color, HAIR_COLOR_OPTION_MAP)
    eye_color_value = _label_to_value(eye_color, EYE_COLOR_OPTION_MAP)
    outfit_palette_value = _label_to_value(outfit_palette, OUTFIT_PALETTE_OPTION_MAP)
    material_finish_value = _label_to_value(material_finish, MATERIAL_OPTION_MAP)

    appearance_values = _labels_to_values(appearance_features, APPEARANCE_OPTION_MAP)
    apparel_values = _labels_to_values(apparel_details, APPAREL_DETAIL_OPTION_MAP)
    marking_values = _labels_to_values(markings, MARKING_OPTION_MAP)
    accessories_values = _labels_to_values(accessories, ACCESSORY_OPTION_MAP)
    tech_values = _labels_to_values(tech_details, TECH_DETAIL_OPTION_MAP)

    preset = PROFESSION_PRESETS.get(profession)
    has_custom_profession = bool(custom_profession.strip())
    role = custom_profession.strip() if has_custom_profession else (preset["role"] if preset else "sci-fi character")
    outfit = None if has_custom_profession else (preset["outfit"] if preset else None)

    subject_line = _format_subject(
        framing=framing_value,
        gender=gender_value,
        age=age_value,
        body_type=body_type_value,
        role=role,
        outfit=outfit,
        expression=expression_value,
        gaze=gaze_value,
        appearance_features=appearance_values,
        apparel_details=apparel_values,
        markings=marking_values,
        skin_tone=skin_tone_value,
        hair_style=hair_style_value,
        hair_color=hair_color_value,
        eye_color=eye_color_value,
        outfit_palette=outfit_palette_value,
        material_finish=material_finish_value,
        accessories=accessories_values,
        tech_details=tech_values,
    )

    ratio_line = ""
    if aspect_ratio_value and aspect_ratio_value != "Unspecified":
        ratio_line = f"aspect ratio {aspect_ratio_value.split()[0]}."

    extra_line = extra_modifiers.strip()

    style_cfg = _load_style_config()
    parts = [style_cfg["style"], "", subject_line]
    if ratio_line:
        parts.extend(["", ratio_line])
    parts.extend(["", style_cfg["background"], "", style_cfg["mood"]])
    if extra_line:
        parts.extend(["", extra_line])

    return "\n".join(parts).strip() + "\n"
