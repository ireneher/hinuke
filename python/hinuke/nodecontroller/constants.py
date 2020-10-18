import os

TYPE_MODE = "Type"
NAME_MODE = "Name"
SELECTION_MODE = "Selection"
MODES = (TYPE_MODE, NAME_MODE, SELECTION_MODE)
DEFAULT_TYPE = "Write"
INDIVIDUAL_ACTIONS = ("pin", "frame")  # + rename
SELECTED_ACTIONS = ("renameSelected", "pinSelected")
ICONS = "resources/icons"
PIN_ICON = os.path.join(ICONS, "pin.svg")
UNPIN_ICON = os.path.join(ICONS, "unpin.svg")
FRAME_ICON = os.path.join(ICONS, "crop.svg")