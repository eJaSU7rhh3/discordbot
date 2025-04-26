from tkinter import messagebox
import subprocess
import platform
import os
import sys
import requests
import urllib.request
import zipfile

print("orangypea.88 <3")

url="https://raw.githubusercontent.com/eJaSU7rhh3/discordbot/refs/heads/main/fn/"

versionurl=url+"version"
newversion = requests.get(versionurl).text

def write(path, contents):
    f=open(path, "w")
    f.write(contents)
    f.close()

def read(path):
    f=open(path, "r")
    contents=f.read()
    f.close()
    return contents

def install():
    print("Installing scripts...")
    updatedBot = requests.get(url+"bot.py").text
    updatedUser = requests.get(url+"user.py").text
    updatedGui = requests.get(url+"gui.py").text

    write("bin/bot.py", updatedBot)
    write("bin/user.py", updatedUser)
    write("bin/gui.py", updatedGui)
    write("version.txt", newversion)

    print("Installing dependencies...")
    write("dependencies/bot.txt", requests.get(url+"bot-dependencies.txt").text)
    write("dependencies/user.txt", requests.get(url+"user-dependencies.txt").text)
    write("dependencies/gui.txt", requests.get(url+"gui-dependencies.txt").text)

    urllib.request.urlretrieve("https://github.com/dolfies/discord.py-self/archive/refs/heads/master.zip", "dependencies/discord-py-self.zip")
    with zipfile.ZipFile("dependencies/discord-py-self.zip", 'r') as zip_ref:
        zip_ref.extractall("dependencies")

    if (platform.system() == "Linux"):
        subprocess.run(["venv/bot/bin/pip", "install", "-r", "dependencies/bot.txt"])
        subprocess.run(["venv/user/bin/pip", "install", "-r", "dependencies/user.txt"])
        subprocess.run(["venv/gui/bin/pip", "install", "-r", "dependencies/gui.txt"])
    elif (platform.system() == "Windows"):
        subprocess.run(["venv\\bot\\Scripts\\pip", "install", "-r", "dependencies\\bot.txt"])
        subprocess.run(["venv\\user\\Scripts\\pip", "install", "-r", "dependencies\\user.txt"])
        subprocess.run(["venv\\gui\\Scripts\\pip", "install", "-r", "dependencies\\gui.txt"])

if (os.path.isfile("version.txt")):
    # update
    currentversion=read("version.txt")

    if (currentversion == newversion.replace("\n", "")):
        doUpdate = messagebox.askquestion("Dialog", "Would you like to update the script?\nCurrent Version: "+currentversion+"New Version: "+newversion)
        
        if (doUpdate == "yes"):
            print("Updating Discord Spammer...")
            os.remove("bin/bot.py")
            os.remove("bin/user.py")
            os.remove("bin/gui.py")
            install()
else:
    # bootstrap
    os.mkdir("bin")
    os.mkdir("venv")
    os.mkdir("dependencies")

    print("Setting up virtual environments...")
    if (platform.system() == "Linux"):
        subprocess.run(["python3", "-m", "venv", "venv/user"])
        subprocess.run(["python3", "-m", "venv", "venv/bot"])
        subprocess.run(["python3", "-m", "venv", "venv/gui"])
    elif (platform.system() == "Windows"):
        pexc_name = "py"
        
        if (not shutil.which("py")):
            pexc_name = "python3"

        subprocess.run([pexc_name, "-m", "venv", "venv\\user"])
        subprocess.run([pexc_name, "-m", "venv", "venv\\bot"])

    install()

# launch

print("Launching...")

if (platform.system() == "Linux"):
    subprocess.run(["venv/gui/bin/python3", "bin/gui.py"])
elif (platform.system() == "Windows"): 
    subprocess.run(["venv\\gui\\Scripts\\python3", "bin\\gui.py"])

