# pip install PySide2
# pip install pyqtdarktheme
# pip install Pillow
from ssl import create_default_context
from PySide2 import QtCore
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import sys, os, qdarktheme
from functools import partial
from PIL import Image
import cv2, numpy as np

from stego import encode as s_encode, decode as s_decode

class main(QWidget):
    
    #################################
    # !! MODIFY VALUES HERE ONLY !! #
    #################################

    # File Extensions
    FE_IMG = ['.jpg','.jpeg','.bmp','.png']
    FE_DOC = ['.docx','.txt','.xls','.xlsx']
    FE_AUD = ['.mp3','.mp4','.wav']
    FE_ALL = FE_IMG+FE_DOC+FE_AUD
    # Path for non-images
    IMG_BLANK = 'file.png'
    ENC_IMG_IPT = ''
    ENC_IMG_OUT = ''
    ENC_IMG_PL = ''
    DEC_IMG_IPT = ''      
    DEC_IMG_OUT = ''
    NUM_OF_LSB = 0

    #################################
    # !! DO NOT TOUCH BELOW !! #
    #################################

    def __init__(self, parent=None):
        super(main, self).__init__(parent)
        self.setFixedSize(1020, 600)
        self.gui()

    def gui(self):
        
        self.w1 = self
        self.w1.setAutoFillBackground(True)
        self.w1.setWindowTitle("LSB Steganography")
        self.w1.resize(1020, 600)
        self.w1.setCursor(QtCore.Qt.ArrowCursor)
        self.w1.setToolTip("")
        self.group3 = QGroupBox(self.w1)
        self.group3.setAutoFillBackground(True)
        self.group3.setTitle("File Explorer")
        self.group3.move(20, 20)
        self.group3.resize(240, 560)
        self.group3.setCursor(QtCore.Qt.ArrowCursor)
        self.group3.setToolTip("")

        hlay = QHBoxLayout(self.group3)
        self.treeview = QTreeView()
        self.treeview.setDragDropMode(QAbstractItemView.InternalMove) # Drag and drop from explorer
        self.treeview.setColumnWidth(0, 250)
        self.treeview.setAlternatingRowColors(True)
        """ self.listview = QListView() """
        hlay.addWidget(self.treeview)
        """ hlay.addWidget(self.listview) """

        #path = QtCore.QDir.currentPath()
        path = QtCore.QDir.currentPath()

        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QtCore.QDir.rootPath())
        self.dirModel.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries)

        """ self.fileModel = QFileSystemModel()
        self.fileModel.setFilter(QtCore.QDir.NoDotAndDotDot |  QtCore.QDir.AllEntries) """

        self.treeview.setModel(self.dirModel)
        """ self.listview.setModel(self.fileModel) """

        self.treeview.setRootIndex(self.dirModel.index(path))
        """ self.listview.setRootIndex(self.fileModel.index(path)) """

        self.treeview.doubleClicked.connect(self.on_clicked)
        self.treeview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(self.context_menu)

        self.group4 = QGroupBox(self.w1)
        self.group4.setAutoFillBackground(True)
        self.group4.setTitle("LSB Encode/Decode")
        self.group4.move(270, 20)
        self.group4.resize(730, 560)
        self.group4.setCursor(QtCore.Qt.ArrowCursor)
        self.group4.setToolTip("")
        self.tab = QTabWidget(self.group4)
        self.tab.move(20, 30)
        self.tab.resize(690, 340)
        self.tab.setCursor(QtCore.Qt.ArrowCursor)
        self.tab.setToolTip("")
        self.ta1 = QWidget(self.tab)
        self.ta1.setAutoFillBackground(True)
        self.ta1.setWindowTitle("")
        self.ta1.move(0, 0)
        self.ta1.resize(686, 313)
        self.ta1.setCursor(QtCore.Qt.ArrowCursor)
        self.ta1.setToolTip("")

        ### /// ###
        mainLayout = QVBoxLayout()

        self.photoViewer_ENC_IPT = ImageLabel(1)
        mainLayout.addWidget(self.photoViewer_ENC_IPT)

        self.image2_copy = QLabel(self.ta1)
        self.image2_copy.move(18, 16)
        self.image2_copy.resize(75, 75)
        self.image2_copy.setToolTip("Input object")

        self.image2_copy.setLayout(mainLayout)
        ### /// ###

        self.label2 = QLabel(self.ta1)
        self.label2.setText("Choose Input File:")
        self.label2.move(108, 16)
        self.label2.resize(100, 22)
        self.label2.setCursor(QtCore.Qt.ArrowCursor)
        self.label2.setToolTip("")
        main.gui.ltext1 = QLineEdit(self.ta1)
        main.gui.ltext1.setText("")
        main.gui.ltext1.move(228, 18)
        main.gui.ltext1.resize(380, 22)
        main.gui.ltext1.setCursor(QtCore.Qt.IBeamCursor)
        main.gui.ltext1.setToolTip("")
        main.gui.ltext1.setEnabled(False)
        self.button3 = QToolButton(self.ta1)
        self.button3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button3.setText("Browse")
        self.button3.move(608, 17)
        self.button3.resize(60, 22)
        self.button3.setCursor(QtCore.Qt.ArrowCursor)
        self.button3.setToolTip("")
        self.button3.clicked.connect(partial(self.browsefiles,"b3"))

        ### /// ###
        mainLayout = QVBoxLayout()

        self.photoViewer_ENC_PL = ImageLabel(2)
        mainLayout.addWidget(self.photoViewer_ENC_PL)

        self.image_copy2 = QLabel(self.ta1)
        self.image_copy2.move(18, 120)
        self.image_copy2.resize(75, 75)
        self.image_copy2.setToolTip("Payload object")

        self.image_copy2.setLayout(mainLayout)
        ### /// ###
        
        self.label2_copy = QLabel(self.ta1)
        self.label2_copy.setText("Choose Payload:")
        self.label2_copy.move(108, 120)
        self.label2_copy.resize(100, 22)
        self.label2_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.label2_copy.setToolTip("")
        main.gui.ltext1_copy = QLineEdit(self.ta1)
        main.gui.ltext1_copy.setText("")
        main.gui.ltext1_copy.move(228, 122)
        main.gui.ltext1_copy.resize(380, 22)
        main.gui.ltext1_copy.setCursor(QtCore.Qt.IBeamCursor)
        main.gui.ltext1_copy.setToolTip("")
        main.gui.ltext1_copy.setEnabled(False)
        self.button3_copy = QToolButton(self.ta1)
        self.button3_copy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button3_copy.setText("Browse")
        self.button3_copy.move(608, 121)
        self.button3_copy.resize(60, 22)
        self.button3_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.button3_copy.setToolTip("")
        self.button3_copy.clicked.connect(partial(self.browsefiles,"b3c"))
        self.label4 = QLabel(self.ta1)
        self.label4.setText("Number of LSB (0-7):")
        self.label4.move(108, 166)
        self.label4.resize(100, 22)
        self.label4.setCursor(QtCore.Qt.ArrowCursor)
        self.label4.setToolTip("")
        self.hslider2 = QSlider(self.ta1)
        self.hslider2.setMinimum(0)
        self.hslider2.setMaximum(7)
        self.hslider2.setSingleStep(1)
        self.hslider2.setValue(main.NUM_OF_LSB)
        self.hslider2.setOrientation(QtCore.Qt.Horizontal)
        self.hslider2.move(228, 168)
        self.hslider2.resize(380, 22)
        self.hslider2.setCursor(QtCore.Qt.ArrowCursor)
        self.hslider2.setToolTip("")
        self.hslider2.valueChanged.connect(self.changedValue)
        self.ltext2 = QLineEdit(self.ta1)
        self.ltext2.setText("0")
        self.ltext2.move(628, 166)
        self.ltext2.resize(20, 22)
        self.ltext2.setCursor(QtCore.Qt.IBeamCursor)
        self.ltext2.setToolTip("")
        self.ltext2.setEnabled(False)
        self.hprogress1 = QProgressBar(self.ta1)
        self.hprogress1.setMinimum(0)
        self.hprogress1.setMaximum(100)
        self.hprogress1.setValue(0)
        self.hprogress1.setOrientation(QtCore.Qt.Horizontal)
        self.hprogress1.move(18, 226)
        self.hprogress1.resize(650, 22)
        self.hprogress1.setCursor(QtCore.Qt.ArrowCursor)
        self.hprogress1.setToolTip("")
        self.hprogress1.setEnabled(False)
        self.button4 = QToolButton(self.ta1)
        self.button4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button4.setText("Encode")
        self.button4.move(258, 256)
        self.button4.resize(160, 42)
        self.button4.setCursor(QtCore.Qt.ArrowCursor)
        self.button4.setToolTip("Starts encoding file")
        self.button4.clicked.connect(self.encode)
        self.label2_copy_copy_copy = QLabel(self.ta1)
        self.label2_copy_copy_copy.setText("Choose Output File:")
        self.label2_copy_copy_copy.move(108, 60)
        self.label2_copy_copy_copy.resize(100, 22)
        self.label2_copy_copy_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.label2_copy_copy_copy.setToolTip("")
        main.gui.ltext1_copy_copy_copy = QLineEdit(self.ta1)
        main.gui.ltext1_copy_copy_copy.setText("")
        main.gui.ltext1_copy_copy_copy.move(228, 62)
        main.gui.ltext1_copy_copy_copy.resize(380, 22)
        main.gui.ltext1_copy_copy_copy.setCursor(QtCore.Qt.IBeamCursor)
        main.gui.ltext1_copy_copy_copy.setToolTip("")
        self.button3_copy_copy_copy = QToolButton(self.ta1)
        self.button3_copy_copy_copy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button3_copy_copy_copy.setText("Browse")
        self.button3_copy_copy_copy.move(608, 62)
        self.button3_copy_copy_copy.resize(60, 22)
        self.button3_copy_copy_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.button3_copy_copy_copy.setToolTip("")
        self.button3_copy_copy_copy.clicked.connect(partial(self.browsefiles,"b3cc"))
        self.tab.addTab(self.ta1, "Encode")
        self.ta2 = QWidget(self.tab)
        self.ta2.setAutoFillBackground(True)
        self.ta2.setWindowTitle("")
        self.ta2.move(0, 0)
        self.ta2.resize(686, 313)
        self.ta2.setCursor(QtCore.Qt.ArrowCursor)
        self.ta2.setToolTip("")

        ### /// ###
        mainLayout = QVBoxLayout()

        self.photoViewer_DEC_IPT = ImageLabel(3)
        mainLayout.addWidget(self.photoViewer_DEC_IPT)

        self.image2_copy_copy = QLabel(self.ta2)
        self.image2_copy_copy.move(18, 16)
        self.image2_copy_copy.resize(75, 75)
        self.image2_copy_copy.setToolTip("Input object")

        self.image2_copy_copy.setLayout(mainLayout)
        ### /// ###

        self.label2_copy_copy = QLabel(self.ta2)
        self.label2_copy_copy.setText("Choose Input File:")
        self.label2_copy_copy.move(108, 16)
        self.label2_copy_copy.resize(100, 22)
        self.label2_copy_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.label2_copy_copy.setToolTip("")
        main.gui.ltext1_copy_copy = QLineEdit(self.ta2)
        main.gui.ltext1_copy_copy.setText("")
        main.gui.ltext1_copy_copy.move(228, 18)
        main.gui.ltext1_copy_copy.resize(380, 22)
        main.gui.ltext1_copy_copy.setCursor(QtCore.Qt.IBeamCursor)
        main.gui.ltext1_copy_copy.setToolTip("")
        main.gui.ltext1_copy_copy.setEnabled(False)
        self.button3_copy_copy = QToolButton(self.ta2)
        self.button3_copy_copy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button3_copy_copy.setText("Browse")
        self.button3_copy_copy.move(608, 17)
        self.button3_copy_copy.resize(60, 22)
        self.button3_copy_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.button3_copy_copy.setToolTip("")
        self.button3_copy_copy.clicked.connect(partial(self.browsefiles,"b3ccc"))
        self.hprogress1_copy = QProgressBar(self.ta2)
        self.hprogress1_copy.setMinimum(0)
        self.hprogress1_copy.setMaximum(100)
        self.hprogress1_copy.setValue(0)
        self.hprogress1_copy.setOrientation(QtCore.Qt.Horizontal)
        self.hprogress1_copy.move(18, 226)
        self.hprogress1_copy.resize(650, 22)
        self.hprogress1_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.hprogress1_copy.setToolTip("")
        self.hprogress1_copy.setEnabled(False)
        self.button4_copy = QToolButton(self.ta2)
        self.button4_copy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button4_copy.setText("Decode")
        self.button4_copy.move(258, 256)
        self.button4_copy.resize(160, 42)
        self.button4_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.button4_copy.setToolTip("Starts decoding file")
        self.button4_copy.clicked.connect(self.decode)
        self.label2_copy_copy_copy_copy = QLabel(self.ta2)
        self.label2_copy_copy_copy_copy.setText("Choose Output File:")
        self.label2_copy_copy_copy_copy.move(108, 60)
        self.label2_copy_copy_copy_copy.resize(100, 22)
        self.label2_copy_copy_copy_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.label2_copy_copy_copy_copy.setToolTip("")
        main.gui.ltext1_copy_copy_copy_copy = QLineEdit(self.ta2)
        main.gui.ltext1_copy_copy_copy_copy.setText("")
        main.gui.ltext1_copy_copy_copy_copy.move(228, 62)
        main.gui.ltext1_copy_copy_copy_copy.resize(380, 22)
        main.gui.ltext1_copy_copy_copy_copy.setCursor(QtCore.Qt.IBeamCursor)
        main.gui.ltext1_copy_copy_copy_copy.setToolTip("")
        self.button3_copy_copy_copy_copy = QToolButton(self.ta2)
        self.button3_copy_copy_copy_copy.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.button3_copy_copy_copy_copy.setText("Browse")
        self.button3_copy_copy_copy_copy.move(608, 62)
        self.button3_copy_copy_copy_copy.resize(60, 22)
        self.button3_copy_copy_copy_copy.setCursor(QtCore.Qt.ArrowCursor)
        self.button3_copy_copy_copy_copy.setToolTip("")
        self.button3_copy_copy_copy_copy.clicked.connect(partial(self.browsefiles,"b3cccc"))
        self.tab.addTab(self.ta2, "Decode")
        self.label1 = QLabel(self.group4)
        self.label1.setText("Logs")
        self.label1.move(20, 375)
        self.label1.resize(90, 22)
        self.label1.setCursor(QtCore.Qt.ArrowCursor)
        self.label1.setToolTip("")
        main.gui.text3_logs = "[ACW 1.0 Coursework - Steganography]"
        main.gui.text3 = QPlainTextEdit(self.group4)
        main.gui.text3.setPlainText(main.gui.text3_logs)
        main.gui.text3.appendPlainText("[File Explorer] Loading current directory...")
        main.gui.text3.move(20, 400)
        main.gui.text3.resize(690, 150)
        main.gui.text3.setCursor(QtCore.Qt.ArrowCursor)
        main.gui.text3.setToolTip("")
        main.gui.text3.setReadOnly(True)

        return self.w1

    # /// /// #
    # Encode logic
    # /// /// #
    def encode(self):
        
            if (os.path.getsize(main.ENC_IMG_PL) > os.path.getsize(main.ENC_IMG_IPT)):
                main.gui.text3.appendPlainText("[Error] Payload image size is larger than the object")
            else:
                """ self.button4.setEnabled(False) """
                secret_data = open(main.ENC_IMG_PL,"r")
                data = secret_data.read()
                # encode the data into the image
                encoded_image = s_encode(image_name=main.ENC_IMG_IPT, secret_data=data)
                secret_data.close()
                # save the output image (encoded image)
                cv2.imwrite(main.ENC_IMG_OUT, encoded_image)
    
    # /// /// #
    # Decode logic
    # /// /// #
    def decode(self):
        decoded_data = s_decode(main.DEC_IMG_IPT)
        main.gui.text3.appendPlainText("[Decode] " + decoded_data)

    # /// /// #
    # File explorer events
    # /// /// #

    # On click event
    def on_clicked(self, index):
        path = self.dirModel.fileInfo(index).absoluteFilePath()
        """ self.listview.setRootIndex(self.fileModel.setRootPath(path)) """
        main.gui.text3.appendPlainText("> "+path)
        os.startfile(path)
    # Right-click menu event
    def context_menu(self):
        menu = QMenu()
        open = menu.addAction("Open")
        open.triggered.connect(self.open_file)
        cursor = QCursor()
        menu.exec_(cursor.pos())
    
    def open_file(self):
        index = self.treeview.currentIndex()
        path = self.dirModel.filePath(index)
        os.startfile(path)


    # /// /// #
    # Slider events
    # /// /// #

    # Slider on change
    def changedValue(self):
        main.NUM_OF_LSB = self.hslider2.value()
        self.ltext2.setText(str(main.NUM_OF_LSB))
        main.gui.text3.appendPlainText("[Encode] Number of LSB: " + str(main.NUM_OF_LSB))
        if main.NUM_OF_LSB > 3:
            main.gui.text3.appendPlainText("[Encode] !Warning: Higher LSB may reduce image quality")
    
    # /// /// #
    # File Dialog events
    # /// /// #
    def browsefiles(self, name):
        def open():
            fname = QFileDialog.getOpenFileName(self, 'Select File', os.path.dirname(__file__))
            return fname[0]
        def close():
            fname = QFileDialog.getSaveFileName(self, 'Select File', os.path.dirname(__file__))
            return fname[0]
        if name == 'b3':
            main.gui.ltext1.setText(open())
            main.ENC_IMG_IPT = main.gui.ltext1.text()
            if main.ENC_IMG_IPT:
                main.gui.text3.appendPlainText("[Encode] input > " + main.ENC_IMG_IPT)
                # Get file name and extension
                file_name, file_extension = os.path.splitext(main.ENC_IMG_IPT)
                if file_extension.lower() in main.FE_ALL:
                    if file_extension.lower() in main.FE_IMG:
                        self.photoViewer_ENC_IPT.set_image(main.ENC_IMG_IPT)
                    else:
                        self.photoViewer_ENC_IPT.set_image(main.IMG_BLANK)
                else:
                    main.gui.text3.appendPlainText("[Error] Invalid file format!")

        elif name == 'b3c':
            main.gui.ltext1_copy.setText(open())
            main.ENC_IMG_PL = main.gui.ltext1_copy.text()
            if main.ENC_IMG_PL:
                main.gui.text3.appendPlainText("[Encode] payload > " + main.ENC_IMG_PL)
                file_name, file_extension = os.path.splitext(main.ENC_IMG_PL)
                if file_extension.lower() in main.FE_ALL:
                    if file_extension.lower() in main.FE_IMG:
                        self.photoViewer_ENC_PL.set_image(main.ENC_IMG_PL)
                    else:
                        self.photoViewer_ENC_PL.set_image(main.IMG_BLANK)
                else:
                    main.gui.text3.appendPlainText("[Error] Invalid file format!")

        elif name == 'b3cc':
            main.gui.ltext1_copy_copy_copy.setText(close())
            main.ENC_IMG_OUT = main.gui.ltext1_copy_copy_copy.text()
            main.gui.text3.appendPlainText("[Encode] output > " + main.ENC_IMG_OUT)
        elif name == 'b3ccc':
            main.gui.ltext1_copy_copy.setText(open())
            main.DEC_IMG_IPT = main.gui.ltext1_copy_copy.text()
            if file_extension.lower() in main.FE_ALL:
                if main.DEC_IMG_IPT:
                    main.gui.text3.appendPlainText("[Decode] input > " + main.DEC_IMG_IPT)
                    file_name, file_extension = os.path.splitext(main.DEC_IMG_IPT)
                    if file_extension.lower() in main.FE_IMG:
                        self.photoViewer_ENC_PL.set_image(main.DEC_IMG_IPT)
                    else:
                        self.photoViewer_ENC_PL.set_image(main.IMG_BLANK)
            else:
                main.gui.text3.appendPlainText("[Error] Invalid file format!")
        elif name == 'b3cccc':
            main.gui.ltext1_copy_copy_copy_copy.setText(close())
            main.DEC_IMG_OUT = main.gui.ltext1_copy_copy_copy_copy.text()
            main.gui.text3.appendPlainText("[Decode] output > " + main.DEC_IMG_OUT)

    
class ImageLabel(QLabel):
    def __init__(self, id):
        super().__init__()
        
        self.setAlignment(Qt.AlignCenter)
        self.setText('Drop file')
        self.setStyleSheet('''
            QLabel{
                border: 2px dashed #aaa
            }
        ''')
        self.cUrl = ''
        self.setAcceptDrops(True)
        self.id = id
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            # Get file name and extension
            file_name, file_extension = os.path.splitext(file_path)
            if file_extension.lower() in main.FE_ALL:
                if file_extension.lower() in main.FE_IMG:
                    self.set_image(file_path)
                else:
                    self.set_image(main.IMG_BLANK)
                # Update necessary guis based on label ids
                if self.id == 1:
                    main.ENC_IMG_IPT = file_path
                    main.gui.ltext1.setText(main.ENC_IMG_IPT)
                    main.gui.text3.appendPlainText("[Encode] input > " + main.ENC_IMG_IPT)
                elif self.id == 2:
                    main.ENC_IMG_PL = file_path
                    main.gui.ltext1_copy.setText(main.ENC_IMG_PL)
                    main.gui.text3.appendPlainText("[Encode] payload > " + main.ENC_IMG_PL)
                elif self.id == 3:
                    main.DEC_IMG_IPT = file_path
                    main.gui.ltext1_copy_copy.setText(main.DEC_IMG_IPT)
                    main.gui.text3.appendPlainText("[Decode] input > " + main.DEC_IMG_IPT)
            else:
                main.gui.text3.appendPlainText("[Error] Invalid file format!")

            event.accept()
        else:
            event.ignore()

    def getId(self):
        return self.id

    def set_image(self, file_path):
        self.setPixmap(QPixmap(file_path))
        self.cUrl = file_path

    def setPixmap(self, image): 
        super().setPixmap(image.scaled(75, 75, Qt.KeepAspectRatio, Qt.FastTransformation))
    
    def mouseDoubleClickEvent(self, event):
        if not self.cUrl:
            main.gui.text3.appendPlainText("[Error] No files in drop box currently!")
        else:
            img = Image.open(self.cUrl)
            img.show()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    #app.setStyleSheet(qdarktheme.load_stylesheet())
    a = main()
    a.show()
    sys.exit(app.exec_())