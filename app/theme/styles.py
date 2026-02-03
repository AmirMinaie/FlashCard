# theme/styles.py
from kivy.lang import Builder
from kivy.metrics import dp
from .colors import AppColors

# بارگذاری استایل‌های KV
KV_STYLES = """
#:import colors theme.colors.AppColors
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp

<AppTextField@MDTextField>:
    size_hint_y: None
    height: dp(56)
    line_color_normal: app.theme_cls.border_color
    line_color_focus: app.theme_cls.border_color_focused
    hint_text_color: colors.LIGHT_THEME.disabled if app.theme_cls.theme_style == "Light" else colors.DARK_THEME.disabled
    text_color: colors.LIGHT_THEME.on_surface if app.theme_cls.theme_style == "Light" else colors.DARK_THEME.on_surface
    font_name: app.theme_cls.font_styles["BodyMedium"][0]
    font_size: sp(14)
    padding: [dp(12), dp(16)]
    radius: [dp(4), dp(4), 0, 0]
    mode: "rectangle"
    
    canvas.before:
        Color:
            rgba: app.theme_cls.card_background
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius

<AppButton@MDRaisedButton>:
    size_hint_y: None
    height: dp(48)
    font_name: app.theme_cls.font_styles["LabelLarge"][0]
    font_size: sp(14)
    md_bg_color: app.theme_cls.primary_color
    text_color: 1, 1, 1, 1
    elevation_normal: app.theme_cls.elevation_small
    radius: app.theme_cls.radius_medium
    padding: [dp(24), dp(12)]

<AppIconButton@MDIconButton>:
    icon_size: dp(24)
    theme_icon_color: "Custom"
    icon_color: app.theme_cls.primary_color if not self.disabled else app.theme_cls.disabled_hint_text_color
    size_hint: None, None
    size: dp(48), dp(48)
    radius: dp(24)

<AppCard@MDCard>:
    size_hint: None, None
    elevation: app.theme_cls.elevation_medium
    radius: app.theme_cls.radius_medium
    padding: app.theme_cls.padding_medium
    spacing: app.theme_cls.spacing_small
    md_bg_color: app.theme_cls.card_background

<AppDialog@MDDialog>:
    size_hint: [0.9, None]
    height: dp(300)
    radius: [app.theme_cls.radius_large, app.theme_cls.radius_large, app.theme_cls.radius_large, app.theme_cls.radius_large]
    md_bg_color: app.theme_cls.dialog_background
    
<AppToolbar@MDToolbar>:
    elevation: app.theme_cls.elevation_medium
    md_bg_color: app.theme_cls.primary_color
    specific_text_color: 1, 1, 1, 1
    left_action_items: [["menu", lambda x: None]]
    right_action_items: []
    
<AppSnackbar@MDSnackbar>:
    size_hint_x: 0.9
    pos_hint: {"center_x": 0.5}
    radius: [app.theme_cls.radius_medium, app.theme_cls.radius_medium, app.theme_cls.radius_medium, app.theme_cls.radius_medium]
    md_bg_color: app.theme_cls.card_background
    
<AppSwitch@MDSwitch>:
    width: dp(64)
    active: False
    
<AppCheckbox@MDCheckbox>:
    size_hint: None, None
    size: dp(48), dp(48)
    
<AppProgressBar@MDProgressBar>:
    height: dp(4)
"""

# بارگذاری استایل‌ها
def load_styles():
    """بارگذاری استایل‌ها در برنامه"""
    Builder.load_string(KV_STYLES)