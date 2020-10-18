import nuke
import nukescripts


class Sharer(nukescripts.PythonPanel):
    def __init__(self, name, node):
        super(Sharer, self).__init__(name)
        self.node = node
        self.type = node.Class()

        knobNamesFromNode = self.node.writeKnobs(nuke.WRITE_USER_KNOB_DEFS).split(" ")

        # Divider I
        self.firstDivider = nuke.Text_Knob("divider1", "Nodes", "")
        self.allKnobs = [self.firstDivider]
        # Nodes of same type
        self.nodeKnobs = []
        for n in nuke.allNodes(recurseGroups=True):
            if n.Class() == self.type and n.name() != self.node.name():
                nodeNameKnob = nuke.Boolean_Knob(n.name(), n.name(), 1.0)
                nodeNameKnob.setFlag(0x1000)  # New line
                self.nodeKnobs.append(nodeNameKnob)
                self.allKnobs.append(nodeNameKnob)

        # Divider II
        self.secondDivider = nuke.Text_Knob("divider2", "", "")
        # Knobs dropdown
        self.knobs = nuke.Enumeration_Knob("knobs", "Knob", knobNamesFromNode)
        # Value of selected knob
        self.value = self.__cloneKnob(knobNamesFromNode[0])
        self.value.setFlag(0x1000)  # New line
        self.value.setFlag(0x00000080)  # Disabled

        # Divider III
        self.thirdDivider = nuke.Text_Knob("divider3", "", "")
        # Share button
        self.button = nuke.Script_Knob("Share")
        self.button.setFlag(0x1000)  # New line

        self.allKnobs.extend([self.secondDivider,
                              self.knobs,
                              self.value,
                              self.thirdDivider,
                              self.button])

        self.__buildUI()

    def __buildUI(self):
        for knob in self.allKnobs:
            self.addKnob(knob)

    def __cloneKnob(self, knobName):
        ogKnob = self.node.knob(knobName)
        createKnob = getattr(nuke, ogKnob.Class())
        newKnob = createKnob(knobName)
        newKnob.fromScript(ogKnob.toScript())

        return newKnob

    def knobChanged(self, knob):
        if knob == self.knobs:
            self.value = self.__cloneKnob(self.knobs.value())
            self.value.setFlag(0x1000)  # New line
            self.value.setFlag(0x00000080)  # Disabled
            for uiKnob in self.allKnobs:
                self.removeKnob(uiKnob)

            self.allKnobs[-3] = self.value

            self.__buildUI()

        elif knob == self.button:
            self.share()

    def share(self):
        nodeNames = [n.name() for n in self.nodeKnobs if n.getValue() == 1.0]
        for node in nuke.allNodes(recurseGroups=True):
            if node.Class() == self.type and node.name() in nodeNames:
                node[self.value.name()].fromScript(self.value.toScript())
        nuke.message("Done")


def launch(node):
    panel = Sharer("Propagate knob value to other nodes", node)
    panel.showModal()