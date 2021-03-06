import sys
from vectorSupport import pcaVector
from matplotlib.figure import Figure
import SimpleITK as sitk
import os
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, uic, QtCore,QtGui
from PyQt5.QtWidgets import QFileDialog,QMessageBox,QSlider
import matplotlib as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from Contours import ContorProduce
UI_PATH = 'view.ui'
if not os.path.exists('data'):
    os.mkdir('data')
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
        QPushButton{
            background-color: rgba(0,0,0,0.5);
            border-color: white;
            color :white;
        }
        QPushButton:hover{
            padding-top: 10px;
            padding-bottom: 5px;
        }
        QComboBox{
            background-color: rgba(0,0,0,0.1);
            color :black;
        }
        QSlider{
            background-color: rgba(0,0,0,0.5);

        }
                
        '''

def loadNII(file_path): #return numpy array
    tmp = os.path.splitext(file_path)
    if not(tmp[1] == '.nii' or tmp[1]== '.gz'):
       return np.array([]) 
    image = sitk.ReadImage(file_path)
    ndrev = sitk.GetArrayFromImage(image)
    return ndrev

class Application(QtWidgets.QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super().__init__()
        #UIã®åæå

        self.initUI()
        self.Setting()
        self.initFigure()
        self.initContorFigure()
        
    def Setting(self):
        self.anno = False
        self.setStyleSheet(StyleSheet)
        self.Loaded = False
        self.kParameterWidget.setValidator(QtGui.QIntValidator())
        self.FileBrowser.clicked.connect(self.showDIALOG)
        self.NiiList.currentIndexChanged.connect(lambda: self.showNii(self.NiiList.currentText()))
        self.ContorList.currentIndexChanged.connect(lambda: self.showContor(self.ContorList.currentText()))
        
    def initUI(self):
        self.resize(1400,800)#ã¦ã£ã³ãã¦ãµã¤ãºã®å¤æ´
        self.FigureWidget = QtWidgets.QWidget(self)
        self.FigureWidget.setGeometry(10,50,600,600) 
        # FigureWidgetã«Layoutãè¿½å 
        self.FigureLayout = QtWidgets.QVBoxLayout(self.FigureWidget)
        self.FigureLayout.setContentsMargins(0,0,0,0)
        #Contorãè¡¨ç¤ºããwidgetãè¿½å 
        self.ContorFigureWidget = QtWidgets.QWidget(self)
        self.ContorFigureWidget.setGeometry(750,50,600,600)
       #ContorWidgetç¨ã®layoutãè¿½å  
        self.ContorFigureLayout = QtWidgets.QVBoxLayout(self.ContorFigureWidget)
        self.ContorFigureLayout.setContentsMargins(0,0,0,0)

        self.ContorList = QtWidgets.QComboBox(self)
        self.ContorList.setGeometry(750,10,50,20)

        self.FileBrowser = QtWidgets.QPushButton('select file',self)
        self.FileBrowser.move(0,10)

        self.NiiList =QtWidgets.QComboBox(self) 
        self.NiiList.setGeometry(550,10,50,20)

        self.FileNameText = QtWidgets.QLabel(self)
        self.FileNameText.setText('your selected file path')
        self.FileNameText.setGeometry(110,10,300,30)
        
        self.Output = QtWidgets.QLabel(self)
        self.Output.setText('Output')
        self.Output.setGeometry(820,10,100,30)
        
        self.VectorOutput = QtWidgets.QLabel(self)
        self.VectorOutput.setText('current pca vactor')
        self.VectorOutput.setGeometry(950,10,200,30)

        self.kParameterNotionText = QtWidgets.QLabel(self)
        self.kParameterNotionText.setText('kparameter')
        self.kParameterNotionText.setGeometry(1200,10,100,30)

        self.kParameterWidget = QtWidgets.QLineEdit(self)
        self.kParameterWidget.setGeometry(1350,10,30,30)

    def initSlider(self,vmax):
        self.sld = QtWidgets.QSlider(Qt.Vertical,self)
        self.sld.setMinimum(0)
        self.sld.setMaximum(vmax)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setGeometry(650,50,20,600)
        self.sld.setValue(0)
        self.sld.setSingleStep(1)
        self.sld.valueChanged.connect(self.valueChange)
        self.sld.show()

    def valueChange(self):
        self.showNii(str(self.sld.value()))

    def initContorFigure(self):
        self.ContorFigure = plt.figure.Figure()
        self.ContorFigureCanvas = FigureCanvas(self.ContorFigure)
        self.ContorFigureCanvas.mpl_connect('motion_notify_event',self.mouse_move)
        self.ContorFigureLayout.addWidget(self.ContorFigureCanvas)
        self.contor_axes = self.ContorFigure.add_subplot(1,1,1)
        self.contor_axes.set_aspect('equal')
        self.contor_axes.axis('off')
    
    def initFigure(self):
        self.Figure = plt.figure.Figure()
        # FigureãFigureCanvasã«è¿½å 
        self.FigureCanvas = FigureCanvas(self.Figure)
        # Layoutã«FigureCanvasãè¿½å 
        self.FigureLayout.addWidget(self.FigureCanvas)
        #figureããaxesãä½æ
        self.axes = self.Figure.add_subplot(1,1,1)
        self.axes.axis('off')
    
    def updateFigure(self):
        self.FigureCanvas.draw()

    def updateContorFigure(self):
        self.ContorFigureCanvas.draw()

    def showDIALOG(self):
        self.NiiList.clear()
        self.NiiLength = 0
        # ç¬¬äºå¼æ°ã¯ãã¤ã¢ã­ã°ã®ã¿ã¤ãã«ãç¬¬ä¸å¼æ°ã¯è¡¨ç¤ºãããã¹
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        FILEPATH = fname[0]
        self.FileNameText.setText(FILEPATH)
        NII_Data = loadNII(FILEPATH)
        if len(NII_Data) > 0:
            self.NiiLength = len(NII_Data) 
            np.save(SAVE_PATH,NII_Data)
            for index in range(self.NiiLength):
                self.NiiList.addItem(str(index))
            self.initSlider(self.NiiLength-1)
        else:
            dlg = QMessageBox(self)
            dlg.setWindowTitle('error')
            dlg.setText('input file  needs to be .nii file')
            dlg.exec()

    def showNii(self,index):#indexãstråã§ãã
        self.axes.cla()
        self.axes.axis('off')
        self.ContorList.clear()
        if index == '':
            return
        index = int(index)
        self.NII_IMAGE= np.load(SAVE_PATH)[index]
        self.ContorData = ContorProduce(self.NII_IMAGE)#ç»åé¸ææã«ãã®è¼ªé­ãã¼ã¿ãä½æ
        for i in range(len(self.ContorData.contours)):
            self.ContorList.addItem(str(i))
        tmp = self.NII_IMAGE
        self.axes.imshow(self.NII_IMAGE)
        self.updateFigure()
        
    def showContor(self,index):#indexãstråã§ãã
        self.contor_axes.cla()#åã®plotãã¼ã¿ã®åé¤
        if index == '':
            return
        index = int(index)
        self.ContorBox = self.ContorData.produce(index)
        X = self.ContorBox[:,0]
        Y = self.ContorBox[:,1]
        self.anno = self.contor_axes.scatter(X,Y,c='blue',s=10)
        self.contor_axes.axis('off')
        self.pca = pcaVector(self.ContorBox)#Contorè¡¨ç¤ºæã«pcaãè¨ç®,defaultã§ï¼ã¤ã®è¿å
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
        if event.inaxes != self.contor_axes or  self.anno == False:
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