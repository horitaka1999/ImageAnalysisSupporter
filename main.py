import sys
from vectorSupport import pcaVector
from matplotlib.figure import Figure
import SimpleITK as sitk
import os
import circle
from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtWidgets import QFileDialog,QMessageBox
import matplotlib as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from Contours import ContorProduce
UI_PATH = 'view.ui'
SAVE_PATH = 'data/sliced.npy'
StyleSheet = '''
        *{
            font-weight: bold;
        }
        QMainWindow{
            background-color:rgba(148,87,168,0.5);
        }
        QLabel{
            background-color:rgba(0,0,0,0.5);
            color: white;
        }
        QLineEdit{
            border-radius:8px;
            background-color:rgba(0,0,0,0.5);
            color: white;
        }
        QLineEdit:hover{
        }
        
        '''
def loadNII(file_path): #return numpy array
    if os.path.splitext(file_path)[1] != '.nii':
       return np.array([]) 
    image = sitk.ReadImage(file_path)
    ndrev = sitk.GetArrayFromImage(image)
    return ndrev

class Application(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super().__init__()
        #UIの初期化

        self.initUI()
        self.Setting()
        self.initFigure()
        self.initContorFigure()
        
    def Setting(self):
        self.Loaded = False
        self.setStyleSheet(StyleSheet)
        self.Loaded = False
        self.kParameterWidget.setValidator(QtGui.QIntValidator())
        self.FileBrowser.clicked.connect(self.showDIALOG)
        self.NiiList.currentIndexChanged.connect(lambda: self.showNii(self.NiiList.currentText()))
        self.ContorList.currentIndexChanged.connect(lambda: self.showContor(self.ContorList.currentText()))
        
    def initUI(self):
        self.resize(1400,800)#ウィンドウサイズの変更
        self.FigureWidget = QtWidgets.QWidget(self)
        self.FigureWidget.setGeometry(10,50,600,600) 
        # FigureWidgetにLayoutを追加
        self.FigureLayout = QtWidgets.QVBoxLayout(self.FigureWidget)
        self.FigureLayout.setContentsMargins(0,0,0,0)
        #Contorを表示するwidgetを追加
        self.ContorFigureWidget = QtWidgets.QWidget(self)
        self.ContorFigureWidget.setGeometry(750,50,600,600)
       #ContorWidget用のlayoutを追加 
        self.ContorFigureLayout = QtWidgets.QVBoxLayout(self.ContorFigureWidget)
        self.ContorFigureLayout.setContentsMargins(0,0,0,0)

        self.ContorList = QtWidgets.QComboBox(self)
        self.ContorList.setGeometry(750,10,20,20)

        self.FileBrowser = QtWidgets.QPushButton('select file',self)
        self.FileBrowser.move(0,10)

        self.NiiList =QtWidgets.QComboBox(self) 
        self.NiiList.setGeometry(600,10,20,20)

        self.FileNameText = QtWidgets.QLabel(self)
        self.FileNameText.setText('your selected file path')
        self.FileNameText.setGeometry(100,10,300,30)
        
        self.Output = QtWidgets.QLabel(self)
        self.Output.setText('Output')
        self.Output.setGeometry(800,10,100,30)
        
        self.VectorOutput = QtWidgets.QLabel(self)
        self.VectorOutput.setText('current pca vactor')
        self.VectorOutput.setGeometry(950,10,200,30)

        self.kParameterNotionText = QtWidgets.QLabel(self)
        self.kParameterNotionText.setText('kparameter')
        self.kParameterNotionText.setGeometry(1200,10,100,30)

        self.kParameterWidget = QtWidgets.QLineEdit(self)
        self.kParameterWidget.setGeometry(1350,10,30,30)

    def initContorFigure(self):
        self.ContorFigure = plt.figure.Figure()
        self.ContorFigureCanvas = FigureCanvas(self.ContorFigure)
        self.ContorFigureCanvas.mpl_connect('motion_notify_event',self.mouse_move)
        self.ContorFigureLayout.addWidget(self.ContorFigureCanvas)
        self.contor_axes = self.ContorFigure.add_subplot(1,1,1)
        self.contor_axes.axis('off')
    
    def initFigure(self):
        self.Figure = plt.figure.Figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.FigureLayout.addWidget(self.FigureCanvas)
        #figureからaxesを作成
        self.axes = self.Figure.add_subplot(1,1,1)
        self.axes.axis('off')
    
    def updateFigure(self):
        self.FigureCanvas.draw()

    def updateContorFigure(self):
        self.ContorFigureCanvas.draw()

    def showDIALOG(self): 
        self.NiiList.clear()
        self.NiiLength = 0
        # 第二引数はダイアログのタイトル、第三引数は表示するパス
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        FILEPATH = fname[0]
        self.FileNameText.setText(FILEPATH)
        NII_Data = loadNII(FILEPATH)
        if len(NII_Data) > 0:
            self.NiiLength = len(NII_Data) 
            for index in range(self.NiiLength):
                self.NiiList.addItem(str(index))
            np.save(SAVE_PATH,NII_Data)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle('error')
            dlg.setText('input file  needs to be .nii file')
            dlg.exec()

    def showNii(self,index):#indexがstr型でくる
        self.ContorList.clear()
        if index == '':
            return
        index = int(index)
        self.NII_IMAGE= np.load(SAVE_PATH)[index]
        self.ContorData = ContorProduce(self.NII_IMAGE)#画像選択時にその輪郭データを作成
        for i in range(len(self.ContorData.contours)):
            self.ContorList.addItem(str(i))
        tmp = self.NII_IMAGE
        tmp *= 255
        self.axes.imshow(tmp,cmap='gray')
        self.updateFigure()
        
    def showContor(self,index):#indexがstr型でくる
        self.Loaded = True
        self.contor_axes.cla()#前のplotデータの削除
        if index == '':
            return
        index = int(index)
        self.ContorBox = self.ContorData.produce(index)
        X = self.ContorBox[:,0]
        Y = self.ContorBox[:,1]
        self.anno = self.contor_axes.scatter(X,Y,c='blue',s=10)
        self.contor_axes.axis('off')
        self.pca = pcaVector(self.ContorBox)#Contor表示時にpcaを計算,defaultで５つの近傍
        self.pca.saveData()
        self.updateContorFigure()

    def showSelectedContor(self,ContorBox,index,kParameter):
        self.contor_axes.cla()
        selected_x = []
        selected_y = []
        for i in range(index-kParameter,index+kParameter):
            if 0 <= i < len(ContorBox):
                selected_x.append(ContorBox[i][0])
                selected_y.append(ContorBox[i][1])
        X = self.ContorBox[:,0]
        Y = self.ContorBox[:,1]
        self.anno = self.contor_axes.scatter(X,Y,c = 'blue',s=10)
        self.contor_axes.scatter(selected_x,selected_y,c = 'red',s=10)
        self.contor_axes.axis('off')
        self.updateContorFigure()
        return
    
        
    def mouse_move(self,event):#ContorFigure Clicked Event
        x = event.xdata
        y = event.ydata
        if event.inaxes != self.contor_axes and not self.Loaded:
            return
        cont,rev = self.anno.contains(event)
        if not cont:
            self.Output.setText('cannot calculate!')
            return 
        if cont:
            self.kParameter = 16
            if self.kParameterWidget.text().isdecimal():
                self.kParameter = int(self.kParameterWidget.text())
            self.Currentindex = rev['ind'][0]
            self.showSelectedContor(self.ContorBox,self.Currentindex,self.kParameter)
            self.showCalc(self.Currentindex)
        if self.Currentindex >= len(self.ContorBox):
            print('error')
            return
            
    def showCalc(self,index):
        self.VectorOutput_update(index)
        maxArg = self.pca.calcMaxArg(index,self.kParameter)
        if maxArg > 0.1:
            self.Output.setStyleSheet('color: red')
        else:
            self.Output.setStyleSheet('color :white')
        self.Output.setText(str(maxArg))
        
    def VectorOutput_update(self,index):
        x = self.pca.revVector[index][0]
        y = self.pca.revVector[index][1]
        output_text = 'x:' + str(x)[:4] + 'y:' + str(y)[:4]
        self.VectorOutput.setText(output_text)
        
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = Application()
    mainwindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()