"""
Utility functions and classes for Galileo application.

This module provides common utilities including configuration management,
caching, date parsing, and file system helpers.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
import requests
from requests import Response


# Directory constants
APPDATA_DIR = "."
USERDATA_DIR = "./"

# Default configuration structure
DEFAULT_CONFIG = {
    "Resumen Diario": {
        "Weather": {"Enabled": True, "Location": "Ortuella"},
        "Jokes": {"Enabled": True, "Url": "https://naiel.fyi/chistes.txt"},
    },
    "Receta": "No Disp.",
}

# Global variables
CONFIG: Optional[Dict[str, Any]] = None
REQ_CACHE: Dict[str, Response] = {}

# Initialize directory paths based on environment
if hasattr(sys, "_MEIPASS"):
    APPDATA_DIR = os.path.join(sys._MEIPASS)
if os.environ.get("ISDOCKER"):
    USERDATA_DIR = os.environ.get("DATAPATH", "/data/")


class DateParser:
    """
    Parser for ISO datetime strings with localization support.
    
    Provides methods to format dates in Spanish locale and
    extract common date/time components.
    """

    LOCALE_DATE = {
        "DAY_OF_WEEK": (
            "Lunes", "Martes", "Miércoles", "Jueves", 
            "Viernes", "Sábado", "Domingo"
        ),
        "MONTH": (
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ),
        "FORMATS": {
            "Day": "{hdow} {day} de {hmonth} del {year}",
        },
    }

    def __init__(self, iso: Optional[str] = None, locale: Dict[str, Any] = None) -> None:
        """
        Initialize DateParser with optional ISO datetime string.

        Args:
            iso: ISO datetime string. If None, uses current datetime.
            locale: Custom locale configuration. Defaults to Spanish.
        """
        self.locale = locale or self.LOCALE_DATE
        self.dt = datetime.fromisoformat(iso) if iso else datetime.now()

    def human_day(self) -> str:
        """
        Format the date as human-readable string in current locale.

        Returns:
            Formatted date string (e.g., "Lunes 15 de Enero del 2024")
        """
        hdow = self.locale["DAY_OF_WEEK"][self.dt.weekday()]
        hmonth = self.locale["MONTH"][self.dt.month - 1]
        format_str = self.locale["FORMATS"]["Day"]
        
        return format_str.format(
            hdow=hdow,
            hmonth=hmonth,
            day=self.dt.day,
            month=self.dt.month,
            year=self.dt.year,
        )

    def pretty_time(self) -> str:
        """
        Format time as HH:MM string.

        Returns:
            Time string in HH:MM format
        """
        return f"{self.dt.hour:02d}:{self.dt.minute:02d}"

    def pretty_month_code(self) -> str:
        """
        Format month as YYYY-MM string.

        Returns:
            Month string in YYYY-MM format
        """
        return f"{self.dt.year}-{self.dt.month:02d}"

    def pretty_day_code(self) -> str:
        """
        Format date as YYYY-MM-DD string.

        Returns:
            Date string in YYYY-MM-DD format
        """
        return f"{self.dt.year}-{self.dt.month:02d}-{self.dt.day:02d}"


def cached_request(name: str, *args, **kwargs) -> Response:
    """
    Make a cached HTTP GET request.
    
    Args:
        name: Cache key for the request
        *args: Arguments passed to requests.get()
        **kwargs: Keyword arguments passed to requests.get()
        
    Returns:
        Response object from requests library
    """
    if name in REQ_CACHE:
        return REQ_CACHE[name]
    
    REQ_CACHE[name] = requests.get(*args, **kwargs)
    return REQ_CACHE[name]


def clear_cache() -> None:
    """Clear the HTTP request cache."""
    global REQ_CACHE
    REQ_CACHE.clear()


def get_config() -> Dict[str, Any]:
    """
    Load configuration from file or create default if not exists.
    
    Returns:
        Configuration dictionary
    """
    global CONFIG
    config_path = os.path.join(USERDATA_DIR, "config.json")
    
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config: {e}. Using default configuration.")
        CONFIG = DEFAULT_CONFIG.copy()
    
    return CONFIG


def set_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save configuration to file.
    
    Args:
        new_config: Configuration dictionary to save
        
    Returns:
        The saved configuration dictionary
    """
    global CONFIG
    config_path = os.path.join(USERDATA_DIR, "config.json")
    
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        CONFIG = new_config
    except IOError as e:
        print(f"Error saving config: {e}")
        raise
    
    return CONFIG


def check_path(path: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        path: Directory path to check and create
    """
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def pyson_sort(data: Dict[str, Dict], key_to_sort: str, reverse: bool = False) -> Dict[str, Dict]:
    """
    Sort dictionary by a key in nested dictionaries.
    
    Args:
        data: Dictionary with nested dictionaries to sort
        key_to_sort: Key name in nested dictionaries to sort by
        reverse: Whether to sort in descending order
        
    Returns:
        New sorted dictionary
    """
    sorted_items = sorted(
        data.items(), 
        key=lambda x: x[1].get(key_to_sort, ""), 
        reverse=reverse
    )
    return dict(sorted_items)

