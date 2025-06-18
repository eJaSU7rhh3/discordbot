from multiprocessing.connection import Client
import discord
from discord import app_commands
from discord.ext import commands
import random
import string
import time
import sys
import os

address = ('localhost', int(sys.argv[1]))
conn = Client(address, authkey=str.encode(sys.argv[2]))

token=conn.recv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
    name="spam",
    description="uhh"
)
@app_commands.describe(text="text")
async def spam(interaction, text: str, slowmode_delay: int = 0, randomize: bool = False):
    await interaction.response.send_message("orangypea <3 gg/cnSX6CFBJr", ephemeral=True, silent=True)
    
    ws = interaction.followup

    if (len(text)>2000):
        # too big
        return

    subtext = text

    if (randomize):
        available_length = 1999-len(text)

        if (available_length < 6):
            randomize = False

    for i in range(0,5):
        if (randomize):
            x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
            subtext=text+" "+x
        await ws.send(subtext, silent=True)
        if (slowmode_delay>0):
            return

@tree.command(
    name="send",
    description="send one message"
)
@app_commands.describe(text="send")
async def send(interaction, text: str):
    await interaction.response.send_message("orangypea <3", ephemeral=True)
    
    ws = interaction.followup
    await ws.send(text, silent=True)

@client.event
async def on_ready():
    global conn
    if (not os.path.exists("synced/"+str(client.application_id))):
        await tree.sync()
        if (not os.path.isdir("synced")):
            os.mkdir("synced")
        sf=open("synced/"+str(client.application_id), "w")
        sf.write(".")
        sf.close()
    conn.send({"type":"success", "value":"Logged in as "+str(client.user), "displayname":client.user.display_name, "appid":client.application_id, "username": str(client.user)})

try:
    client.run(token, log_handler=None)
except Exception as e:
    conn.send({"type":"error", "value":str(e)})
