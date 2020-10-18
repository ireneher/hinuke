import nuke
from PySide2 import QtWidgets, QtCore, QtGui

import constants
from hinuke import utils


class Signals(QtCore.QObject):
    pinToggled = QtCore.Signal(object, object)

    def __init__(self, parent=None):
        super(Signals, self).__init__(parent)


class NodeList(QtWidgets.QListWidget):
    def __init__(self, signals=None):
        super(NodeList, self).__init__()
        self.signals = signals
        self.itemDoubleClicked.connect(self._onItemDoubleClicked)
        self.itemSelectionChanged.connect(self._onSelectionChanged)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.numKeyMapping = self._mapNumKeyPress()

    def addNode(self, node, isPinned=False):
        nodeWidget = NodeWidget(node, isPinned=isPinned, signals=self.signals)
        nodeItem = QtWidgets.QListWidgetItem()
        nodeItem.setTextAlignment(QtCore.Qt.AlignHCenter)
        nodeItem.setSizeHint(nodeWidget.sizeHint())
        self.addItem(nodeItem)
        self.setItemWidget(nodeItem, nodeWidget)

    def _getNodeFromItem(self, item):
        return self.itemWidget(item).node

    def toggleNodeState(self, node):
        node['disable'].setValue(not node['disable'].value())

    def _onItemDoubleClicked(self, item):
        node = self._getNodeFromItem(item)
        node.showControlPanel()

    def _onSelectionChanged(self):
        for idx in range(self.count() - 1):
            item = self.item(idx)
            node = self._getNodeFromItem(item)
            node.setSelected(item.isSelected())

    def keyPressEvent(self, event):
        if event.key() in self.numKeyMapping.keys():
            if self.currentItem():
                node = self._getNodeFromItem(self.currentItem())
                nuke.connectViewer(self.numKeyMapping[event.key()], node)
        else:
            super(NodeList, self).keyPressEvent(event)

    def _mapNumKeyPress(self):
        mapping = {}
        for number in range(0, 9):
            mapping[getattr(QtCore.Qt, "Key_{}".format(number+1))] = number

        return mapping


class NodeWidget(QtWidgets.QWidget):
    def __init__(self, node, isPinned=False, signals=None):
        super(NodeWidget, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.isPinned = isPinned
        self.signals = signals
        self.node = node
        self.label = QtWidgets.QLabel(node.name())
        self.label.setMinimumWidth(435)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        # Icons
        self.pinIcon = QtGui.QIcon(constants.PIN_ICON)
        self.unpinIcon = QtGui.QIcon(constants.UNPIN_ICON)
        self.frameIcon = QtGui.QIcon(constants.FRAME_ICON)
        # Buttons
        self.pinButton = QtWidgets.QPushButton()
        self.pinButton.setToolTip("Pin node")
        self.pinButton.setIcon(self._getPinIcon())
        self.frameButton = QtWidgets.QPushButton()
        self.frameButton.setToolTip("Frame node in nodegraph")
        self.frameButton.setIcon(self.frameIcon)
        # Make layout
        layout.addWidget(self.pinButton)
        layout.addWidget(self.label)
        layout.addWidget(self.frameButton)
        layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        # Signals
        self.pinButton.clicked.connect(self._onPin)
        self.frameButton.clicked.connect(self._onFrame)

    def _getPinIcon(self):
        return self.pinIcon if self.isPinned else self.unpinIcon

    def _onPin(self):
        self.isPinned = not self.isPinned
        self.pinButton.setIcon(self._getPinIcon())
        if self.signals:
            self.signals.pinToggled.emit(self.node, self.isPinned)

    def _onFrame(self):
        nuke.zoom(2, [self.node.xpos(), self.node.ypos()])


class NodeController(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(NodeController, self).__init__(parent=parent)

        self.signals = Signals()
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

        self.nodeList = NodeList(signals=self.signals)

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

    def _processInput(self):
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