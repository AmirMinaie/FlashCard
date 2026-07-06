import os
import uuid
import shutil
from pathlib import Path
import logging
from datetime import datetime
from cmn.resource_helper import PathManager
from cmn.FilenameExtractor import FilenameExtractor
from fake_useragent import UserAgent
from cmn.NetworkClient import NetworkClient
from urllib.parse import urlparse, unquote
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError, TDRC
from cmn.logger import logger
from cmn.config_reader import ConfigReader

class FileManager:
    def __init__(self):
        self.AppName = ConfigReader().get("App_Name")
        self.base_dir = Path(PathManager.bundled_path(PathManager.FILES_DIR))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.network = NetworkClient()

    @classmethod
    def getfilepath(self,fileName):
        return str(PathManager.FILES_DIR / fileName)

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
            self.set_metadata(file_path['file_path'] , fileName ,self.AppName )
            
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
        file_path = self.base_dir / filename

        result = self.network.download(source_path, file_path)

        if not result.get("success"):
            raise Exception(result.get("error"))
        


        return {
            "success": True,
            'url': source_path,
            "file_path": str(file_path),
            "file_name": filename,
            "file_size": file_path.stat().st_size 
            }

    def copy_file(self,source_path , file_id ):
        source = Path(source_path)

        extension = source.suffix

        destination = self.base_dir / f"{filename}{extension}"

        shutil.copy2(source, destination)

        return {
            "success": True,
            "file_path": str(destination),
            "file_name": destination.name,
            "file_size": destination.stat().st_size
        }

    def headers(self, url):
        parsed = urlparse(url)
    
        return {
            "User-Agent": UserAgent().random,
            "Referer": f"{parsed.scheme}://{parsed.netloc}/",
            "Origin": f"{parsed.scheme}://{parsed.netloc}",
            "Host": parsed.netloc,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
    
    def set_metadata(self,file_path, title=None, author=None):
        try:
            now = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            try:
                audio = EasyID3(file_path)
            except ID3NoHeaderError:
                audio = EasyID3()
                audio.save(file_path)
                audio = EasyID3(file_path)

            if title:
                audio["title"] = title

            if author:
                audio["artist"] = author 

            audio.save()

            id3 = ID3(file_path)

            id3.add(TDRC(encoding=3, text=now))
            id3.save()

            logger.info(f"Metadata set successfully for {file_path}: {file_path}")
            return {
                "success": True,
                "result": file_path
            }

        except Exception as e:
            logger.exception(f"Failed to set metadata for {file_path}")
            return {
                "success": False,
                "error": str(e)
            }