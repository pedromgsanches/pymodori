## NEXT:
# excepçoes sons e imagens
# impedir duas instancias
# show timer, botao restart, botao cancel

# Muito mais tarde: 
# # detecta movimentos do rato
# # detecta se bloqueia o Pc
# # caso muito ativo durante muito tempo - o icone muda e os sons tocam

import sys, os, random
from playsound import playsound
from time import sleep
from datetime import datetime, timedelta
from PyQt5.QtCore import QRunnable, Qt, QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QLabel, QApplication, QMainWindow

from win10toast import ToastNotifier
toaster = ToastNotifier()

from configparser import ConfigParser

cfg = ConfigParser()
try:
    cfg.read('config.ini')
    time1_seconds = cfg.getint('pymodori','lotime') * 60
    time2_seconds = cfg.getint('pymodori','hitime') * 60
except:
    #cfg('pymodori','lotime') = 20
    #cfg('pymodori','hitime') = 25
    #with open('config.ini', 'w') as configfile:
    #    cfg.write(configfile)
    time1_seconds = 20*60
    time2_seconds = 25*60

## for now it's just useless because is not testing file, is adding string to variable // define as list, for each in list -> test
try:
    sound1_file   = 'data/sound1.mp3'
    sound2_file   = 'data/sound2.mp3'
    hap           = 'data/hap.png'
    sad           = 'data/sad.png'
    mad           = 'data/mad.png'
    pym           = 'data/pym.png'
    pymtoast      = 'data/pymtoast.png'
    sadtoast      = 'data/sadtoast.txt'
    madtoast      = 'data/madtoast.txt'
except:
    print("Where are my data files?")
    sys.exit()

# Get Toast -- definir classe
with open(sadtoast) as st:
    sadlist = []
    for i in st:
        sadlist.append(i)
with open(madtoast) as st:
    madlist = []
    for i in st:
        madlist.append(i)
## convert lambda func
def get_sad_toast():
    toast_text=random.choice(sadlist)
    return(toast_text)
## convert lambda func
def get_mad_toast():
    toast_text=random.choice(madlist)
    return(toast_text)


# Classes
class Timer(QRunnable):
    def __init__(self, time1_seconds,time2_seconds):
        super().__init__()
        self.time1_seconds = time1_seconds
        self.time2_seconds = time2_seconds
        print("LoTime set to: ", self.time1_seconds/60, "min | HiTime set to: ", self.time2_seconds/60, "min")
    def runIT(self):
        init_time = datetime.now()
        ct1=0
        x=True
        TrayDef.setIcon("hap")
        tf = open('control','w')
        tf.write('00:00:00')
        tf.close()
        while x==True:
            try:
                f = open('control')
                f.close()
            except IOError:
                print("Bye!")
                x=False
                AppExit()
                
            if (init_time + timedelta(seconds=self.time1_seconds) < datetime.now()) and (ct1==0):
                TrayDef.setIcon("sad")
                playsound(sound1_file)
                toaster.show_toast("Pymodori time is running...",get_sad_toast(),icon_path=pymtoast,duration=10,threaded=True)
                ct1=1
                sleep(2)
                #print("LoTime")
            elif init_time + timedelta(seconds=self.time2_seconds) < datetime.now():
                TrayDef.setIcon("mad")
                playsound(sound2_file)
                toaster.show_toast("Pymodori time has gone...",get_mad_toast(),icon_path=pymtoast,duration=10,threaded=True)
                init_time = datetime.now()
                ct1=0
                sleep(2)
                
                x=False
                #print("HiTime")
            else:   
                tdelta = init_time + timedelta(seconds=self.time2_seconds) - datetime.now()
                tf = open('control','w')
                tf.write(str(tdelta))
                tf.close()
                sleep(2)

class Tray(QRunnable):
    def __init__(self):
        #START QTapp
        # Adding an icon
        self.tray = QSystemTrayIcon() 
        self.tray.setIcon(QIcon(pym)) 
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
        self.o_about.triggered.connect(AboutWindow.showme)
        #self.o_start.triggered.connect(TimerDef.runIT)
        self.o_start.triggered.connect(TWorker)        
        self.o_settings.triggered.connect(SettingsWindow.showme)
        self.tray.setContextMenu(self.menu) 
    
    #Change Tray Icon
    def setIcon(self,NewIcon):
        if NewIcon=="sad":
            self.tray.setIcon(QIcon(sad))
        if NewIcon=="hap":
            self.tray.setIcon(QIcon(hap))
        if NewIcon=="mad":
            self.tray.setIcon(QIcon(mad))
        if NewIcon=="pym":
            self.tray.setIcon(QIcon(pym))            
            
def AppExit():
    os.remove('control')
    app.quit()
    sys.exit()
    
####################### DEF WINDOW ################################################################
class DefWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
    def showme(self):
        label = QLabel("Pymodori!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)
        self.show()

class AboWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About Pymodori")    
        
        tf = open('control','r')
        tlab = QLabel("Pomodori inspired App, \nbut as a Python exercise.\n - \n"+tf.read())
        tf.close()

    def showme(self):
        tf = open('control','r')
        tlab = QLabel("Pomodori inspired App, \nbut as a Python exercise.\n - \n"+tf.read())
        tf.close()
        tlab.setWordWrap(True)
        tlab.setAlignment(Qt.AlignCenter) 
        self.setCentralWidget(tlab)
        self.show()
                      
# MultiThread --
# worker1 -> trayIcon
# worker2 -> timer()

def TWorker():
    TimerDef = Timer(time1_seconds,time2_seconds)
    pool.start(TimerDef.runIT)

tf = open('control','w')
tf.write('00:00:00')
tf.close()
    
app = QApplication([]) 
app.setQuitOnLastWindowClosed(False) 
SettingsWindow = DefWindow()
AboutWindow = AboWindow()
TrayDef = Tray()
pool = QThreadPool.globalInstance()

#app.exec_()

def main():
    pool.start(app.exec_())
    pool.CancelAll()
    os.remove('control') 
    sys.exit(app.exec_())

if __name__ == "__main__":
    #cf = open('control',"a+")
    #cf.write("OK")
    #cf.close()
    main()




