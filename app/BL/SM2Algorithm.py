from datetime import datetime, timedelta

class SM2Algorithm:
    """پیاده‌سازی کامل الگوریتم SM-2"""
    
    MIN_EASE = 1.3
    MAX_EASE = 5.0
    INITIAL_EASE = 2.5
    
    @classmethod
    def calculate_review(cls, 
                         current_ease: float,
                         current_interval: int,
                         current_repetitions: int,
                         quality: int) -> dict:
        """
        محاسبه پارامترهای مرور بعدی
        
        Args:
            current_ease: فاکتور سهولت فعلی
            current_interval: فاصله فعلی (روز)
            current_repetitions: تعداد مرورهای موفق
            quality: کیفیت پاسخ (0-5)
            
        Returns:
            dict: پارامترهای جدید
        """
        # 1. محاسبه ease factor جدید
        new_ease = cls._calculate_new_ease(current_ease, quality)
        
        # 2. محاسبه interval و repetitions جدید
        if quality < 3:  # پاسخ ضعیف
            new_interval = 1
            new_repetitions = 0
        else:  # پاسخ خوب
            new_repetitions = current_repetitions + 1
            new_interval = cls._calculate_new_interval(
                current_interval, new_ease, new_repetitions
            )
        
        # 3. محاسبه تاریخ مرور بعدی
        next_review_date = datetime.now() + timedelta(days=new_interval)
        
        return {
            'ease_factor': new_ease,
            'interval': new_interval,
            'repetitions': new_repetitions,
            'next_review': next_review_date
        }
    
    @staticmethod
    def _calculate_new_ease(current_ease: float, quality: int) -> float:
        """محاسبه ease factor جدید"""
        # فرمول SM-2
        new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # محدود کردن به بازه 1.3 تا 5.0
        new_ease = max(SM2Algorithm.MIN_EASE, 
                      min(SM2Algorithm.MAX_EASE, new_ease))
        
        # گرد کردن به ۲ رقم اعشار
        return round(new_ease, 2)
    
    @staticmethod
    def _calculate_new_interval(current_interval: int, 
                               new_ease: float, 
                               new_repetitions: int) -> int:
        """محاسبه interval جدید"""
        if new_repetitions == 1:
            return 1  # روز بعد
        elif new_repetitions == 2:
            return 6  # 6 روز بعد
        else:
            # برای مرورهای بعدی
            return int(current_interval * new_ease + 0.5)  # گرد کردن به نزدیکترین عدد صحیح