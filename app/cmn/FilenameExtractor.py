from urllib.parse import urlparse, unquote
from pathlib import Path
from cmn.config_reader import ConfigReader
import os
import re

class FilenameExtractor:
    @staticmethod
    def extract_filename(url):
        """
        استخراج نام فایل از URL با قابلیت‌های پیشرفته
        """
        try:
            # حذف فضاهای اضافی
            url = url.strip()
            
            # تجزیه URL
            parsed = urlparse(url)
            
            # گرفتن path
            path = parsed.path
            
            # اگر path خالی باشد، از netloc استفاده کن (برای URL‌های خاص)
            if not path:
                # برای URL‌هایی مثل: http://example.com/file.mp3?param=value
                # یا URL‌های بدون path
                return None
            
            # حذف query parameters و fragments
            path = path.split('?')[0].split('#')[0]
            
            # decode کردن کاراکترهای خاص
            path = unquote(path)
            
            # استخراج نام فایل
            filename = Path(path).name
            
            # بررسی معتبر بودن نام فایل
            if not filename or filename == '.' or filename == '..':
                return None
            
            # حذف کاراکترهای غیرمجاز از نام فایل
            filename = FilenameExtractor._sanitize_filename(filename)
            
            return filename if filename else None
            
        except Exception as e:
            print(f"Error extracting filename from URL: {e}")
            return None
    
    @staticmethod
    def extract_filename_with_fallback(url, default_name="audio_file"):
        """
        استخراج نام فایل با fallback name در صورت عدم موفقیت
        """
        filename = FilenameExtractor.extract_filename(url)
        
        if filename:
            return filename
        
        # اگر نام فایل پیدا نشد، از URL سعی کن نامی بسازی
        try:
            parsed = urlparse(url)
            
            # از domain یا path برای ساخت نام استفاده کن
            if parsed.netloc:
                # گرفتن نام دامنه بدون www
                domain = parsed.netloc.replace('www.', '').split('.')[0]
                return f"{domain}_audio.mp3"
            elif parsed.path:
                # استفاده از آخرین بخش path
                path_parts = parsed.path.strip('/').split('/')
                if path_parts:
                    return f"{path_parts[-1]}.mp3"
            
        except:
            pass
        
        return f"{default_name}.mp3"
    
    @staticmethod
    def extract_extension(url):
        """استخراج پسوند فایل از URL"""
        filename = FilenameExtractor.extract_filename(url)
        if filename:
            ext = Path(filename).suffix.lower()
            return ext if ext else None
        return None
    
    @staticmethod
    def _sanitize_filename(filename):
        """پاکسازی نام فایل از کاراکترهای غیرمجاز"""
        # حذف کاراکترهای غیرمجاز
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # حذف فضاهای اضافی
        filename = filename.strip()
        
        # محدود کردن طول نام فایل
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        
        return filename
    
    @staticmethod
    def get_file_type(url):
        """بررسی اینکه آیا URL به یک فایل صوتی اشاره می‌کند"""
        extensions = ConfigReader()
        extension = FilenameExtractor.extract_extension(url)
        category = ''
        for format in extensions.get('Valid_file_format_mapping'):
            if format['extension'] == extension.lower():
                return format['category']
            
        return 'unknow'