import os
import uuid
import shutil
from pathlib import Path
import logging
from datetime import datetime
from cmn.resource_helper import resource_path
from cmn.FilenameExtractor import FilenameExtractor
from fake_useragent import UserAgent
import requests
from urllib.parse import urlparse, unquote

class FileManager:
    def __init__(self, base_directory="files"):
        self.base_dir = Path(resource_path(base_directory))
        self.base_dir.mkdir(exist_ok=True)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def generate_unique_id(self):
        return str(uuid.uuid4())
    
    def save_file(self, source_path, source_type="local"):
        """
        save file and return direction
        
        Args:
            source_path:
            source_type:(local, online)
        
        Returns:
            dict: direction dave file
        """
        try:
            file_id = self.generate_unique_id()
            etention = FilenameExtractor.extract_extension(source_path)
            file_path = None
            
            if source_type == 'online':
                file_path = self.download_online(source_path , file_id + etention)
            elif source_type == 'local':
                file_path = self.copy_file(source_path , file_id)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")

            fileName = FilenameExtractor.extract_filename(source_path)
            file_size = os.path.getsize(file_path['file_path'])
            type_ = FilenameExtractor.get_file_type(file_path['file_name'])
            
            return {
                'file_id': file_id,
                'filePath': file_id + etention,
                'fileName': fileName,
                'fileSize': file_size,
                'sourceType': source_type,
                'type_': type_
            }
            
        except Exception as e:
            logging.error(f"Error saving audio file: {e}")
            raise
    
    def delete_audio_file(self, file_path):
        """حذف فایل صوتی"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logging.error(f"Error deleting audio file: {e}")
            return False
    
    def cleanup_temp_files(self):
        """پاکسازی فایل‌های موقت"""
        temp_dir = self.sub_dirs['temp']
        for file in temp_dir.glob("*"):
            try:
                # حذف فایل‌های قدیمی‌تر از ۲۴ ساعت
                file_age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
                if file_age.total_seconds() > 24 * 3600:
                    file.unlink()
            except Exception as e:
                logging.warning(f"Could not delete temp file {file}: {e}")

    def download_online(self, source_path , filename , timeout=30 ):
        """
        دانلود فایل از URL
        
        Args:
            source_path: آدرس فایل
            filename: نام فایل (اختیاری)
            timeout: زمان انتظار
        
        Returns:
            dict: اطلاعات فایل دانلود شده
        """
        try:
            session = requests.Session()
            
            response = session.get(source_path, stream=True, timeout=timeout , headers=self.headers())
            response.raise_for_status() 

            # مسیر کامل فایل
            file_path = self.base_dir / filename
            
            # ذخیره فایل
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            
            file_size = os.path.getsize(file_path)
            
            return {
                'success': True,
                'url': source_path,
                'file_path': str(file_path),
                'file_name': filename,
                'file_size': file_size
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'url': filename
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP Error: {e}',
                'url': filename,
                'status_code': e.response.status_code if hasattr(e, 'response') else None
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request Error: {e}',
                'url': filename
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected Error: {e}',
                'url': filename
            }

    def copy_file(self,source_path , file_id ):
        pass

    def headers(self):
        """ایجاد headers معتبر برای Cambridge Dictionary"""
        ua = UserAgent()
        return {
            'User-Agent': ua.random,
            'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://dictionary.cambridge.org/',
            'Sec-Fetch-Dest': 'audio',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }