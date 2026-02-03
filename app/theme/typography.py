from kivy.metrics import sp

class Typography:
    
    FONT_FAMILY = {
        "regular": "Roboto",
        "medium": "RobotoMedium",
        "bold": "RobotoBold",
        "light": "RobotoLight",
    }
    
    FONT_SIZES = {
        "display_large": sp(57),
        "display_medium": sp(45),
        "display_small": sp(36),
        "headline_large": sp(32),
        "headline_medium": sp(28),
        "headline_small": sp(24),
        "title_large": sp(22),
        "title_medium": sp(16),
        "title_small": sp(14),
        "body_large": sp(16),
        "body_medium": sp(14),
        "body_small": sp(12),
        "label_large": sp(14),
        "label_medium": sp(12),
        "label_small": sp(11),
    }
    
    FONT_STYLES = {
        "DisplayLarge": [FONT_FAMILY["regular"], FONT_SIZES["display_large"], 0, -0.25],
        "DisplayMedium": [FONT_FAMILY["regular"], FONT_SIZES["display_medium"], 0, 0],
        "DisplaySmall": [FONT_FAMILY["regular"], FONT_SIZES["display_small"], 0, 0],
        "HeadlineLarge": [FONT_FAMILY["regular"], FONT_SIZES["headline_large"], 0, 0],
        "HeadlineMedium": [FONT_FAMILY["regular"], FONT_SIZES["headline_medium"], 0, 0],
        "HeadlineSmall": [FONT_FAMILY["regular"], FONT_SIZES["headline_small"], 0, 0],
        "TitleLarge": [FONT_FAMILY["medium"], FONT_SIZES["title_large"], 0, 0],
        "TitleMedium": [FONT_FAMILY["medium"], FONT_SIZES["title_medium"], 0.15, 0],
        "TitleSmall": [FONT_FAMILY["medium"], FONT_SIZES["title_small"], 0.1, 0],
        "BodyLarge": [FONT_FAMILY["regular"], FONT_SIZES["body_large"], 0.5, 0],
        "BodyMedium": [FONT_FAMILY["regular"], FONT_SIZES["body_medium"], 0.25, 0],
        "BodySmall": [FONT_FAMILY["regular"], FONT_SIZES["body_small"], 0.4, 0],
        "LabelLarge": [FONT_FAMILY["medium"], FONT_SIZES["label_large"], 0.1, 0.5],
        "LabelMedium": [FONT_FAMILY["medium"], FONT_SIZES["label_medium"], 0.4, 0.5],
        "LabelSmall": [FONT_FAMILY["medium"], FONT_SIZES["label_small"], 0.5, 0.5],
    }