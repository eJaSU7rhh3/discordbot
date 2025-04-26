import discord
from discord.ext import commands
import os
import json
import sys
import time
import urllib.request

spam_message = sys.argv[1]
fallback_message = sys.argv[2]
token = sys.argv[3]
application_name = sys.argv[4]
command_name = sys.argv[5]
guild_id = sys.argv[6]
randomize_message = sys.argv[7]
maximum_spam_count = int(sys.argv[8])

if (randomize_message == "y"):
    randomize_message = True
else:
    randomize_message = False

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        application=None
        for auth in await self.authorizations():
            if auth.application.name.lower().find(application_name.lower()) != -1:
                print(auth.application.name+" found!")
                application = auth.application
                break

        if (application == None):
            print(application_name+" not found.")
            await client.close()
            return

        command=None
        
        for cmd in await application.bot.application_commands():
            if (cmd.name.lower().find(command_name.lower()) != -1):
                command = cmd

        if (command == None):
            print("Command not found.")
            await client.close()
            return

        guild=client.get_guild(int(guild_id))

        if (guild == None):
            print("Guild not found.")
            
            channel=self.get_channel(int(guild_id))
            if (channel != None):
                print("Channel detected.")
                requires_fallback = False
 
                if (channel.guild):
                    user = channel.guild.get_member(client.user.id)
                    permissions = channel.permissions_for(user)
                    if (not permissions.attach_files):
                        requires_fallback = True
                        print("Fallback needed.")

                command.target_channel = channel
                count=0
                while True:
                    if (maximum_spam_count != -1 and count>=maximum_spam_count):
                        await client.close()
                        print("Spam finished.")
                        await guild.leave()
                        break
                    count+=1
                    command.target_channel = channel
                    if (not requires_fallback):
                        await command.__call__(channel=channel, text=spam_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                    else:
                        await command.__call__(channel=channel, text=fallback_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                    print("sent in channel.")

            await client.close()
            return
        else:
            print("Guild \""+guild.name+"\" found!")

        validchannels = []
        fallbackchannels = []

        user = guild.get_member(client.user.id)

        for channel in guild.channels:
            if (channel.type == discord.ChannelType.category):
                 continue
            permissions = channel.permissions_for(user)

            if (not permissions.view_channel
                or not permissions.read_message_history
                or not permissions.read_messages
                or not permissions.use_application_commands
                or not permissions.send_messages
                ):
                continue
            validchannels.append(channel)
            if (not permissions.attach_files):
                fallbackchannels.append(channel)

        count=0
        while True:
            if (maximum_spam_count != -1 and count>=maximum_spam_count):
                await client.close()
                print("Spam finished.")
                await guild.leave()
                break
            count+=1
            for channel in validchannels:
                try:
                    command.target_channel = channel
                    if (not permissions.view_channel
                        or not permissions.read_message_history
                        or not permissions.read_messages
                        or not permissions.use_application_commands
                        or not permissions.send_messages
                        ):
                        validchannels.remove(channel)
                        continue
                    if (not channel in fallbackchannels):
                        await command.__call__(channel=channel, text=spam_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                    else:
                        await command.__call__(channel=channel, text=fallback_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)

                    print("sent in #"+channel.name)
                except Exception as e:
                    if (e == KeyboardInterrupt or "Session" in str(e)):
                        await client.close()
                        sys.exit(0)
                        break
                    print(e)
                    print("failed to send command")


client = MyClient()
client.run(token)
