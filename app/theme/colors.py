from kivy.utils import get_color_from_hex
from kivy.properties import DictProperty

class AppColors:    
    PRIMARY = {
        "50": get_color_from_hex("#E3F2FD"),
        "100": get_color_from_hex("#BBDEFB"),
        "200": get_color_from_hex("#90CAF9"),
        "300": get_color_from_hex("#64B5F6"),
        "400": get_color_from_hex("#42A5F5"),
        "500": get_color_from_hex("#2196F3"),  # رنگ اصلی
        "600": get_color_from_hex("#1E88E5"),
        "700": get_color_from_hex("#1976D2"),
        "800": get_color_from_hex("#1565C0"),
        "900": get_color_from_hex("#0D47A1"),
    }
    
    ACCENT = {
        "A100": get_color_from_hex("#82B1FF"),
        "A200": get_color_from_hex("#448AFF"),
        "A400": get_color_from_hex("#2979FF"),
        "A700": get_color_from_hex("#2962FF"),
    }
    
    SYSTEM = {
        "success": get_color_from_hex("#4CAF50"),
        "warning": get_color_from_hex("#FF9800"),
        "error": get_color_from_hex("#F44336"),
        "info": get_color_from_hex("#2196F3"),
    }
    
    LIGHT_THEME = {
        "background": get_color_from_hex("#FFFFFF"),
        "surface": get_color_from_hex("#F5F5F5"),
        "on_background": get_color_from_hex("#000000"),
        "on_surface": get_color_from_hex("#212121"),
        "border": get_color_from_hex("#E0E0E0"),
        "divider": get_color_from_hex("#EEEEEE"),
        "disabled": get_color_from_hex("#9E9E9E"),
    }
    
    DARK_THEME = {
        "background": get_color_from_hex("#121212"),
        "surface": get_color_from_hex("#1E1E1E"),
        "on_background": get_color_from_hex("#FFFFFF"),
        "on_surface": get_color_from_hex("#E0E0E0"),
        "border": get_color_from_hex("#424242"),
        "divider": get_color_from_hex("#303030"),
        "disabled": get_color_from_hex("#757575"),
    }
    
    @classmethod
    def get_theme_colors(cls, theme_style="Light"):
        return cls.LIGHT_THEME if theme_style == "Light" else cls.DARK_THEME
    
    @classmethod
    def get_color(cls, color_type, shade="500"):
        if color_type == "primary":
            return cls.PRIMARY.get(shade, cls.PRIMARY["500"])
        elif color_type == "accent":
            return cls.ACCENT.get(shade, cls.ACCENT["A200"])
        elif color_type == "system":
            return cls.SYSTEM.get(shade, cls.SYSTEM["info"])