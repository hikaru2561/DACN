"""
Application Configuration
"""
from .colors import COLORS
from .constants import *

# UI Configuration
UI_CONFIG = {
    "colors": COLORS,
    "fonts": {
        "default": ("Segoe UI", 10),
        "bold": ("Segoe UI", 10, "bold"),
        "header": ("Segoe UI", 14, "bold"),
        "title": ("Segoe UI", 18, "bold"),
    },
    "window_sizes": WINDOW_SIZES,
}
