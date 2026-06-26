import ctypes
from ctypes import wintypes
from urllib.parse import urlparse
from cmn.config_reader import ConfigReader
import logging


class NetworkClient:
    def __init__(self):
        self.backend = ConfigReader().get("network_backend")

        if self.backend == "wininet":
            self._init_wininet()

    # ---------------------------
    # PUBLIC METHOD
    # ---------------------------
    def download(self, url, file_path):
        if self.backend == "requests":
            return self._download_requests(url, file_path)
        elif self.backend == "wininet":
            return self._download_wininet(url, file_path)
        else:
            raise ValueError("Unknown backend")

    # ---------------------------
    # REQUESTS (fallback)
    # ---------------------------
    def _download_requests(self, url, file_path):
        import requests
        from fake_useragent import UserAgent

        try:
            session = requests.Session()

            response = session.get(
                url,
                stream=True,
                timeout=30,
                headers={"User-Agent": UserAgent().random}
            )
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            return {
                "success": True,
                "size": file_path.stat().st_size if hasattr(file_path, "stat") else None
            }

        except Exception as e:
            logging.error(e)
            return {"success": False, "error": str(e)}

    # ---------------------------
    # WININET INIT
    # ---------------------------
    def _init_wininet(self):
        self.wininet = ctypes.WinDLL("wininet")

        self.InternetOpen = self.wininet.InternetOpenW
        self.InternetOpen.restype = wintypes.HANDLE

        self.InternetOpenUrl = self.wininet.InternetOpenUrlW
        self.InternetOpenUrl.restype = wintypes.HANDLE

        self.InternetReadFile = self.wininet.InternetReadFile
        self.InternetReadFile.restype = wintypes.BOOL

        self.INTERNET_OPEN_TYPE_PRECONFIG = 0

    # ---------------------------
    # WININET DOWNLOAD
    # ---------------------------
    def _download_wininet(self, url, file_path):
        try:
            hInternet = self.InternetOpen(
                "Mozilla/5.0",
                self.INTERNET_OPEN_TYPE_PRECONFIG,
                None,
                None,
                0
            )

            if not hInternet:
                return {"success": False, "error": "InternetOpen failed"}

            hUrl = self.InternetOpenUrl(
                hInternet,
                url,
                None,
                0,
                0,
                0
            )

            if not hUrl:
                return {"success": False, "error": "InternetOpenUrl failed"}

            buffer = ctypes.create_string_buffer(8192)
            read = wintypes.DWORD()

            with open(file_path, "wb") as f:
                while True:
                    result = self.InternetReadFile(
                        hUrl,
                        buffer,
                        len(buffer),
                        ctypes.byref(read)
                    )

                    if not result or read.value == 0:
                        break

                    f.write(buffer.raw[:read.value])

            return {
                "success": True,
                "file_path": str(file_path)
            }

        except Exception as e:
            logging.error(e)
            return {"success": False, "error": str(e)}