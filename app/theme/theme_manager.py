# theme/theme_manager.py
from kivymd.theming import ThemeManager
from kivy.properties import (
    ColorProperty, StringProperty, DictProperty,
    NumericProperty, BooleanProperty, ObjectProperty
)
from .colors import AppColors
from .typography import Typography

class AppThemeManager(ThemeManager):
    """مدیر تم سفارشی برنامه"""
    
    # رنگ‌های سفارشی
    success_color = ColorProperty(AppColors.SYSTEM["success"])
    warning_color = ColorProperty(AppColors.SYSTEM["warning"])
    error_color = ColorProperty(AppColors.SYSTEM["error"])
    info_color = ColorProperty(AppColors.SYSTEM["info"])
    
    # رنگ‌های سفارشی برای primary و accent
    custom_primary = ColorProperty(AppColors.PRIMARY["500"])
    custom_accent = ColorProperty(AppColors.ACCENT["A200"])
    
    # رنگ‌های border
    border_color = ColorProperty(AppColors.LIGHT_THEME["border"])
    border_color_focused = ColorProperty(AppColors.PRIMARY["500"])
    
    # رنگ‌های surface
    card_background = ColorProperty(AppColors.LIGHT_THEME["surface"])
    dialog_background = ColorProperty(AppColors.LIGHT_THEME["background"])
    
    # سایه‌ها
    shadow_color = ColorProperty([0, 0, 0, 0.1])
    elevation_small = NumericProperty(2)
    elevation_medium = NumericProperty(4)
    elevation_large = NumericProperty(8)
    
    # انیمیشن‌ها
    animation_duration = NumericProperty(0.2)
    animation_transition = StringProperty("out_quad")
    
    # radiusها
    radius_small = NumericProperty(4)
    radius_medium = NumericProperty(8)
    radius_large = NumericProperty(12)
    radius_xlarge = NumericProperty(16)
    
    # paddingها
    padding_small = NumericProperty(8)
    padding_medium = NumericProperty(16)
    padding_large = NumericProperty(24)
    
    # spacingها
    spacing_small = NumericProperty(8)
    spacing_medium = NumericProperty(16)
    spacing_large = NumericProperty(24)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # تنظیم پالت رنگ‌های پیش‌فرض
        self.primary_palette = "Blue"
        self.accent_palette = "Orange"
        self.theme_style = "Light"
        
        self._update_theme_colors()
        
        # رجیستر کردن فونت‌های سفارشی
        self._register_custom_fonts()
        
    def _register_custom_fonts(self):
        """ثبت فونت‌های سفارشی"""
        from kivy.core.text import LabelBase
        
        # رجیستر فونت‌ها (اگر فایل فونت دارید)
        try:
            LabelBase.register(
                name=Typography.FONT_FAMILY["regular"],
                fn_regular="assets/fonts/Roboto-Regular.ttf"
            )
            LabelBase.register(
                name=Typography.FONT_FAMILY["medium"],
                fn_regular="assets/fonts/Roboto-Medium.ttf"
            )
            LabelBase.register(
                name=Typography.FONT_FAMILY["bold"],
                fn_regular="assets/fonts/Roboto-Bold.ttf"
            )
        except:
            pass  # اگر فونت‌ها موجود نبودند، از فونت پیش‌فرض استفاده می‌شود
    
    def _update_theme_colors(self):
        """بروزرسانی رنگ‌ها بر اساس تم"""
        theme_colors = AppColors.get_theme_colors(self.theme_style)
        
        # به‌روزرسانی رنگ‌های پویا
        self.border_color = theme_colors["border"]
        self.card_background = theme_colors["surface"]
        self.dialog_background = theme_colors["background"]
        
        # به‌روزرسانی custom colors
        self.custom_primary = AppColors.PRIMARY["500"]
        self.custom_accent = AppColors.ACCENT["A200"]
        
        # به‌روزرسانی font_styles
        self.font_styles.update(Typography.FONT_STYLES)
    
    def on_theme_style(self, instance, value):
        """هنگام تغییر تم"""
        super().on_theme_style(instance, value)
        self._update_theme_colors()
    
    def toggle_theme(self):
        """تغییر بین تم روشن و تاریک"""
        self.theme_style = "Dark" if self.theme_style == "Light" else "Light"
    
    def set_primary_color(self, color_name, shade="500"):
        """تنظیم رنگ primary"""
        if color_name in ["Red", "Pink", "Purple", "DeepPurple", "Indigo",
                         "Blue", "LightBlue", "Cyan", "Teal", "Green",
                         "LightGreen", "Lime", "Yellow", "Amber", "Orange",
                         "DeepOrange", "Brown", "Gray", "BlueGray"]:
            self.primary_palette = color_name
            self.primary_hue = shade
        else:
            # اگر رنگ سفارشی است
            self.custom_primary = AppColors.get_color(color_name, shade)
    
    def set_accent_color(self, color_name, shade="A200"):
        """تنظیم رنگ accent"""
        if color_name in ["Red", "Pink", "Purple", "DeepPurple", "Indigo",
                         "Blue", "LightBlue", "Cyan", "Teal", "Green",
                         "LightGreen", "Lime", "Yellow", "Amber", "Orange",
                         "DeepOrange"]:
            self.accent_palette = color_name
            self.accent_hue = shade
        else:
            # اگر رنگ سفارشی است
            self.custom_accent = AppColors.get_color(color_name, shade)
    
    def get_color(self, color_name, shade="500"):
        """دریافت رنگ به صورت داینامیک"""
        return AppColors.get_color(color_name, shade)
    
    def get_current_theme_colors(self):
        """دریافت رنگ‌های تم فعلی"""
        return AppColors.get_theme_colors(self.theme_style)
    
    @property
    def primary_color_rgba(self):
        """دریافت رنگ primary به صورت RGBA"""
        return self.custom_primary
    
    @property
    def accent_color_rgba(self):
        """دریافت رنگ accent به صورت RGBA"""
        return self.custom_accent