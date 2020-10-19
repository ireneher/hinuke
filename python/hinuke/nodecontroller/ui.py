import re

import nuke
from PySide2 import QtWidgets, QtCore, QtGui

import constants


class Signals(QtCore.QObject):
    pinToggled = QtCore.Signal(object, object)
    nameChanged = QtCore.Signal()
    statusChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(Signals, self).__init__(parent)


class RenamingDialog(QtWidgets.QDialog):
    def __init__(self, nodes, signals=None, parent=None):
        super(RenamingDialog, self).__init__(parent=parent)
        self.nodes = nodes
        self.signals = signals
        self.setMinimumSize(300, 150)
        layout = QtWidgets.QVBoxLayout(self)
        self.mode = QtWidgets.QComboBox()
        self.mode.addItems(constants.RENAMING_MODES)
        self.mode.currentIndexChanged.connect(self._onCurrentIndexChanged)
        layout.addWidget(self.mode)

        dynamicLayout = QtWidgets.QGridLayout()
        self.nameEdit = QtWidgets.QLineEdit()
        dynamicLayout.addWidget(self.nameEdit)
        self.findLabel = QtWidgets.QLabel("Find")
        self.findEdit = QtWidgets.QLineEdit()
        self.replaceLabel = QtWidgets.QLabel("Replace")
        self.replaceEdit = QtWidgets.QLineEdit()
        dynamicLayout.addWidget(self.findLabel, 1, 1)
        dynamicLayout.addWidget(self.findEdit, 1, 2)
        dynamicLayout.addWidget(self.replaceLabel, 2, 1)
        dynamicLayout.addWidget(self.replaceEdit, 2, 2)
        self.hideReplace()
        self.showRename()
        layout.addLayout(dynamicLayout)

        self.button = QtWidgets.QPushButton("OK")
        self.button.clicked.connect(self._onButtonClicked)
        layout.addWidget(self.button)

    def hideReplace(self):
        self.findLabel.hide()
        self.findEdit.hide()
        self.replaceLabel.hide()
        self.replaceEdit.hide()

    def showReplace(self):
        self.findLabel.show()
        self.findEdit.show()
        self.replaceLabel.show()
        self.replaceEdit.show()

    def hideRename(self):
        self.nameEdit.hide()

    def showRename(self):
        self.nameEdit.show()

    def _onCurrentIndexChanged(self, currentIndex):
        if currentIndex == 0:
            self.hideReplace()
            self.showRename()

        elif currentIndex == 1:
            self.hideRename()
            self.showReplace()

    def _onButtonClicked(self):
        self.rename()
        if self.signals:
            self.signals.nameChanged.emit()
        self.accept()

    def rename(self):
        mode = str(self.mode.currentText())
        if mode == constants.RENAME_MODE:
            self.renameNodes(str(self.nameEdit.text()))
        elif mode == constants.REPLACE_MODE:
            self.replaceNameNodes(str(self.findEdit.text()),
                                  str(self.replaceEdit.text()))

    def renameNodes(self, name):
        if not name:
            return
        for node in self.nodes:
            node.setName(name)

    def replaceNameNodes(self, findStr, replaceStr):
        if not findStr or not replaceStr:
            return
        for node in self.nodes:
            name = node.name()
            compiledName = re.compile(re.escape(findStr), re.IGNORECASE)
            newName = compiledName.sub(replaceStr, name)
            node.setName(newName)


class NodeList(QtWidgets.QListWidget):
    def __init__(self, signals=None):
        super(NodeList, self).__init__()
        self.signals = signals
        self.itemDoubleClicked.connect(self._onItemDoubleClicked)
        self.itemSelectionChanged.connect(self._onSelectionChanged)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.numKeyMapping = self._mapNumKeyPress()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onRightClick)

    def addNode(self, node, isPinned=False):
        nodeWidget = NodeWidget(node,
                                isPinned=isPinned,
                                isEnabled=not node.knob("disable").value()
                                if node.knob("disable") else True,
                                signals=self.signals)
        nodeItem = QtWidgets.QListWidgetItem()
        nodeItem.setTextAlignment(QtCore.Qt.AlignHCenter)
        nodeItem.setSizeHint(nodeWidget.sizeHint())
        self.addItem(nodeItem)
        self.setItemWidget(nodeItem, nodeWidget)

    def _getNodeFromItem(self, item):
        if self.itemWidget(item):
            return self.itemWidget(item).node

    def _onItemDoubleClicked(self, item):
        node = self._getNodeFromItem(item)
        node.showControlPanel()

    def _onSelectionChanged(self):
        for idx in range(self.count() - 1):
            item = self.item(idx)
            node = self._getNodeFromItem(item)
            node.setSelected(item.isSelected())

    def onRightClick(self, pos):
        """
        Custom menu with options:
            - Disable selected
            - Pin selected
            - Rename selected
        """
        menu = QtWidgets.QMenu()
        menu.move(QtGui.QCursor().pos())
        currentItem = self.itemAt(pos)
        if currentItem:
            enableMenu = QtWidgets.QMenu("Disable/Enable")
            menu.addMenu(enableMenu)
            disableAction = enableMenu.addAction("Disable selected")
            enableAction = enableMenu.addAction("Enable selected")
            pinMenu = QtWidgets.QMenu("Pin/Unpin")
            menu.addMenu(pinMenu)
            pinAction = pinMenu.addAction("Pin selected")
            unpinAction = pinMenu.addAction("Unpin selected")
            renameAction = menu.addAction("Rename selected")

            disableAction.triggered.connect(self.disableSelected)
            enableAction.triggered.connect(self.enableSelected)
            pinAction.triggered.connect(self.pinSelected)
            unpinAction.triggered.connect(self.unpinSelected)
            renameAction.triggered.connect(self.renameSelected)

            menu.exec_()

    def renameSelected(self):
        nodes = [self.itemWidget(item).node for item in self.selectedItems()]
        renameDialog = RenamingDialog(nodes, signals=self.signals, parent=self)
        renameDialog.exec_()

    def disableSelected(self):
        self._setStatusSelected(False)

    def enableSelected(self):
        self._setStatusSelected(True)

    def _setStatusSelected(self, isEnabled):
        for item in self.selectedItems():
            self.itemWidget(item).setStatus(isEnabled)
        if self.signals:
            self.signals.statusChanged.emit()

    def pinSelected(self):
        self._setPinSelected(True)

    def unpinSelected(self):
        self._setPinSelected(False)

    def _setPinSelected(self, isPinned):
        for item in self.selectedItems():
            self.itemWidget(item).setPin(isPinned)

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
    def __init__(self, node, isPinned=False, isEnabled=True, signals=None):
        super(NodeWidget, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        self.isPinned = isPinned
        self.isEnabled = isEnabled
        self.signals = signals
        self.node = node
        self.name = node.fullName()
        # Label and status icon
        hlayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(self.name)
        font = self.font()
        font.setPointSize(15)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        hlayout.addWidget(self.label, 90)
        self.status = QtWidgets.QLabel()
        self.disabledPixmap = QtGui.QPixmap(10, 10)
        self.disabledPixmap.fill(QtGui.QColor.fromRgb(*constants.DISABLED_COLOUR))
        self.enabledPixmap = QtGui.QPixmap(10, 10)
        self.enabledPixmap.fill(QtGui.QColor.fromRgb(*constants.ENABLED_COLOUR))
        self.setStatusPixmap()
        hlayout.addWidget(self.status, 10)
        layoutRestrictorWidget = QtWidgets.QWidget()
        layoutRestrictorWidget.setLayout(hlayout)
        layoutRestrictorWidget.setMinimumWidth(435)

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
        layout.addWidget(layoutRestrictorWidget)
        layout.addWidget(self.frameButton)
        layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        # Signals
        self.pinButton.clicked.connect(self._onPin)
        self.frameButton.clicked.connect(self._onFrame)

    def _getPinIcon(self):
        return self.pinIcon if self.isPinned else self.unpinIcon

    def _onPin(self):
        self.togglePin()

    def _onFrame(self):
        # If node is inside of group, frame to its root parent
        node = nuke.toNode(self.name.split(".")[0]) if "." in self.name else self.node
        nuke.zoom(2, [node.xpos(), node.ypos()])

    def togglePin(self):
        self.setPin(not self.isPinned)

    def setPin(self, isPinned):
        self.isPinned = isPinned
        self.pinButton.setIcon(self._getPinIcon())
        if self.signals:
            self.signals.pinToggled.emit(self.node, self.isPinned)

    def setStatusPixmap(self):
        pixmap = self.enabledPixmap if self.isEnabled else self.disabledPixmap
        self.status.setPixmap(pixmap)

    def setStatus(self, isEnabled):
        self.isEnabled = isEnabled
        if self.node.knob("disable"):
            self.node.knob("disable").setValue(not self.isEnabled)
        self.setStatusPixmap()

