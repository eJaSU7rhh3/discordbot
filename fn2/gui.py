from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTextEdit, QGridLayout, QLineEdit, QLabel, QComboBox, QVBoxLayout, QGroupBox, QHBoxLayout, QDialog, QDialogButtonBox, QCheckBox, QInputDialog, QSpinBox, QMessageBox, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from multiprocessing.connection import Listener
from contextlib import closing

import subprocess
import threading
import platform
import socket
import signal
import uuid
import json
import time
import sys
import os

# variables and functions

settings={"token":"", "bot_token":"", "default_preset": 0, "presets":[], "randomize":False, "auto_leave":-1}

netAuth=str(uuid.uuid4())

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

userInfo={"username":""}
uConn=None

botInfo={"name":"","appid":0}
bConn=None

address = ('localhost', find_free_port())
listener = Listener(address, authkey=str.encode(netAuth))
userPort = address[1]

userProc = None
botProc = None

def applySettings():
    f=open("settings.json", "w")
    f.write(json.dumps(settings))
    f.close()


# gui code

class loginWindow(QDialog):
    token = ""
    def setTk(self, tk):
        self.token = tk
        self.accept()

    def __init__(self, parent):
        super().__init__(parent)
        
        self.setWindowTitle("Login to Discord Account")
        layout=QVBoxLayout()
        self.setLayout(layout)

        label1 = QLabel()
        label1.setText("Token")

        tokenBox = QLineEdit()
         
        label2 = QLabel()
        label2.setTextFormat(Qt.TextFormat.RichText)
        label2.setText("To get the token for your personal account:<br><br>1. Open Discord in your web browser and login<br>2. Open any server or direct message channel<br>3. Press <b>Ctrl+Shift+I</b> to show developer tools<br>4. Navigate to the <b>Network</b> tab<br>5. Press <b>Ctrl+R</b> to reload<br>6. Switch between random chnanels to trigger network requests<br>7. Search for a request that starts with <b>messages</b><br>8. Select the <b>Headers</b> tab on the right<br>9. Scroll down to the <b>Request Headers</b> section<br>10. Copy the value of the <b>authorization</b> header<br>")
        label2.resize(250, 0)
        label2.setWordWrap(True)

        btnBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btnBox.accepted.connect(lambda: self.setTk(tokenBox.text()))
        btnBox.rejected.connect(self.reject)

        layout.addWidget(label1)
        layout.addWidget(tokenBox)
        layout.addWidget(btnBox)
        layout.addWidget(label2)
        self.setFixedSize(250, 500)

class botLoginWindow(QDialog):
    token = ""
    def setTk(self, tk):
        self.token = tk
        self.accept()

    def __init__(self, parent):
        super().__init__(parent)
        
        self.setWindowTitle("Login to Bot Account")
        layout=QVBoxLayout()
        self.setLayout(layout)

        label1 = QLabel()
        label1.setText("Token")

        tokenBox = QLineEdit()
         
        label2 = QLabel()

        btnBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btnBox.accepted.connect(lambda: self.setTk(tokenBox.text()))
        btnBox.rejected.connect(self.reject)

        layout.addWidget(label1)
        layout.addWidget(tokenBox)
        layout.addWidget(btnBox)
        self.setFixedSize(250, 100)

def auth():
    global userProc

    if (userProc != None):
        userProc.kill()

    global userInfo
    global botInfo
    global userPort
    global netAuth
    global uConn
    while True:
        tokenui = loginWindow(None)
        tokenui.exec()
        if (tokenui.result() != QDialog.DialogCode.Accepted):
            sys.exit(0)
        token = tokenui.token
        userProc = None
        if (os.name == "posix"):
            userProc = subprocess.Popen(["venv/user/bin/python3", "bin/user.py", str(userPort), netAuth])
        elif (os.name == "nt"): 
            userProc = subprocess.Popen(["venv\\user\\Scripts\\python", "bin/user.py", str(userPort), netAuth])

        time.sleep(1)
        uConn = listener.accept()
        uConn.send(token)
        result = uConn.recv()
        msgBox = QMessageBox()
        msgBox.setText(result["value"])
        msgBox.exec()
        if (result["type"] != "error"):
            settings["token"] = token
            userInfo["username"] = result["username"]

            if (botInfo["appid"] != 0):
                uConn.send({"type":"check_app", "id":botInfo["appid"]})
                hasApp = uConn.recv()
                if (not hasApp):
                    msgBox = QMessageBox()
                    msgBox.setTextFormat(Qt.TextFormat.RichText);
                    msgBox.setText("You should install the application to your Discord Account.\n<a href=\"https://discord.com/oauth2/authorize?client_id="+str(botInfo["appid"])+"\">https://discord.com/oauth2/authorize?client_id="+str(botInfo["appid"])+"</a>")
                    msgBox.exec()
            applySettings()
            break
        uConn.close()

def setupBot():
    global botInfo
    global userPort
    global netAuth
    global bConn
    global uConn
    global botProc

    if (botProc != None):
        botProc.kill()

    while True:
        tokenui = botLoginWindow(None)
        tokenui.exec()
        if (tokenui.result() != QDialog.DialogCode.Accepted):
            sys.exit(0)
        token = tokenui.token
        botProc = None
        if (os.name == "posix"):
            botProc = subprocess.Popen(["venv/bot/bin/python3", "bin/bot.py", str(userPort), netAuth])
        elif (os.name == "nt"):
            botProc = subprocess.Popen(["venv\\bot\\Scripts\\python", "bin/bot.py", str(userPort), netAuth])
        time.sleep(1)
        bConn = listener.accept()
        bConn.send(token)
        result = bConn.recv()
        msgBox = QMessageBox()
        msgBox.setText(result["value"])
        msgBox.exec()
        if (result["type"] != "error"):
            uConn.send({"type":"check_app", "id":result["appid"]})
            hasApp = uConn.recv()
            if (not hasApp):
                msgBox = QMessageBox()
                msgBox.setTextFormat(Qt.TextFormat.RichText);
                msgBox.setText("You should install the application to your Discord Account.\n<a href=\"https://discord.com/oauth2/authorize?client_id="+str(result["appid"])+"\">https://discord.com/oauth2/authorize?client_id="+str(result["appid"])+"</a>")
                msgBox.exec()
            settings["bot_token"] = token
            botInfo["displayname"] = result["displayname"]
            botInfo["appid"] = result["appid"]
            botInfo["username"] = result["username"]
            applySettings()
            break
        bConn.close()

class presetAddWindow(QDialog):
    presetName=""
    presetMsg=""
    presetFallback=""

    def setAll(self, pn, pm, pf, pi):
        self.presetName = pn
        self.presetMsg = pm
        self.presetFallback = pf
        if (not pn in presetsToList() or presetsToList().index(pn) == pi):
            self.accept()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Preset name already exists.")

    def __init__(self, parent, presetIndex):
        super().__init__(parent)

        self.setWindowTitle("Add Preset")
        layout=QVBoxLayout()
        self.setLayout(layout)

        label1 = QLabel()
        label1.setText("Preset Name")

        presetNameBox = QLineEdit()
         
        label2 = QLabel()
        label2.setText("Spam Message")

        spamMsgBox = QTextEdit()

        label3 = QLabel()
        label3.setText("Fallback Message")

        fallbackMsgBox = QTextEdit()

        if (presetIndex != -1):
            presetNameBox.setText(settings["presets"][presetIndex]["name"])
            spamMsgBox.setText(settings["presets"][presetIndex]["spam"])
            fallbackMsgBox.setText(settings["presets"][presetIndex]["fallback"])
        
        btnBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btnBox.accepted.connect(lambda: self.setAll(presetNameBox.text(), spamMsgBox.toPlainText(), fallbackMsgBox.toPlainText(), presetIndex))
        btnBox.rejected.connect(self.reject)

        layout.addWidget(label1)
        layout.addWidget(presetNameBox)
        layout.addWidget(label2)
        layout.addWidget(spamMsgBox)
        layout.addWidget(label3)
        layout.addWidget(fallbackMsgBox)
        layout.addWidget(btnBox)
        self.setFixedSize(250, 400)

sWtree=None
sWlb=None
sWalb=None
sWbtn=None
resultMsg=""

def listenSpam():
    global resultMsg
    global sWtree
    global sWlb
    global sWalb
    global sWbtn

    chanlist={}

    while True:
        msg = uConn.recv()
        if (not isinstance(msg, dict)):
            continue # invalid
        elif (msg["type"] == "error" or msg["type"] == "success"):
            resultMsg = msg["value"]
            sWlb.setText(msg["value"])
            sWbtn.setText("Continue")
            break
        elif (msg["type"] == "alert"):
            sWalb.setText(msg["value"])
        elif (msg["type"] == "chanlist"):
            chanlist = msg["value"]
            for chanid in list(chanlist.keys()):
                chanItem = QTreeWidgetItem(sWtree)
                chanItem.setText(0, "#"+chanlist[chanid]["name"]+" - "+chanid[-5:])
                chanItem.setText(1, "0")
                chanlist[chanid]["item"] = chanItem
        elif (msg["type"] == "info"):
            chanlist[msg["id"]]["count"] += 1
            chanlist[msg["id"]]["item"].setText(1, str(chanlist[msg["id"]]["count"]))

class spamWindow(QDialog):
    def __init__(self, parent):
        global sWtree
        global sWlb
        global sWalb
        global sWbtn

        super().__init__(parent)

        self.setWindowTitle("Ongoing Spam")
        layout=QVBoxLayout()
        self.setLayout(layout)

        tree = QTreeWidget()
        tree.setColumnCount(2)
        tree.setHeaderLabels(["Name", "Count"])

        lb = QLabel()
        alb= QLabel()

        btn = QPushButton()
        btn.setText("Stop Spam")
        btn.pressed.connect(lambda: self.close())

        layout.addWidget(tree)
        layout.addWidget(lb)
        layout.addWidget(alb)
        layout.addWidget(btn)

        sWtree=tree
        sWlb=lb
        sWalb=alb
        sWbtn=btn
        thread = threading.Thread(target=listenSpam)
        thread.start()


def presetsToList():
    global settings
    presetList = []

    for preset in settings["presets"]:
        presetList.append(preset["name"])
    return presetList

def addPreset(parent, comboBox, presetIndex=-1):
    global settings
    presetDialog = presetAddWindow(parent, presetIndex)
    presetDialog.exec()

    if (presetDialog.result() == QDialog.DialogCode.Accepted):
        if (presetIndex == -1):
            settings["presets"].append({"name":presetDialog.presetName, "spam":presetDialog.presetMsg, "fallback":presetDialog.presetFallback})
        else:
            settings["presets"][presetIndex] = {"name":presetDialog.presetName, "spam":presetDialog.presetMsg, "fallback":presetDialog.presetFallback}
        applySettings()
        presetItemArray = presetsToList()
        
        comboBox.clear()
        comboBox.addItems(presetItemArray)
        comboBox.setCurrentText(presetDialog.presetName)

def deletePreset(parent, comboBox):
    global settings
    presetList = presetsToList()
    selectedPreset = QInputDialog.getItem(parent, "Delete Preset", "Select preset to delete", presetList, editable=False)
    
    if (selectedPreset[1] == False):
        return

    del settings["presets"][presetList.index(selectedPreset[0])]
    applySettings()

    presetItemArray = presetsToList()
    
    currentItem = comboBox.currentText()
    comboBox.clear()
    comboBox.addItems(presetItemArray)

    if (currentItem != selectedPreset[0]):
        comboBox.setCurrentText(currentItem)

def updateRndChk(chk):
    global settings
    settings["randomize"] = chk
    applySettings()

def updateMSC(val):
    global settings
    settings["auto_leave"] = val
    applySettings()

def updatePreset(new):
    global settings
    settings["default_preset"] = new
    applySettings()

def logout(lb):
    lb.setText("...")
    settings["token"] = ""
    applySettings()
    auth()
    lb.setText("Logged in as "+userInfo["username"]+" <a href=\".\">Logout</a>")

def changeBotToken(lb):
    lb.setText("...")
    setupBot()
    lb.setText("Bot: "+botInfo["username"]+" <a href=\".\">Change Token</a>")

def startSpam(p):
    global resultMsg
    if (len(settings["presets"]) < 1):
        msgBox = QMessageBox(p)
        msgBox.setText("No presets available.")
        msgBox.exec()
        return
    spamid = QInputDialog.getText(p, "Auto Spam", "Server/Channel id:")
    
    if (spamid[1] != True):
        return

    spamid = spamid[0]    

    uConn.flush()
    uConn.send({"type":"start_spam", "spam_message":settings["presets"][settings["default_preset"]]["spam"], "fallback_message":settings["presets"][settings["default_preset"]]["fallback"], "max_spam":settings["auto_leave"], "randomize":settings["randomize"], "id":spamid, "appid":botInfo["appid"]}) 
    sW = spamWindow(p)
    sW.exec()
    uConn.send('')
    while resultMsg=="":
        pass
    msgBox = QMessageBox(p)
    msgBox.setText(resultMsg)
    msgBox.exec()
    resultMsg=""

class MainWindow(QMainWindow):
    def __init__(self):
        global settings
        super().__init__()

        self.setWindowTitle("Discord Spammer v.fn")

        mainWidget = QWidget()
        layout=QVBoxLayout(mainWidget)

        label = QLabel()
        label.setText("Presets")

        presetItemArray = presetsToList()

        presetList = QComboBox()
        presetList.addItems(presetItemArray)
        if (len(settings["presets"]) > 0):
            presetList.setCurrentText(settings["presets"][settings["default_preset"]]["name"])
        presetList.currentIndexChanged.connect(updatePreset)

        presetBtns = QWidget()
        presetBtnsLayout = QHBoxLayout(presetBtns)

        addPresetBtn = QPushButton()
        addPresetBtn.setText("Add")
        addPresetBtn.pressed.connect(lambda: addPreset(self, presetList))

        removePresetBtn = QPushButton()
        removePresetBtn.setText("Delete")
        removePresetBtn.pressed.connect(lambda: deletePreset(self, presetList))

        editPresetBtn = QPushButton()
        editPresetBtn.setText("Edit")
        editPresetBtn.pressed.connect(lambda: addPreset(self, presetList, presetList.currentIndex()))

        presetBtnsLayout.addWidget(addPresetBtn)
        presetBtnsLayout.addWidget(removePresetBtn)
        presetBtnsLayout.addWidget(editPresetBtn)

        randomizeMsgChk = QCheckBox()
        randomizeMsgChk.setText("Randomize (anti-spam protection)")
        randomizeMsgChk.stateChanged.connect(lambda: updateRndChk(randomizeMsgChk.isChecked()))
        randomizeMsgChk.setChecked(settings["randomize"])

        label1 = QLabel()
        label1.setText("Maximum Spam Count (-1 for unlimited) (leaves after maximum spam count is reached)")
        
        maxSpamCountBox = QSpinBox()
        maxSpamCountBox.setMinimum(-1)
        maxSpamCountBox.setMaximum(65534)
        maxSpamCountBox.setValue(settings["auto_leave"])
        maxSpamCountBox.valueChanged.connect(updateMSC)

        startSpamBtn = QPushButton()
        startSpamBtn.setText("Start Spam")
        startSpamBtn.pressed.connect(lambda: startSpam(self))

        label2 = QLabel()
        label2.setText("orangypea <3 gg/cnSX6CFBJr")

        label3 = QLabel()
        label3.setTextFormat(Qt.TextFormat.RichText)
        label3.setText("Logged in as "+userInfo["username"]+" <a href=\".\">Logout</a>")
        label3.linkActivated.connect(lambda: logout(label3))

        label4 = QLabel()
        label4.setTextFormat(Qt.TextFormat.RichText)
        label4.setText("Bot: "+botInfo["username"]+" <a href=\".\">Change Token</a>")
        label4.linkActivated.connect(lambda: changeBotToken(label4))

        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label)
        layout.addWidget(presetList)
        layout.addWidget(presetBtns)
        layout.addWidget(randomizeMsgChk)
        layout.addWidget(label1)
        layout.addWidget(maxSpamCountBox)
        layout.addWidget(startSpamBtn)
        layout.addWidget(label2)

        self.setCentralWidget(mainWidget)
        self.show()

app = QApplication(sys.argv)

if (os.path.isfile("settings.json")):
    f=open("settings.json", "r")
    settings = json.loads(f.read())
    f.close()

if (settings["token"] == ""):
    auth()
else:
    userProc = None
    if (os.name == "posix"):
        userProc = subprocess.Popen(["venv/user/bin/python3", "bin/user.py", str(userPort), netAuth])
    elif (os.name == "nt"):
        userProc = subprocess.Popen(["venv\\user\\Scripts\\python", "bin/user.py", str(userPort), netAuth])
    time.sleep(1)
    uConn = listener.accept()
    uConn.send(settings["token"])
    result = uConn.recv()
    if (result["type"] == "error"):
        uConn.close()
        auth()
    else:
        userInfo["username"] = result["username"]

if (settings["bot_token"] == ""):
    setupBot()
else:
    botProc = None
    if (os.name == "posix"):
        botProc = subprocess.Popen(["venv/bot/bin/python3", "bin/bot.py", str(userPort), netAuth])
    elif (os.name == "nt"):
        botProc = subprocess.Popen(["venv\\bot\\Scripts\\python", "bin/bot.py", str(userPort), netAuth])
    time.sleep(1)
    bConn = listener.accept()
    bConn.send(settings["bot_token"])
    result = bConn.recv()
    if (result["type"] == "error"):
        bConn.close()
        setupBot()
    else:
        botInfo["displayname"] = result["displayname"]
        botInfo["username"] = result["username"]
        botInfo["appid"] = result["appid"]
        applySettings()

        uConn.send({"type":"check_app", "id":botInfo["appid"]})
        hasApp = uConn.recv()
        if (not hasApp):
            msgBox = QMessageBox()
            msgBox.setTextFormat(Qt.TextFormat.RichText);
            msgBox.setText("You should install the application to your Discord Account.\n<a href=\"https://discord.com/oauth2/authorize?client_id="+str(result["appid"])+"\">https://discord.com/oauth2/authorize?client_id="+str(result["appid"])+"</a>")
            msgBox.exec()

w = MainWindow()
app.exec()

userProc.kill()
botProc.kill()
