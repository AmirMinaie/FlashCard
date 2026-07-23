def get_progress_color(value):
    """
    Range: 0 - 150
    Returns 10 color levels
    """
    value = 100 * value

    colors = [
        (0.8, 0.0, 0.0, 1),   # 0   Red
        (0.8, 0.2, 0.0, 1),   # 15
        (0.8, 0.4, 0.0, 1),   # 30
        (0.8, 0.6, 0.0, 1),   # 45
        (0.8, 0.8, 0.0, 1),   # 60
        (0.6, 0.8, 0.0, 1),   # 75
        (0.4, 0.8, 0.0, 1),   # 90
        (0.2, 0.8, 0.0, 1),   # 105
        (0.0, 0.8, 0.2, 1),   # 120
        (0.0, 0.8, 0.0, 1),   # 135+
    ]

    # محدود کردن مقدار
    value = max(0, min(value, 150))

    # تعیین سطح رنگ
    index = int(value / 15)

    # جلوگیری از خارج شدن از لیست
    index = min(index, len(colors) - 1)

    return colors[index]