import logging
from app.core.config import settings

def configure_logging():
    logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

configure_logging()
