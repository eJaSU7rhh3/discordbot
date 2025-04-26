from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QTextEdit, QGridLayout, QLineEdit, QLabel, QComboBox, QVBoxLayout, QGroupBox, QHBoxLayout, QDialog, QDialogButtonBox, QCheckBox, QInputDialog, QSpinBox
import subprocess
import requests
import threading
import platform
import json
import time
import sys
import os

# variables and functions

token = ""
botToken = ""
preset_messages = {}
application_name = ""
command_name = ""
maximum_spam_count = -1
default_preset = ""
randomize_message = False

current_preset = ""

def updatejson():
    f=open("botspammer.json", "w")
    f.write(json.dumps({"token": token, "preset_messages": preset_messages, "application_name": application_name, "command_name":command_name, "maximum_spam_count": maximum_spam_count, "default_preset":default_preset, "randomize_message": randomize_message, "botToken":botToken}))
    f.close()

if (os.path.exists("botspammer.json")):
    f=open("botspammer.json", "r")
    arr = json.loads(f.read())
    f.close()

    if ("token" in arr):
        token = arr["token"]

    if ("botToken" in arr):
        botToken = arr["botToken"]
    
    if ("preset_messages" in arr):
        preset_messages = arr["preset_messages"]
    
    if ("application_name" in arr):
        application_name = arr["application_name"]

    if ("command_name" in arr):
        command_name = arr["command_name"]

    if ("maximum_spam_count" in arr):
        maximum_spam_count = arr["maximum_spam_count"]

    if ("default_preset" in arr):
        default_preset = arr["default_preset"]
        if (default_preset in preset_messages):
            current_preset = default_preset

    if ("randomize_message" in arr):
        randomize_message = arr["randomize_message"]

# gui code

def startBot():
    if (platform.system() == "Linux"):
        threading.Thread( target=subprocess.run, args=( ["venv/bot/bin/python", "bin/bot.py", botToken], )).start()
    elif (platform.system() == "Windows"):
        subprocess.run(["venv\\bot\\Scripts\\python3", "bin\\bot.py", botToken])

def startSpam(parent):
    guildId = QInputDialog.getText(parent, "Start Spam", "Enter server (or channel) ID")

    if (guildId[1] == False):
        return

    rmstr = "n"
    if (randomize_message):
        rmstr = "y"
    if (platform.system() == "Linux"):
        threading.Thread( target=subprocess.run, args=( ["venv/user/bin/python3", "bin/user.py", preset_messages[current_preset]["spam_message"], preset_messages[current_preset]["fallback_message"], token, application_name, command_name, guildId[0], rmstr, str(maximum_spam_count)], )).start()
    elif (platform.system() == "Windows"):
        threading.Thread( target=subprocess.run, args=( ["venv\\user\\Scripts\\python", "bin\\user.py", preset_messages[current_preset]["spam_message"], preset_messages[current_preset]["fallback_message"], token, application_name, command_name, guildId[0], rmstr, str(maximum_spam_count)], )).start()
    

class presetAddWindow(QDialog):
    presetName=""
    presetMsg=""
    presetFallback=""

    def setAll(self, pn, pm, pf):
        self.presetName = pn
        self.presetMsg = pm
        self.presetFallback = pf
        self.accept()

    def __init__(self, parent, presetName):
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

        if (presetName != ""):
            label1.setVisible(False)
            presetNameBox.setText(presetName)
            presetNameBox.setVisible(False)

            spamMsgBox.setText(preset_messages[presetName]["spam_message"])
            fallbackMsgBox.setText(preset_messages[presetName]["fallback_message"])
        
        btnBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btnBox.accepted.connect(lambda: self.setAll(presetNameBox.text(), spamMsgBox.toPlainText(), fallbackMsgBox.toPlainText()))
        btnBox.rejected.connect(self.reject)

        layout.addWidget(label1)
        layout.addWidget(presetNameBox)
        layout.addWidget(label2)
        layout.addWidget(spamMsgBox)
        layout.addWidget(label3)
        layout.addWidget(fallbackMsgBox)
        layout.addWidget(btnBox)
        self.setFixedSize(250, 400)

        

def addPreset(parent, comboBox, presetName=""):
    global preset_messages
    presetDialog = presetAddWindow(parent, presetName)
    presetDialog.exec()

    if (presetDialog.result() == QDialog.DialogCode.Accepted):
        preset_messages[presetDialog.presetName] = {"spam_message":presetDialog.presetMsg, "fallback_message":presetDialog.presetFallback}
        updatejson()
        presetItemArray = list(preset_messages.keys())
        
        comboBox.clear()
        comboBox.addItems(presetItemArray)
        comboBox.setCurrentText(presetDialog.presetName)

def deletePreset(parent, comboBox):
    global preset_messages
    selectedPreset = QInputDialog.getItem(parent, "Delete Preset", "Select preset to delete", list(preset_messages.keys()), editable=False)
       
    if (selectedPreset[1] == False):
        return

    preset_messages.pop(selectedPreset[0], None)
    updatejson()

    presetItemArray = list(preset_messages.keys())
    
    currentItem = comboBox.currentText()
    comboBox.clear()
    comboBox.addItems(presetItemArray)

    if (currentItem != selectedPreset[0]):
        comboBox.setCurrentText(currentItem)

def setDefaultPreset(comboBox, lb):
    global default_preset
    default_preset = comboBox.currentText()
    lb.setText("Current Default: "+default_preset)
    updatejson()

def updateBotToken(tk):
    global botToken
    botToken = tk
    updatejson()

def updateRndChk(chk):
    global randomize_message
    randomize_message = chk
    updatejson()

def updateToken(tk):
    global token
    token = tk
    updatejson()

def updateMSC(val):
    global maximum_spam_count
    maximum_spam_count = val
    updatejson()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Discord Spammer v.fn")

        mainWidget = QWidget()
        layout=QVBoxLayout(mainWidget)

        botGrpBox = QGroupBox()
        botGrpBox.setTitle("Bot")

        botGrpBoxLayout=QGridLayout(botGrpBox)

        label1 = QLabel()
        label1.setText("Bot Token")

        botTokenBox = QLineEdit()
        botTokenBox.setText(botToken)
        botTokenBox.setEchoMode(QLineEdit.EchoMode.Password)
        botTokenBox.editingFinished.connect(lambda: updateBotToken(botTokenBox.text()))

        button = QPushButton("Start Bot")
        button.pressed.connect(startBot)

        usrGrpBox = QGroupBox()
        usrGrpBox.setTitle("User")
        
        usrGrpBoxLayout=QGridLayout(usrGrpBox)

        label2 = QLabel()
        label2.setText("User Token")
        
        userTokenBox = QLineEdit()
        userTokenBox.setText(token)
        userTokenBox.setEchoMode(QLineEdit.EchoMode.Password)
        userTokenBox.editingFinished.connect(lambda: updateToken(userTokenBox.text()))

        label3 = QLabel()
        label3.setText("Presets")

        presetItemArray = list(preset_messages.keys())

        presetList = QComboBox()
        presetList.addItems(presetItemArray)
        presetList.setCurrentText(default_preset)

        currentDefaultLb = QLabel()
        currentDefaultLb.setText("Current Default: "+default_preset)

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
        editPresetBtn.pressed.connect(lambda: addPreset(self, presetList, presetList.currentText()))

        setDefaultPresetBtn = QPushButton()
        setDefaultPresetBtn.setText("Set as default")
        setDefaultPresetBtn.pressed.connect(lambda: setDefaultPreset(presetList, currentDefaultLb))

        presetBtnsLayout.addWidget(addPresetBtn)
        presetBtnsLayout.addWidget(removePresetBtn)
        presetBtnsLayout.addWidget(editPresetBtn)
        presetBtnsLayout.addWidget(setDefaultPresetBtn)

        randomizeMsgChk = QCheckBox()
        randomizeMsgChk.setText("Randomize (anti-spam protection)")
        randomizeMsgChk.stateChanged.connect(lambda: updateRndChk(randomizeMsgChk.isChecked()))
        randomizeMsgChk.setChecked(randomize_message)

        label4 = QLabel()
        label4.setText("Maximum Spam Count (-1 for unlimited) (leaves after maximum spam count is reached)")
        
        maxSpamCountBox = QSpinBox()
        maxSpamCountBox.setMinimum(-1)
        maxSpamCountBox.setMaximum(65534)
        maxSpamCountBox.setValue(maximum_spam_count)
        maxSpamCountBox.valueChanged.connect(updateMSC)

        startSpamBtn = QPushButton()
        startSpamBtn.setText("Start Spam")
        startSpamBtn.pressed.connect(lambda: startSpam(self))

        label5 = QLabel()
        label5.setText("orangypea.88 <3")

        botGrpBoxLayout.addWidget(label1, 0, 0)
        botGrpBoxLayout.addWidget(botTokenBox, 1, 0)
        botGrpBoxLayout.addWidget(button, 2, 0)
        usrGrpBoxLayout.addWidget(label2, 3, 0)
        usrGrpBoxLayout.addWidget(userTokenBox, 4, 0)
        usrGrpBoxLayout.addWidget(label3, 5, 0)
        usrGrpBoxLayout.addWidget(presetList, 6, 0)
        usrGrpBoxLayout.addWidget(currentDefaultLb, 7, 0)
        usrGrpBoxLayout.addWidget(presetBtns, 8, 0)
        usrGrpBoxLayout.addWidget(randomizeMsgChk, 9, 0)
        usrGrpBoxLayout.addWidget(label4, 10, 0)
        usrGrpBoxLayout.addWidget(maxSpamCountBox, 11, 0)
        usrGrpBoxLayout.addWidget(startSpamBtn, 12, 0)

        layout.addWidget(botGrpBox)
        layout.addWidget(usrGrpBox)
        layout.addWidget(label5)

        self.setCentralWidget(mainWidget)
        self.show()


app = QApplication(sys.argv)
w = MainWindow()
app.exec()
print("Close console window to stop.")
