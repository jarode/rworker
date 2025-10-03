"""
Prosty system logowania
"""
import logging
import sys
from datetime import datetime


def setup_logger(name: str = "spa_automation", level: str = "INFO") -> logging.Logger:
    """
    Konfiguruje logger z prostym formatowaniem
    
    Args:
        name: Nazwa loggera
        level: Poziom logowania (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: Skonfigurowany logger
    """
    logger = logging.getLogger(name)
    
    # Usuń istniejące handlery
    logger.handlers.clear()
    
    # Ustaw poziom
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Handler do console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Format: [TIMESTAMP] LEVEL - Message
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "spa_automation") -> logging.Logger:
    """Zwraca istniejący logger lub tworzy nowy"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        return setup_logger(name)
    
    return logger

