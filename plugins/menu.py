import nuke
from nukescripts import panels

from hinuke.knobshare import main as knobshare
from hinuke.nodecontroller import main as nodecontroller

propertiesMenu = nuke.menu("Properties")
propertiesMenu.addCommand("Share knob [HI]", lambda: knobshare.launch(nuke.toNode(nuke.openPanels()[-1])))

panels.registerWidgetAsPanel(
    'nodecontroller.NodeController',
    'Node Controller [HI]',
    'uk.co.thefoundry.NodeController'
)
