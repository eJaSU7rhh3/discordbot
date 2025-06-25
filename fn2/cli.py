from multiprocessing.connection import Listener
from contextlib import closing
import subprocess
import threading
import platform
import socket
import signal
import time
import json
import uuid
import os

def clear():
    os.system('cls' if os.name == 'nt' else "printf '\033c'")

clear()
print("Discord Spammer v.FN")
print("orangypea <3")
print("https://discord.gg/cnSX6CFBJr")
print("Initializing...")

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

def auth():
    clear()
    global userProc

    if (userProc != None):
        userProc.kill()

    global userInfo
    global botInfo
    global userPort
    global netAuth
    global uConn
    while True:
        print("To get the token for your personal account:\n\n1. Open Discord in your web browser and login\n2. Open any server or direct message channel\n3. Press *Ctrl+Shift+I* to show developer tools\n4. Navigate to the *Network* tab\n5. Press *Ctrl+R* to reload\n6. Switch between random chnanels to trigger network requests\n7. Search for a request that starts with *messages*\n8. Select the *Headers* tab on the right\n9. Scroll down to the *Request Headers* section\n10. Copy the value of the *authorization* header\n")
        token=input("Enter your Discord Token: ")
        clear()
        userProc = None
        if (os.name == "posix"):
            userProc = subprocess.Popen(["venv/user/bin/python3", "bin/user.py", str(userPort), netAuth])
        elif (os.name == "nt"): 
            userProc = subprocess.Popen(["venv\\user\\Scripts\\python", "bin/user.py", str(userPort), netAuth])

        time.sleep(1)
        uConn = listener.accept()
        uConn.send(token)
        result = uConn.recv()
        print("** "+result["value"]+" **\n")
        if (result["type"] != "error"):
            settings["token"] = token
            userInfo["username"] = result["username"]

            if (botInfo["appid"] != 0):
                uConn.send({"type":"check_app", "id":botInfo["appid"]})
                hasApp = uConn.recv()
                if (not hasApp):
                    print("You should install the application to your Discord Account.\nhttps://discord.com/oauth2/authorize?client_id="+str(botInfo["appid"]))
                    input("Press Enter to continue...")
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
        token=input("Enter your Discord Bot Token: ")
        clear()
        botProc = None
        if (os.name == "posix"):
            botProc = subprocess.Popen(["venv/bot/bin/python3", "bin/bot.py", str(userPort), netAuth])
        elif (os.name == "nt"):
            botProc = subprocess.Popen(["venv\\bot\\Scripts\\python", "bin/bot.py", str(userPort), netAuth])
        time.sleep(1)
        bConn = listener.accept()
        bConn.send(token)
        result = bConn.recv()
        print("** "+result["value"]+" **\n")
        if (result["type"] != "error"):
            uConn.send({"type":"check_app", "id":result["appid"]})
            hasApp = uConn.recv()
            if (not hasApp):
                print("You should install the application to your Discord Account.\nhttps://discord.com/oauth2/authorize?client_id="+str(result["appid"]))
                input("Press Enter to continue...")
            settings["bot_token"] = token
            botInfo["displayname"] = result["displayname"]
            botInfo["appid"] = result["appid"]
            botInfo["username"] = result["username"]
            applySettings()
            break
        bConn.close()

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
    print(result["value"])
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
    print(result["value"])
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
            print("You should install the application to your Discord Account.\nhttps://discord.com/oauth2/authorize?client_id="+str(botInfo["appid"]))
            input("Press Enter to continue...")

def logout():
    settings["token"] = ""
    applySettings()
    auth()

def callStopSpam():
    input()
    uConn.send('')

def startSpam():
    if (len(settings["presets"]) < 1):
        print("No presets available.")
        return
    while True:    
        clear()        
        print("Preset:"+settings["presets"][settings["default_preset"]]["name"]+" ("+str(settings["default_preset"])+")\n[0] Back\n[1] Start\n[2] Change Preset")
        option = input("Option: ")

        if (option == "0"):
            break
        elif (option == "1"):  
            clear()
            spamid = input("Server/Channel id: ")
            uConn.send({"type":"start_spam", "spam_message":settings["presets"][settings["default_preset"]]["spam"], "fallback_message":settings["presets"][settings["default_preset"]]["fallback"], "max_spam":settings["auto_leave"], "randomize":settings["randomize"], "id":spamid, "appid":botInfo["appid"]})
            clear()
            thread = threading.Thread(target=callStopSpam)
            thread.start()
            chanlist={}
            while True:
                msg = uConn.recv()
                if (not isinstance(msg, dict)):
                    continue # invalid
                elif (msg["type"] == "error" or msg["type"] == "success"):
                    print(msg["value"])
                    break
                elif (msg["type"] == "alert"):
                    print(msg["value"])
                elif (msg["type"] == "chanlist"):
                    chanlist = msg["value"]
                elif (msg["type"] == "info"):
                    clear()
                    chanlist[msg["id"]]["count"] += 1
                    print("Press Enter to stop spam.\n###")
                    for chanid in list(chanlist.keys()):
                        print("#"+chanlist[chanid]["name"]+" ["+str(chanlist[chanid]["count"])+"]"+" - "+chanid[-5:])
                    
            input("Press Enter to continue...")
        elif (option == "2"):
            for index in range(0, len(settings["presets"])):
                print("["+str(index)+"] "+settings["presets"][index]["name"])
            tbd = input("Option: ")
            
            if (tbd.isdigit() and len(settings["presets"]) > int(tbd)):
                settings["default_preset"] = int(tbd)
                applySettings()

def presetsToList():
    global settings
    presetList = []

    for preset in settings["presets"]:
        presetList.append(preset["name"])

def managePresets():
    while True:
        clear()
        print("[q] Back\n[+] Add Preset\n")   
        for index in range(0, len(settings["presets"])):
            print("["+str(index)+"] "+settings["presets"][index]["name"])
        tbd = input("Option: ")

        if (tbd.lower() == "q"):
            break
        elif (tbd == "+"):
            try:
                clear()
                while True:
                    presetName = input("Preset Name: ")
                    if (presetName in presetsToList()):
                        print("Preset name already exists.")
                    else:
                        break
                clear()            
                print("Enter/Paste your content. Ctrl-D or Ctrl-Z (windows) to save it.\nSpam Message:")
                contents = []
                while True:
                    try:
                        line = input()
                    except EOFError:
                        break
                    contents.append(line)
                spamMessage = "\n".join(contents)
                clear()
                print("Enter/Paste your content. Ctrl-D or Ctrl-Z (windows) to save it.\nFallback Message:")
                contents = []
                while True:
                    try:
                        line = input()
                    except EOFError:
                        break
                    contents.append(line)
                fallbackMessage = "\n".join(contents)

                clear()
                confirmPrompt = input("Preset Name: "+presetName+"\nSpam Message: "+spamMessage+"\nFallback Message: "+fallbackMessage+"\n\nConfirm? (Y/n)")

                if (confirmPrompt.lower() == "n"):
                    print("\nPreset not created.")
                    time.sleep(0.5)
                    continue
                settings["presets"].append({"name":presetName, "spam":spamMessage, "fallback":fallbackMessage})
                applySettings()
            except:
                print("\nPreset not created.")
                time.sleep(0.5)
        elif (tbd.isdigit()):
            clear()
            print("[0] Delete\n[1] Rename\n[2] Edit Spam Message\n[3] Edit Fallback Message\n[4] View Spam Message\n[5] View Fallback Message")
            option=input("Option: ")
            if (option=="0"):
                del settings["presets"][int(tbd)]
            elif (option=="1"):
                newName=input("New Name: ")
                if (newName == ""):
                    print("Name not changed.")
                    time.sleep(0.5)
                elif (newName in presetsToList()):
                    print("Preset name already exists.")
                else:
                    settings["presets"][int(tbd)]["name"] = newName
            elif (option=="2"):
                try:
                    clear()            
                    print("Enter/Paste your content. Ctrl-D or Ctrl-Z (windows) to save it.\nSpam Message:")
                    contents = []
                    while True:
                        try:
                            line = input()
                        except EOFError:
                            break
                        contents.append(line)
                    spamMessage = "\n".join(contents)
                    clear()
                    if (spamMessage.replace("\n", "") == ""):
                        print("Spam message not changed.")
                        time.sleep(0.5)
                    else:
                        settings["presets"][int(tbd)]["spam"] = spamMessage
                except:
                    print("Spam message not changed.")
                    time.sleep(0.5)
            elif (option=="3"):
                try:
                    clear()            
                    print("Enter/Paste your content. Ctrl-D or Ctrl-Z (windows) to save it.\nFallback Message:")
                    contents = []
                    while True:
                        try:
                            line = input()
                        except EOFError:
                            break
                        contents.append(line)
                    spamMessage = "\n".join(contents)
                    clear()
                    if (spamMessage.replace("\n", "") == ""):
                        print("Fallback message not changed.")
                        time.sleep(0.5)
                    else:
                        settings["presets"][int(tbd)]["fallback"] = spamMessage
                except:
                    print("Fallback message not changed.")
                    time.sleep(0.5)
            elif (option=="4"):
                clear()
                print(settings["presets"][int(tbd)]["spam"]+"\n")
                input("Press Enter to continue...")
            elif (option=="5"):
                clear()
                print(settings["presets"][int(tbd)]["fallback"]+"\n")
                input("Press Enter to continue...")
            applySettings()

def otherSettings():
    clear()
    while True:
        clear()
        entry = input(
"0- Back\n"
+"1- Toggle Randomize Messages "
+ ("[on]" if settings["randomize"] else "[off]"+"") # on/off randomize message status
+"\n2- Auto Leave Guild: "
+("after "+str(settings["auto_leave"])+" messages" if settings["auto_leave"] != -1 else "Never (-1)") # auto leave value
+"\nOption: "
)
        if (entry == "0"):
            clear()
            break
        elif (entry == "1"):
            settings["randomize"] = not settings["randomize"]
            applySettings()
        elif (entry == "2"):
            clear()
            newAutoLeave = input("New Auto Leave Value (current: "+str(settings["auto_leave"])+"): ")

            nv = -1

            try:
                nv=int(newAutoLeave)
            except:
                nv=[]

            if ((not isinstance(nv, int) and newAutoLeave != "never") or (isinstance(nv, int) and nv < -1)):
                print("Invalid Value.")
                time.sleep(0.5)
            elif (newAutoLeave == "never"):
                settings["auto_leave"] = -1
            elif (isinstance(nv, int)):
                settings["auto_leave"] = nv
            applySettings()

functions = {"0":0, "1":startSpam, "2":managePresets, "3":otherSettings, "4": setupBot, "5": logout}

while True:
    clear()
    entry = input("Logged in as "+userInfo["username"]+"\nBot: "+botInfo["username"]+"\n0- Exit\n1- Start Spam\n2- Manage Presets\n3- Other Settings\n4- Reconfigure Bot\n5- Logout\nOption: ")
    
    if (entry != "0" and entry in functions):
        functions[entry]()
    elif (not entry in functions):
        print("Invalid Option.")
        time.sleep(0.5)
    else:
        clear()
        userProc.kill()
        botProc.kill()
        break
