#NEXT:
# criar ficheiro config automatico para o caso de nao existir
# excepçoes sons e imagens
# impedir duas instancias
# show timer, botao restart, 

# Muito mais tarde: 
# # detecta movimentos do rato
# # detecta se bloqueia o Pc
# # caso muito ativo durante muito tempo - o icone muda e os sons tocam
import sys
import os
from playsound import playsound
from time import sleep
from datetime import datetime, timedelta
from PyQt5.QtCore import QRunnable, Qt, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QLabel, QApplication, QMainWindow

from configparser import ConfigParser
cfg = ConfigParser()
cfg.read('config.ini')
print(cfg.sections())

time1_seconds = cfg.getint('pymodori','lotime') * 60
time2_seconds = cfg.getint('pymodori','hitime') * 60

sound1_file   = 'data/sound1.mp3'
sound2_file   = 'data/sound2.mp3'
hap           = 'data/hap.png'
sad           = 'data/sad.png'
mad           = 'data/mad.png'


class Timer(QRunnable):
    def __init__(self, time1_seconds,time2_seconds):
        super().__init__()
        self.time1_seconds = time1_seconds
        self.time2_seconds = time2_seconds
        print("HiTime set to: ", self.time1_seconds, " | LoTime set to: ", self.time2_seconds)
    def runIT(self):
        init_time = datetime.now()
        ct1=0
        x=True
        TrayDef.setIcon("hap")
        while x==True:
            try:
                f = open('control')
                f.close()
            except IOError:
                print("exit-timer")
                x=False
            if (init_time + timedelta(seconds=self.time1_seconds) < datetime.now()) and (ct1==0):
                TrayDef.setIcon("sad")
                playsound(sound1_file)
                ct1=1
                sleep(5)
                print("LoTime")
            elif init_time + timedelta(seconds=self.time2_seconds) < datetime.now():
                TrayDef.setIcon("mad")
                playsound(sound2_file)
                init_time = datetime.now()
                ct1=0
                sleep(5)
                x=False
                print("HiTime")
            else:   
                tdelta = init_time + timedelta(seconds=self.time2_seconds) - datetime.now()
                print("Time2Buzz: ", tdelta)
                sleep(5)

class Tray(QRunnable):
    def __init__(self):
        #START QTapp
        # Adding an icon
        self.tray = QSystemTrayIcon() 
        self.tray.setIcon(QIcon(hap)) 
        self.tray.setVisible(True) 
        # Creating the menu options
        self.menu = QMenu() 
        self.o_start = QAction("(Re)Start!")
        self.o_settings = QAction("Settings") 
        self.o_about = QAction("About") 
        self.o_quit = QAction("Quit") 
        self.menu.addAction(self.o_start)
        self.menu.addAction(self.o_settings) 
        self.menu.addAction(self.o_about) 
        self.menu.addAction(self.o_quit) 
        # Menu Options
        self.o_quit.triggered.connect(AppExit) 
        self.o_quit.triggered.connect(sys.exit) 
        self.o_about.triggered.connect(AboutWindow.show)
        #self.o_start.triggered.connect(TimerDef.runIT)
        self.o_start.triggered.connect(TWorker)        
        self.o_settings.triggered.connect(SettingsWindow.show)
        self.tray.setContextMenu(self.menu) 
    
    #Change Tray Icon
    def setIcon(self,NewIcon):
        if NewIcon=="sad":
            self.tray.setIcon(QIcon(sad))
        if NewIcon=="hap":
            self.tray.setIcon(QIcon(hap))
        if NewIcon=="mad":
            self.tray.setIcon(QIcon(mad))
            
def AppExit():
    os.remove('control')
    app.quit()
    sys.exit()
    
####################### DEF WINDOW ################################################################
class DefWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        label = QLabel("Pymodori!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

class AboWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        label = QLabel("Pomodori inspired App, but as a Python exercise.")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
                
# MultiThread --
# worker1 -> trayIcon
# worker2 -> timer()

def TWorker():
    TimerDef = Timer(time1_seconds,time2_seconds)
    pool.start(TimerDef.runIT)

app = QApplication([]) 
app.setQuitOnLastWindowClosed(False) 
SettingsWindow = DefWindow()
AboutWindow = AboWindow()
TrayDef = Tray()
pool = QThreadPool.globalInstance()

#app.exec_()

def main():
    pool.start(app.exec_())
    mainControl = 0
    pool.CancelAll()
    os.remove('control') 
    sys.exit(app.exec_())

if __name__ == "__main__":
    cf = open('control',"a+")
    cf.write("OK")
    cf.close()
    main()
