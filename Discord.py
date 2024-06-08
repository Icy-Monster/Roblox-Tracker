import requests
import json

import asyncio 
import datetime

import discord
from discord import app_commands



Token = "" # Set this to your Discord Bot's Token

Intents = discord.Intents.default()
Client = discord.Client(intents=Intents)

Tree = app_commands.CommandTree(Client)
##########################################

# These are .txt files that list the user ids, you can find out how to get them here: https://github.com/Icy-Monster/Roblox-Group-Scraper for other groups
AdminList = open(r"/home/icy/Desktop/Admins.txt", 'r').readlines()
StarList = open(r"/home/icy/Desktop/StarCreators.txt", 'r').readlines()

# The UsernameRequest is not in order, so this is just a quick botch
async def GetUser(UserList: tuple[str], ID: int):
    for User in UserList:
        if User["id"] == ID:
            return User

async def FetchStatus(UserIDs: tuple[int], Channel: discord.channel, Emoji: str) -> tuple[int]:
    headers = {
        'Content-Type': 'application/json','Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Cookie': ".ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|" # Set this to your Roblox Cookie, I recommend making a new account for this- as to not ratelimit your main account
    }

    StatusRequest = requests.post('https://presence.roblox.com/v1/presence/users', headers=headers, data=json.dumps({"userIds": UserIDs}))

    UsernameRequest = requests.post('https://users.roblox.com/v1/users', headers=headers, data=json.dumps({"userIds": UserIDs}))
    UsernameRequest = json.loads(UsernameRequest.content.decode('utf-8'))["data"]

    for User in json.loads(StatusRequest.content.decode('utf-8'))["userPresences"]:
        Playing = User["userPresenceType"] == 2
        
        if not Playing: pass

        content = ""
        color = 0xff0000
        Description = "**Cannot join user**"

        if User["placeId"] != None:
            content = "@everyone"
            color = 0x00af00
            Description = "**[Join](https://www.roblox.com/games/start?placeId=16302670534&launchData=" + str(User["placeId"]) + "/" + User["gameId"] + ") them in ["+ User["lastLocation"] +"](https://www.roblox.com/games/"+ str(User["placeId"]) +")**"

        UserInfo = await GetUser(UsernameRequest, User["userId"])

        Title = "** "+ Emoji +" "+ UserInfo["displayName"] +" (@"+ UserInfo["name"] +")**"

        Embed = discord.Embed(
            title=Title,
            description=Description,
            color=color,
            timestamp=datetime.datetime.now(),
            url="https://www.roblox.com/users/"+ str(User["userId"]) +"/profile",
            )
        await Channel.send(embed=Embed,content=content)
        


@Client.event
async def on_ready():
    Channel = Client.get_channel() # Change this to the channel you want the join activity logged

    # 50 users are sent at a time, for faster logging- 50 is the limit Roblox allows
    while True:
        for i in range( round(sum(1 for _ in AdminList) / 50) ):
            UserList = AdminList[i*50  :  i*50 + 50]

            await FetchStatus(UserList, Channel, "🛡️ ") # ⭐  🛡️
            await asyncio.sleep(18)

##########################################
Client.run(Token)
