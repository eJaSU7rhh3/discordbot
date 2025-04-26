import discord
from discord import app_commands
from discord.ext import commands
import random
import string
import time
import sys
import os

token=sys.argv[1]

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
    name="spam",
    description="uhh"
)
@app_commands.describe(text="text")
async def spam(interaction, text: str, slowmode_delay: int = 0, randomize: bool = False):
    await interaction.response.send_message("orangypea.88 <3", ephemeral=True, silent=True)
    
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
    await interaction.response.send_message("orangypea.88 <3", ephemeral=True, silent=True)
    
    ws = interaction.followup
    await ws.send(text, silent=True)

@client.event
async def on_ready():
    print("Syncing")
    await tree.sync()
    print("Ready!")

client.run(token)
