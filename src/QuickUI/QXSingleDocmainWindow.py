#!/usr/bin/python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from QXAction import *
from QXApplication import *
from QXStaticConfig import *
from QXToolBar import *
import platform
import sys
import re
import quick_ui_res
import json



class QXSingleDocMainWindow(QMainWindow):
    
    def __init__(self,parent=None):
        QMainWindow.__init__(self,parent)
        self.initDefaultUI()
        
        

    def initDefaultUI(self,hasToolBar = True,hasMenuBar = True):
        d = QApplication.desktop()
        screenWidget = d.screen(d.primaryScreen())
        w = screenWidget.size().height()
        h = screenWidget.size().height() * 0.6
        self.resize(w,h)
        import random,os
        random.seed(os.urandom(128))
        self.move(QPoint(
            random.randint(0,int((screenWidget.size().width()  - w) / 2)) ,
            random.randint(0,int((screenWidget.size().height() - h) / 2)))
            )
        
        self.appName = QXApplication.appName()
        
        
        self.setWindowTitle("Untitled[*] - %s" % self.appName)   
        self._fileOpenSuffix = "All Files (*.*)"
        self._fileSaveAsSuffix = "All Files (*.*)"
        self.setFileReadOnly(False)
        self._fileName = None
        self.setFileCreateByMe(False)
        
        

        self.actionDocumentNew = QXAction('&New',self,triggered=self.ActionFileNew)
        self.actionDocumentOpen = QXAction('&Open',self,triggered=self.ActionFileOpen)
        self.actionDocumentSave = QXAction('&Save',self,triggered=self.ActionFileSave)
        self.actionDocumentSaveAs = QXAction('Save &As',self,triggered=self.ActionFileSaveAs)
        
        self.actionConfigure = QXAction('Preferences...',self,triggered=self.ActionPreferences)
        
        self.actionApplicationExit = QXAction('Quit',self,triggered=self.close)
        
        self.actionEditUndo = QXAction('&Undo',self,triggered=self.onEditUndo)
        self.actionEditRedo = QXAction('&Redo',self,triggered=self.onEditRedo)
        self.actionEditCut = QXAction('Cu&t',self,triggered=self.onEditCut)
        self.actionEditCopy = QXAction('&Copy',self,triggered=self.onEditCopy)
        self.actionEditPaste = QXAction('&Paste',self,triggered=self.onEditPaste)
        
        #toolbar
        
        if hasToolBar:
            self.tbrMain = self.addToolBar("Main")
            
            self.tbrMain.addAction(self.actionDocumentNew)
            self.tbrMain.addAction(self.actionDocumentOpen)
            self.tbrMain.addAction(self.actionDocumentSave)
            
            self.tbrMain.addSeparator()
            
            self.tbrMain.addAction(self.actionEditUndo)
            self.tbrMain.addAction(self.actionEditRedo)            
            self.tbrMain.addSeparator()
            
            self.tbrMain.addAction(self.actionEditCut)
            self.tbrMain.addAction(self.actionEditCopy)
            self.tbrMain.addAction(self.actionEditPaste)
            self.tbrMain.addSeparator()
            
            self.tbrMain.addAction(self.actionConfigure)
                        
        self.setUnifiedTitleAndToolBarOnMac(True)    
        
        if hasMenuBar:
            self.mnuMain = self.menuBar()
            mnuFile = self.mnuMain.addMenu('&File')
            mnuFile.addAction(self.actionDocumentNew)
            mnuFile.addAction(self.actionDocumentOpen)
            mnuFile.addAction(self.actionDocumentSave)
            mnuFile.addAction(self.actionDocumentSaveAs)
            mnuFile.addSeparator()
            
            if platform.system() == 'Linux':
                mnuFile.addSeparator()
                mnuFile.addAction(self.actionConfigure)
                 
            mnuFile.addAction(self.actionApplicationExit)
            
            mnuEdit = self.mnuMain.addMenu('&Edit')
            mnuEdit.addAction(self.actionEditUndo)
            mnuEdit.addAction(self.actionEditRedo)
            mnuEdit.addSeparator()
            mnuEdit.addAction(self.actionEditCut)
            mnuEdit.addAction(self.actionEditCopy)   
            mnuEdit.addAction(self.actionEditPaste) 
            
            if platform.system() == 'Windows':
                mnuEdit.addSeparator()
                mnuEdit.addAction(self.actionConfigure)            

        self.preferenceDialog = QXStaticConfig()
        self.preferenceDialog.setWindowTitle("%s - Preferences" % QXApplication.appName())
        
        self.addPreferencePage('General',QXApplication.findIcon('configure','default',self.preferenceDialog.cloGetActionSetIcon(0)),[{'group_title' : '' , 'items' : [
                      {'section_title' : 'Theme', 'items' : [
                        {'item_title' : 'Icon Theme',
                         'item_type' : QXStaticConfig.List ,
                         'item_default' : QXApplication.getIconThemeList() ,
                         'call_back' : QXApplication.getIconThemeCallBack() }
                    ]}
                ]}])
    
    def addPreferencePage(self,title,icon,conf):
        self.preferenceDialog.addConfigPage(
            {
                'title' : title,
                'icon'  : icon,
                'items' : conf
            }
        )   
        
    def setFileDialogSuffix(self,s):
        allFormat = []
        for i in str(s).split(';;'):
            m = re.match(r'.*\(([^\)]+)\)\s*$',i)
            if m:
                for j in re.split(r'\s+',m.group(1)):                  
                    allFormat.append(j)
        allFormatStr='All supported format (%s)' % " ".join(allFormat)
        self._fileOpenSuffix = allFormatStr + ';;' + s 
        if not re.match(r'.*;;\s*$',s):
            s = s + ';;'
        self._fileSaveAsSuffix = s + allFormatStr
    
    def setFileSaveAsSuffix(self,s):  
        self._fileSaveAsSuffix = s
        
    def setFileCreateByMe(self,t):
        self._fileCreateByMe = t
        
    def fileCreateByMe(self):
        return self._fileCreateByMe
        
    def setFileName(self,f):
        self._fileName = f;
    
    def setFileReadOnly(self,t):
        self._fileReadOnly = t
        
    def loadFinished(self,success = False):
        
        if not success:
            self.setFileName(None)
            self.setWindowTitle("Untitled[*] - %s" % self.appName)
            return
        
        if not self._fileReadOnly:
            self.setWindowTitle("%s[*] - %s" % (self._fileName,self.appName))
        else:
            self.setWindowTitle("%s (Read Only) - %s" % (self._fileName,self.appName))
            
    def fileName(self):
        return self._fileName
    
    def ActionFileNew(self):
        QXApplication.invokeSelf()

    def ActionFileOpen(self):
        fileName = QFileDialog.getOpenFileName(self,"Open",QDir.currentPath(),self._fileOpenSuffix)
        if not fileName is None and fileName != '':
            self.setFileCreateByMe(False)
            self.ActionFileLoad(fileName)
    
    def ActionFileLoad(self,f):
        self.updateStatusBarMessage("Loading %s" % f)
        self.setFileName(f)
        self.t = QTimer()
        self.t.setSingleShot(True)
        self.t.timeout.connect(self.onFileLoad)
        self.t.start(100)

    def ActionFileSave(self):
        if self._fileName is None or self._fileReadOnly:
            self.setFileCreateByMe(True)
            self.ActionFileSaveAs()
        else:
            self.onFileSave(self.fileName())
                
            
    def ActionFileSaveAs(self):
        fileName = QFileDialog.getSaveFileName(self,"Save As",QDir.currentPath(),self._fileSaveAsSuffix)
        if not fileName is None and fileName != '':
            if self.onFileSaveAs(fileName):            
                self.ActionFileLoad(fileName)

    def ActionPreferences(self):
        self.preferenceDialog.setAttribute(Qt.WA_DeleteOnClose,False)
        self.preferenceDialog.show()
        

    def onFileLoad(self):
        pass

    def onFileSaveAs(self,fileName):
        return False
    
    def onFileSave(self,fileName):
        pass

    def setEditUndoRedoStatus(self,canUndo,canRedo):
        self.actionEditUndo.setEnabled(canUndo)
        self.actionEditRedo.setEnabled(canRedo)

    def onEditUndo(self):
        pass
    
    def onEditRedo(self):
        pass
    
    def onEditCut(self):
        pass
    
    def onEditCopy(self):
        pass
    
    def onEditPaste(self):
        pass
    
    def updateStatusBarMessage(self,s):
        self.statusBar().showMessage(s)
    
    def closeEvent(self,e):
        if (self.isWindowModified()):
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowTitle(self.appName)
            msgBox.setText("The document %s has been modified." % self.fileName())
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            ret = msgBox.exec_()
            
            if ret == QMessageBox.Cancel:
                e.ignore()
                return
            
            if ret == QMessageBox.Save:
                self.ActionFileSave()
                e.accept()
                return            
        e.accept()
        return                  
            
if __name__ == '__main__':
    import sys
    app = QXApplication(sys.argv,'QuickUI')
    w = QXSingleDocMainWindow()
    w.show()
    app.exec_()