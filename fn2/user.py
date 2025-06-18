""" 
First argument is port, second argument is authkey.

First message should always be the user token.
"""
from multiprocessing.connection import Client
import threading
import discord
import sys

address = ('localhost', int(sys.argv[1]))
conn = Client(address, authkey=str.encode(sys.argv[2]))

stopSpam = threading.Event()

token=conn.recv()

def stopSpamCall():
    global conn
    global stopSpam

    conn.recv()
    stopSpam.set()

try:
    class MyClient(discord.Client):
        async def on_ready(self):
            global conn
            conn.send({"type":"success", "value":"Logged in as "+str(client.user), "username":str(client.user)})
            while True:
                msg=conn.recv()
                if (msg=="exit"):
                    break
                elif (not isinstance(msg, dict)):
                    conn.send({"type":"error", "value":"Invalid Message."})
                elif (msg["type"] == "check_app"):
                    found=False                    
                    for auth in await self.authorizations():
                        if (auth.application.id == msg["id"]):
                            found=True
                            break
                    conn.send(found)
                elif (msg["type"] == "start_spam"):
                    try:
                        spam_message = msg["spam_message"]
                        fallback_message = msg["fallback_message"]
                        maximum_spam_count = msg["max_spam"]
                        randomize_message = msg["randomize"]
                        guild_id = msg["id"]
                        
                        stopSpam.clear()
                        application = None
                        command = None

                        for auth in await self.authorizations():
                            if auth.application.id == msg["appid"]:
                                application = auth.application
                        
                        if (application == None):
                            conn.send({"type":"error", "value":"Application not found."})
                            continue

                        for cmd in await application.bot.application_commands():
                            if (cmd.name.lower().find("spam") != -1):
                                command = cmd

                        if (command == None):
                            conn.send({"type":"error", "value":"Command not found. (Unsynced Application?)"})
                            continue

                        guild=self.get_guild(int(guild_id))

                        if (guild == None): # possibly a channel
                            channel=self.get_channel(int(guild_id))
                            if (channel == None):
                                conn.send({"type":"error", "value":"Server/Channel not found. (Wrong ID?)"})
                                continue
                            thread = threading.Thread(target=stopSpamCall)
                            thread.start()
                            thread.join()

                            requires_fallback = False
     
                            if (channel.guild):
                                user = channel.guild.get_member(client.user.id)
                                permissions = channel.permissions_for(user)
                                if (not permissions.attach_files):
                                    requires_fallback = True
                            command.target_channel = channel
                            count = 0
                            sccount = 0
                            conn.send({"type":"start", "value":"Spam started."})
                            while (not stopSpam.is_set()):
                                if (maximum_spam_count != -1 and count>=maximum_spam_count):
                                    await client.close()
                                    await guild.leave()
                                    conn.send({"type":"success", "value":"Spam finished.\nTotal Spam count: "+str(count)})
                                    break
                                count+=1
                                command.target_channel = channel
                                if (not requires_fallback):
                                    await command.__call__(channel=channel, text=spam_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                                    sccount += 1
                                else:
                                    await command.__call__(channel=channel, text=fallback_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                                    sccount += 1

                        thread = threading.Thread(target=stopSpamCall)
                        thread.start()

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

                        count = 0
                        sccount = 0
                        conn.send({"type":"start", "value":"Spam started."})
                        while (not stopSpam.is_set()):
                            if (maximum_spam_count != -1 and count>=maximum_spam_count):
                                await client.close()
                                await guild.leave()
                                conn.send({"type":"success", "value":"Spam finished.\nTotal Spam count: "+str(sccount)})
                                break
                            count+=1
                            for channel in validchannels:
                                if (stopSpam.is_set()):
                                    break
                                try:
                                    if (not permissions.view_channel
                                        or not permissions.read_message_history
                                        or not permissions.read_messages
                                        or not permissions.use_application_commands
                                        or not permissions.send_messages
                                        ):
                                        validchannels.remove(channel)
                                        continue
                                    command.target_channel = channel
                                    if (not channel in fallbackchannels):
                                        await command.__call__(channel=channel, text=spam_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                                        sccount += 1
                                    else:
                                        await command.__call__(channel=channel, text=fallback_message, slowmode_delay=channel.slowmode_delay, randomize=randomize_message)
                                        sccount += 1
                                except:
                                    pass
                        conn.send({"type":"success", "value":"Spam finished.\nTotal Spam count: "+str(sccount)})
                    except Exception as e:
                        conn.send({"type":"error", "value":str(e)})

                    
            client.close()
            client.clear()

    client = MyClient()
    client.run(token, log_handler=None)
except Exception as e:
    conn.send({"type":"error", "value":str(e)})

conn.close()
