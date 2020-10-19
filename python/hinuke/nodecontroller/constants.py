import os

TYPE_MODE = "Type"
NAME_MODE = "Name"
SELECTION_MODE = "Selection"
MODES = (TYPE_MODE, NAME_MODE, SELECTION_MODE)
DEFAULT_TYPE = "Write"
ICONS = "resources/icons"
PIN_ICON = os.path.join(ICONS, "pin.svg")
UNPIN_ICON = os.path.join(ICONS, "unpin.svg")
FRAME_ICON = os.path.join(ICONS, "crop.svg")
ENABLED_COLOUR = (60, 179, 113)
DISABLED_COLOUR = (205, 92, 92)
RENAME_MODE = "Rename"
REPLACE_MODE = "Replace"
RENAMING_MODES = (RENAME_MODE, REPLACE_MODE)
