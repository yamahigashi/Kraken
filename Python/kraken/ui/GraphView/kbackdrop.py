
#
# Copyright 2010-2015
#

import math
import json

from PySide import QtGui, QtCore

from kraken.ui.backdrop_inspector import BackdropInspector

class KBackdropTitle(QtGui.QGraphicsWidget):

    __color = QtGui.QColor(255, 255, 255)
    __font = QtGui.QFont('Decorative', 14)
    __font.setLetterSpacing(QtGui.QFont.PercentageSpacing, 115)
    __labelBottomSpacing = 12

    def __init__(self, text, parent=None):
        super(KBackdropTitle, self).__init__(parent)

        # self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

        self.__textItem = QtGui.QGraphicsTextItem(text, self)
        self.__textItem.setDefaultTextColor(self.__color)
        self.__textItem.setFont(self.__font)
        self.__textItem.setPos(0, -2)
        option = self.__textItem.document().defaultTextOption()
        option.setWrapMode(QtGui.QTextOption.NoWrap)
        self.__textItem.document().setDefaultTextOption(option)
        self.__textItem.adjustSize()

        self.setPreferredSize(self.textSize())

    def setText(self, text):
        self.__textItem.setPlainText(text)
        self.__textItem.adjustSize()
        self.setPreferredSize(self.textSize())

    def textSize(self):
        return QtCore.QSizeF(
            self.__textItem.textWidth(),
            self.__font.pointSizeF() + self.__labelBottomSpacing
            )

    def setTextColor(self, color):
        self.__color = color
        self.update()


class KBackdropHeader(QtGui.QGraphicsWidget):

    def __init__(self, text, parent=None):
        super(KBackdropHeader, self).__init__(parent)

        # self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

        layout = QtGui.QGraphicsLinearLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        layout.setOrientation(QtCore.Qt.Horizontal)
        self.setLayout(layout)

        self._titleWidget = KBackdropTitle(text, self)
        layout.addItem(self._titleWidget)
        layout.setAlignment(self._titleWidget, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)


    def setText(self, text):
        self._titleWidget.setText(text)


class KBackdrop(QtGui.QGraphicsWidget):

    nameChanged = QtCore.Signal(str, str)

    __defaultColor = QtGui.QColor(65, 120, 122, 255)
    __unselectedPen =  QtGui.QPen(__defaultColor.darker(125), 1.6)
    __selectedPen =  QtGui.QPen(__defaultColor.lighter(175), 1.6)
    __linePen =  QtGui.QPen(QtGui.QColor(25, 25, 25, 255), 1.25)

    __resizeDistance = 16.0
    __setCustomCursor = False

    def __init__(self, graph, name):
        super(KBackdrop, self).__init__()
        self.setAcceptHoverEvents(True)

        self.__name = name
        self.__graph = graph
        self.__color = self.__defaultColor
        self.__color.setAlpha(25)
        self.__inspectorWidget = None

        self.setMinimumWidth(120)
        self.setMinimumHeight(80)
        # self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        layout = QtGui.QGraphicsLinearLayout()
        layout.setContentsMargins(5, 0, 5, 7)
        layout.setSpacing(7)
        layout.setOrientation(QtCore.Qt.Vertical)
        self.setLayout(layout)

        self.__headerItem = KBackdropHeader(self.__name, self)
        layout.addItem(self.__headerItem)
        layout.setAlignment(self.__headerItem, QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        layout.addStretch(1)

        self.setZValue(-10)

        self.__selected = False
        self.__dragging = False
        self.__resizing = False
        self.__resizeCorner = -1


    def getName(self):
        return self.__name


    def setName(self, name):
        if name != self.__name:
            origName = self.__name
            self.__name = name
            self.__headerItem.setText(self.__name)

            # Emit an event, so that the graph can update itsself.
            self.nameChanged.emit(origName, name)

            # Update the node so that the size is computed.
            self.adjustSize()


    def getColor(self):
        return self.__color


    def setColor(self, color):
        self.__color = color
        self.__color.setAlpha(25)
        self.update()


    def getGraph(self):
        return self.__graph


    def getHeader(self):
        return self.__headerItem


    #########################
    ## Selection

    def isSelected(self):
        return self.__selected

    def setSelected(self, selected=True):
        self.__selected = selected
        self.update()


    #########################
    ## Graph Pos

    def getGraphPos(self):
        transform = self.transform()
        size = self.size()
        return QtCore.QPointF(transform.dx()+(size.width()*0.5), transform.dy()+(size.height()*0.5))


    def setGraphPos(self, graphPos):
        self.prepareConnectionGeometryChange()
        size = self.size()
        self.setTransform(QtGui.QTransform.fromTranslate(graphPos.x()-(size.width()*0.5), graphPos.y()-(size.height()*0.5)), False)


    def translate(self, x, y):
        self.prepareConnectionGeometryChange()
        super(KBackdrop, self).translate(x, y)


    # Prior to moving the node, we need to tell the connections to prepare for a geometry change.
    # This method must be called preior to moving a node.
    def prepareConnectionGeometryChange(self):
        pass

    def paint(self, painter, option, widget):
        rect = self.windowFrameRect()
        painter.setBrush(self.__color)

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))

        roundingY = 20.0 / (rect.height() / 80.0)
        roundingX = rect.height() / rect.width() * roundingY

        painter.drawRoundRect(rect, roundingX, roundingY, mode=QtCore.Qt.AbsoluteSize)

        # Title BG
        titleHeight = self.__headerItem.size().height() - 3

        darkerColor = self.__color.darker(125)
        darkerColor.setAlpha(255)
        painter.setBrush(darkerColor)
        roundingYHeader = rect.width() * roundingX / titleHeight
        painter.drawRoundRect(0, 0, rect.width(), titleHeight, roundingX, roundingYHeader)
        painter.drawRect(0, titleHeight * 0.5 + 2, rect.width(), titleHeight * 0.5)

        painter.setBrush(QtGui.QColor(0, 0, 0, 0))
        if self.__selected:
            painter.setPen(self.__selectedPen)
        else:
            painter.setPen(self.__unselectedPen)

        painter.drawRoundRect(rect, roundingX, roundingY, mode=QtCore.Qt.AbsoluteSize)

        super(KBackdrop, self).paint(painter, option, widget)

    #########################
    ## Events

    def mousePressEvent(self, event):
        if event.button() is QtCore.Qt.MouseButton.LeftButton:

            resizeCorner = self.getCorner(event.pos())
            if resizeCorner != -1:
                self.__resizing = True
                self.__resizeCorner = resizeCorner
                self._resizedBackdrop = False
            else:
                modifiers = event.modifiers()
                if modifiers == QtCore.Qt.ControlModifier:
                    if not self.isSelected():
                        self.__graph.selectNode(self, clearSelection=False)
                    else:
                        self.__graph.deselectNode(self)

                elif modifiers == QtCore.Qt.ShiftModifier:
                    if not self.isSelected():
                        self.__graph.selectNode(self, clearSelection=False)
                else:
                    if not self.isSelected():
                        self.__graph.selectNode(self, clearSelection=True)

                    if self.isOnHeader(event.pos()):
                        self.__dragging = True
                        self._nodesMoved = False

            self._mouseDownPoint = self.mapToScene(event.pos())
            self._mouseDelta = self._mouseDownPoint - self.getGraphPos()
            self._lastDragPoint = self._mouseDownPoint
            self._lastResizePoint = self._mouseDownPoint

            self._initPos = self.boundingRect().topLeft()
            self._initWidth = self.boundingRect().width()
            self._initHeight = self.boundingRect().height()

        else:
            super(KBackdrop, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.__dragging:
            newPos = self.mapToScene(event.pos())

            graph = self.getGraph()
            if graph.getSnapToGrid() is True:
                gridSize = graph.getGridSize()

                newNodePos = newPos - self._mouseDelta

                snapPosX = math.floor(newNodePos.x() / gridSize) * gridSize;
                snapPosY = math.floor(newNodePos.y() / gridSize) * gridSize;
                snapPos = QtCore.QPointF(snapPosX, snapPosY)

                newPosOffset = snapPos - newNodePos

                newPos = newPos + newPosOffset

            delta = newPos - self._lastDragPoint
            self.__graph.moveSelectedNodes(delta)
            self._lastDragPoint = newPos
            self._nodesMoved = True

        elif self.__resizing:

            newPos = self.mapToScene(event.pos())
            delta = newPos - self._mouseDownPoint
            self._lastResizePoint = newPos
            self._resizedBackdrop = True

            self.prepareGeometryChange()

            if self.__resizeCorner == 0:

                print "resizing from top left"
                print "Delta X: " + str(delta.x() * -1.0)
                print "Delta Y: " + str(delta.y() * -1.0)

                newWidth = self._initWidth + (delta.x() * -1.0)
                newHeight = self._initHeight + (delta.y() * -1.0)

                if newWidth <= self.minimumWidth():
                    newWidth = self.minimumWidth()

                if newHeight <= self.minimumHeight():
                    newHeight = self.minimumHeight()

                self.setGeometry(self._initPos.x() - (delta.x() * -1.0), self._initPos.y() - (delta.y() * -1.0), newWidth, newHeight)


            elif self.__resizeCorner == 1:
                print "resizing from top right"

            elif self.__resizeCorner == 2:
                print "resizing from bottom left"

            elif self.__resizeCorner == 3:
                self.resize(self._initWidth + delta.x(), self._initHeight + delta.y())

            self.update()

        else:
            super(KBackdrop, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__dragging:
            if self._nodesMoved:

                newPos = self.mapToScene(event.pos())

                delta = newPos - self._mouseDownPoint
                self.__graph.endMoveSelectedNodes(delta)

            self.setCursor(QtCore.Qt.ArrowCursor)
            self.__dragging = False

        elif self.__resizing:

            self.setCursor(QtCore.Qt.ArrowCursor)
            self.__resizing = False
            self.__resizeCorner = -1

        else:
            super(KBackdrop, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.__inspectorWidget is None:
            parentWidget = self.getGraph().getGraphViewWidget()
            self.__inspectorWidget = BackdropInspector(parent=parentWidget, nodeItem=self)
            self.__inspectorWidget.show()
        else:
            self.__inspectorWidget.setFocus()

        super(KNode, self).mouseDoubleClickEvent(event)


    def hoverMoveEvent(self, event):

        resizeCorner = self.getCorner(event.pos())
        if resizeCorner == 0:
            self.__setCustomCursor = True
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif resizeCorner == 1:
            self.__setCustomCursor = True
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif resizeCorner == 2:
            self.__setCustomCursor = True
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif resizeCorner == 3:
            self.__setCustomCursor = True
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        else:
            if self.__setCustomCursor is True:
                self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtCore.Qt.ArrowCursor)

    ################
    ## Misc Methods

    def isOnHeader(self, pos):
        titleHeight = self.__headerItem.size().height() - 3

        topLeft = self.mapFromItem(self, self.boundingRect().topLeft())
        bottomRight = self.mapFromItem(self, self.boundingRect().bottomRight())
        rect = QtCore.QRectF(topLeft, bottomRight);

        return (pos.y() - rect.top()) < titleHeight

    def getCorner(self, pos):
        topLeft = self.mapFromItem(self, self.boundingRect().topLeft())
        bottomRight = self.mapFromItem(self, self.boundingRect().bottomRight())
        rect = QtCore.QRectF(topLeft, bottomRight);

        if (rect.topLeft() - pos).manhattanLength() < self.__resizeDistance:
            return 0
        elif (rect.topRight() - pos).manhattanLength() < self.__resizeDistance:
            return 1
        elif (rect.bottomLeft() - pos).manhattanLength() < self.__resizeDistance:
            return 2
        elif (rect.bottomRight() - pos).manhattanLength() < self.__resizeDistance:
            return 3

        return -1


    def inspectorClosed(self):
        self.__inspectorWidget = None


    #########################
    ## shut down

    def disconnectAllPorts(self):
        pass