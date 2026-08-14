from app.cmn import AppName
import sys

if len(sys.argv) > 1 and sys.argv[1]:
    AppName.APP_NAME = sys.argv[1]
print(f"Environment: {AppName.APP_NAME}")

from app.cmn.splash_screen import SplashScreen
splash = SplashScreen()
splash.show()

from app.startup import initialize_application
from app.app import FlashCardApp
from app.cmn.logger import logger


if __name__ == "__main__":
    logger.info("Starting FlashCard Application...")
    try:
        initialize_application()
        app = FlashCardApp(splash=splash)
        app.run()

    except Exception as e:
        logger.exception(f"❌ Error initializing database: {e}")
        sys.exit(1)