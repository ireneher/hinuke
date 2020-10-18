import nuke

from HINuke.KnobShare import main as KnobShare

propertiesMenu = nuke.menu("Properties")
propertiesMenu.addCommand("Share knob [HI]", lambda: KnobShare.launch(nuke.toNode(nuke.openPanels()[-1])))