import requests
import json

import asyncio
import datetime

import discord

# TODO: Check if the place is private, most likely requires an extra api call

Token = "" # Set this to your Discord Bot's Token

Intents = discord.Intents.default()
Client = discord.Client(intents=Intents)
##########################################

# These are .txt files that list the user ids, you can find out how to get them here: https://github.com/Icy-Monster/Roblox-Group-Scraper for other groups
AdminList = open(r"C:\Users\Monster\Desktop\Admins.txt", 'r').readlines() # change the location to fit your file path
StarList = open(r"C:\Users\Monster\Desktop\StarCreators.txt", 'r').readlines() # change the location to fit your file path

Messages = {}

# The UsernameRequest is not in order, so this is just a quick botch
async def GetUser(UserList: tuple[str], ID: int):
    for User in UserList:
        if User["id"] == ID:
            return User

async def FetchStatus(UserIDs: tuple[int], Channel: discord.channel, Emoji: str) -> tuple[int]:
    headers = {
        'Content-Type': 'application/json','Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        "Cookie": ".ROBLOSECURITY=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|" # Add your Roblox Security cookie here, I recommend using a spare account so you don't get timed out
    }

    StatusRequest = requests.post('https://presence.roblox.com/v1/presence/users', headers=headers, data=json.dumps({"userIds": UserIDs}))

    UsernameRequest = requests.post('https://users.roblox.com/v1/users', headers=headers, data=json.dumps({"userIds": UserIDs}))
    UsernameRequest = json.loads(UsernameRequest.content.decode('utf-8'))["data"]

    for User in json.loads(StatusRequest.content.decode('utf-8'))["userPresences"]:
        Playing = User["userPresenceType"] == 2
        UserInfo = await GetUser(UsernameRequest, User["userId"])

        # Make sure to only post users who have not already been posted and are *currently* playing, otherwise remove them
        if not Playing:
            if UserInfo["name"] in Messages:
                await Messages[UserInfo["name"]].delete()
                del Messages[UserInfo["name"]]
            continue
        if User["placeId"] == None: continue
        if UserInfo["name"] in Messages: continue

        Description = "**[Join](https://www.roblox.com/games/start?placeId=16302670534&launchData=" + str(User["placeId"]) + "/" + User["gameId"] + ") them in ["+ User["lastLocation"] +"](https://www.roblox.com/games/"+ str(User["placeId"]) +")**"

        # The Title is DisplayName (@username) or only @username if they're the same
        Title = "** "+ Emoji +" @"+ UserInfo["displayName"] +"**"
        if UserInfo["displayName"] != UserInfo["name"]:
            Title += " (@"+ UserInfo["name"] +")**"
        
        Embed = discord.Embed(
            title=Title,
            description=Description,
            color=0x00af00,
            timestamp=datetime.datetime.now(),
            url="https://www.roblox.com/users/"+ str(User["userId"]) +"/profile",
            )
        
        Message = await Channel.send(embed=Embed,content= Emoji + "@everyone")
        Messages[UserInfo["name"]] = Message



@Client.event
async def on_ready():
    Channel = Client.get_channel() # Change this to the channel you want the join activity logged

    # 50 users are sent at a time, for faster logging- 50 is the limit Roblox allows
    while True:
        try:
            for i in range( round(sum(1 for _ in AdminList) / 50) ):
                UserList = AdminList[i*50  :  i*50 + 50]
                
                await FetchStatus(UserList, Channel, "<:Admin:1257345106009264148>") # <:Admin:1257345106009264148>  <:IcyIsStupid:1257351523868999763>
                await asyncio.sleep(18)
        except:
            pass

##########################################
Client.run(Token)