from pathlib import Path
import sys
from version import __version__

APP_NAME = "Node Setup App"
APP_VERSION = __version__
APP_GEOMETRY = "800x600"
APP_SIZE = tuple(map(int, APP_GEOMETRY.split("x")))
APP_POSITION = "center"
APP_ICON = "path/to/icon.ico"
APP_THEME = "superhero"
APP_THEME_MODE = "dark"
RESIZABLE = (False, False)

BASE_DIR = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
ASSETS_DIR = BASE_DIR / "assets"