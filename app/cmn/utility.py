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

def format_time(seconds):
    seconds = int(round(seconds))  
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"  
    if minutes > 0:
        return f"{minutes}m {secs}s"   
    return f"{secs}s"

def format_days(days: int) -> str:
    if days <= 0:
        return "No Start"
    years = days // 365
    days %= 365
    months = days // 30
    days %= 30
    parts = []
    if years:
        parts.append(f"{years} Year" if years == 1 else f"{years} Years")
    if months:
        parts.append(f"{months} Month" if months == 1 else f"{months} Months")
    if days:
        parts.append(f"{days} Day" if days == 1 else f"{days} Days")
    return " ".join(parts)