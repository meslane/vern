#!/usr/bin/python3

import time
import datetime

import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from discord.utils import get

with open('tokens.txt') as f:
    tokens = f.read().splitlines()

client = Bot(command_prefix = "!")

def tuple2Str(t):
    str = ''
    for item in t:
        str += item + ' '
        
    return str.rstrip(str[-1])

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief = "Ping the bot")
    async def ping(self, ctx):
        await ctx.send("Acknowledge ping from user {}".format(ctx.message.author.name))

class Shopping(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.shop_list = []
        
        self.load("list.txt")
        
    def save(self, filename):
        f = open(filename, 'w')
        f.writelines(line + '\n' for line in self.shop_list)
        f.close()
        
    def load(self, filename):
        f = open(filename, 'r')
        self.shop_list = f.readlines()
        self.shop_list = [s.strip() for s in self.shop_list]
        f.close()
    
    @commands.command(brief = "Display shopping list")
    async def list(self, ctx):
        string = "```\n"
        
        for i, item in enumerate(self.shop_list):
            string += "{}. {}\n".format(i + 1, item)
            
        string += "```"
        await ctx.send(string)

    @commands.command(brief = "Add item to shopping list")
    async def add(self, ctx, *string):
        item = tuple2Str(string)
        self.shop_list.append(item)
        self.save("list.txt")
        await ctx.send("Added {} to the list".format(item))
    
    @commands.command(brief = "Drop item from shopping list")
    async def drop(self, ctx, *indices):
        indexlist = []

        for index in indices:
            try:
                indexlist.append(int(index))
            except ValueError:
                await ctx.send("{} is not a valid list index".format(index))

        indexlist.sort(reverse=True)

        for index in indexlist:
            try:
                if int(index) < 0:
                    raise IndexError
                
                removed = self.shop_list.pop(int(index) - 1)
                self.save("list.txt")
                await ctx.send("Removed {} from the list".format(removed))
            except IndexError:
                await ctx.send("Could not remove that item from the list")    
    
    @commands.command(brief = "Clear the entire shopping list")
    async def clear(self, ctx):
        self.shop_list.clear()
        self.save("list.txt")
        await ctx.send("Cleared the list")

@loop(seconds=60)
async def take_trash():
    await client.wait_until_ready()
    
    with open('args.txt') as f:
        args = f.read().splitlines()        
        ch_id = int(args[0])
        trashtime = args[1]
    
    channel = client.get_channel(ch_id)
    curtime = time.strftime("%w %H %M", time.localtime())

    if (curtime == trashtime):
        print("Sent trash ping at {}".format(curtime))
        await channel.send("<@&890039516591702066> Tomorrow is trash day! TAKE OUT THE TRASH!")
    
@client.event
async def on_ready():
    try:
        client.add_cog(Misc(client))
        client.add_cog(Shopping(client))
        print("All cogs loaded")    
    except discord.ext.commands.errors.CommandRegistrationError:
        print("Failed to load one or more cogs, they may already be loaded")

print("Starting bot...")
take_trash.start()
client.run(tokens[0])
