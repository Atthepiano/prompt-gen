"""手工运行：python -m tests.dump_snapshot

输出可直接粘到 test_generators_snapshot.py 的 EXPECTED 常量里。
仅在确认 prompt 模板调整是预期变化后使用。
"""
import hashlib
import random


def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _first(opts):
    return opts[0] if opts else ""


def main():
    import character_generator as cg
    import clothing_generator as clg
    import prompt_generator as pg

    random.seed(42)
    print("SPACESHIP_EXPECTED = {")
    for cat, subs in pg.get_component_map().items():
        if not subs:
            continue
        sub = subs[0]
        for tier in pg.get_tier_list():
            out = pg.generate_prompt_by_strings(
                tier, cat, sub, "#445566", "#FFAA00", "None", "None"
            )
            print(f'    "{cat}|{tier}|{sub}": "{_h(out)}",')
    print("}\n")

    lang = "en"
    char_out = cg.generate_character_prompt(
        gender=_first(cg.get_gender_options(lang)), age=25,
        framing=_first(cg.get_framing_options(lang)),
        aspect_ratio=_first(cg.get_aspect_ratio_options(lang)),
        expression=_first(cg.get_expression_options(lang)),
        gaze=_first(cg.get_gaze_options(lang)),
        appearance_features=[],
        body_type=_first(cg.get_body_type_options(lang)),
        skin_tone=_first(cg.get_skin_tone_options(lang)),
        hair_style=_first(cg.get_hair_style_options(lang)),
        hair_color=_first(cg.get_hair_color_options(lang)),
        hair_colors=[],
        hair_bangs_presence=_first(cg.get_bangs_presence_options(lang)),
        hair_bangs_style=_first(cg.get_bangs_style_options(lang)),
        face_shape=_first(cg.get_face_shape_options(lang)),
        eye_size=_first(cg.get_eye_size_options(lang)),
        nose_size=_first(cg.get_nose_size_options(lang)),
        mouth_shape=_first(cg.get_mouth_shape_options(lang)),
        cheek_fullness=_first(cg.get_cheek_fullness_options(lang)),
        jaw_width=_first(cg.get_jaw_width_options(lang)),
        eye_color=_first(cg.get_eye_color_options(lang)),
        clothing_hint=_first(cg.get_clothing_hint_options(lang)),
        artists=[], lang=lang,
    )
    print(f'CHARACTER_DEFAULT_EN = "{_h(char_out)}"')

    cloth_out = clg.generate_clothing_preset_prompt(
        faction=_first(clg.get_faction_options(lang)),
        gender=_first(clg.get_gender_options(lang)),
        role=_first(clg.get_role_options(lang)),
        outfit_category=_first(clg.get_outfit_category_options(lang)),
        silhouette=_first(clg.get_silhouette_options(lang)),
        layering=_first(clg.get_layering_options(lang)),
        material=_first(clg.get_material_options(lang)),
        palette=_first(clg.get_palette_options(lang)),
        wear_state=_first(clg.get_wear_state_options(lang)),
        presentation=_first(clg.get_presentation_options(lang)),
        pose=_first(clg.get_pose_options(lang)),
        view_mode=_first(clg.get_view_mode_options(lang)),
        aspect_ratio=_first(clg.get_aspect_ratio_options(lang)),
        detail_accents=[], accessories=[], insignia=[], lang=lang,
    )
    print(f'CLOTHING_DEFAULT_EN = "{_h(cloth_out)}"')


if __name__ == "__main__":
    main()
