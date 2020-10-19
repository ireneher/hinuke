import nuke
from PySide2 import QtWidgets, QtCore, QtGui

import constants
import ui
from hinuke import utils


class NodeController(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(NodeController, self).__init__(parent=parent)

        self.signals = ui.Signals()
        self.pinned = []
        self.signals.pinToggled.connect(self._onItemPinToggled)

        hLayout = QtWidgets.QHBoxLayout()
        self.mode = QtWidgets.QComboBox(self)
        self.mode.addItems(constants.MODES)
        hLayout.addWidget(self.mode)

        self.input = QtWidgets.QLineEdit()
        self.input.setText(constants.DEFAULT_TYPE)
        self.input.returnPressed.connect(self._processInput)
        hLayout.addWidget(self.input)

        self.checkboxEnable = QtWidgets.QCheckBox("Enabled nodes only")
        hLayout.addWidget(self.checkboxEnable)

        self.button = QtWidgets.QPushButton("Get nodes")
        self.button.clicked.connect(self._processInput)
        hLayout.addWidget(self.button)

        self.nodeList = ui.NodeList(signals=self.signals)
        self.signals.nameChanged.connect(self._processInput)
        self.signals.statusChanged.connect(self._processInput)

        vLayout = QtWidgets.QVBoxLayout(self)
        vLayout.addLayout(hLayout)
        vLayout.addWidget(self.nodeList)

        self._populateUI(utils.getNodesByTypeRecursively(constants.DEFAULT_TYPE))

    def _populateUI(self, collectedNodes):
        self.nodeList.clear()
        for pinnedNode in self.pinned:
            self.nodeList.addNode(pinnedNode, isPinned=True)

        for node in collectedNodes:
            if node not in self.pinned:
                self.nodeList.addNode(node)

    def _processInput(self, *args):
        mode = str(self.mode.currentText())
        userInput = str(self.input.text())
        collectedNodes = []
        if mode == constants.TYPE_MODE:
            collectedNodes = utils.getNodesByTypeRecursively(userInput)
        elif mode == constants.NAME_MODE:
            collectedNodes = utils.getPartiallyMatchingNodes(userInput)
        elif mode == constants.SELECTION_MODE:
            collectedNodes = nuke.selectedNodes()

        if self.checkboxEnable.isChecked():
            collectedNodes = [
                node for node in collectedNodes if node.knob("disable") and not node.knob("disable").value()
                                                   or not node.knob("disable")  # To account for nodes that do not have
                                                                                # a disable knob like the Viewer
            ]

        self._populateUI(collectedNodes)

    def _onItemPinToggled(self, node, isPinned):
        if isPinned:
            self.pinned.append(node)
        elif node in self.pinned:
            self.pinned.remove(node)


def launch():
    dialog = NodeController()
    dialog.exec_()