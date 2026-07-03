import os
import importlib
from cmn.resource_helper import *
from ..base import Base

from .constantDA import constantDA
from .fileFlashcardDA import fileFlashcardDA
from .flashcardDA import flashcardDA
from .reviewFlashcardDA import reviewFlashcardDA
from cmn.logger import logger

#__all__ = []
#
#models_dir = resource_path("app" , "DA" , "models")
#for file in os.listdir(models_dir):
#    if file.endswith(".py") and file != "__init__.py":
#        module_name = f"{__name__}.{file[:-3]}"
#        module = importlib.import_module(module_name)
#
#        for attr_name in dir(module):
#            attr = getattr(module, attr_name)
#            try:
#                if isinstance(attr, type) and issubclass(attr, Base) and attr is not Base:
#                    globals()[attr_name] = attr
#                    __all__.append(attr_name)
#            except TypeError:
#                pass

__all__ = ["constantDA" , "fileFlashcardDA" , "flashcardDA" , "reviewFlashcardDA"]

logger.info("Models loaded dynamically: " + str(  __all__))
