import os
import discord
from dotenv import load_dotenv
from discord.ext.commands import Bot
from discord.ext import commands
import pyrebase
from story_class import story
from branch_class import branch


#set up keys and tokens
load_dotenv()
TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('API_KEY')
AUTH_DOMAIN = os.getenv('AUTH_DOMAIN')
DATABASE_URL = os.getenv('DATABASE_URL')
STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')

config = {
  "apiKey": API_KEY,
  "authDomain": AUTH_DOMAIN,
  "databaseURL": DATABASE_URL,
  "storageBucket": STORAGE_BUCKET
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
stories = db.child("stories").get()

writHub = commands.Bot(command_prefix="w!")

#poll variables
poll_state = False
users_voted = []
branch_polls = {}

#used to get list of stories
story_keys = []
story_list = []

#used to get branches associated with stories
branch_keys = []
branch_list = []

@writHub.event
async def on_ready():
    global story_keys
    global story_list
    global firebase
    global db
    global stories
    
    print(f'{writHub.user} has connected to Discord!')
    
    for user in stories.each():
        story_keys.append(user.key())

    for key in story_keys:
        current_story = db.child("stories").child(key).get()
        #print(current_story.val()['title'])
        #print(current_story.val()['title'])
        try:
            new_story = story(
            title = current_story.val()['title'],
            date = current_story.val()['date'],
            text = current_story.val()['text'],
            description = current_story.val()['description'])
            story_list.append(new_story)
        except KeyError:
            new_story = story(
            title = current_story.val()['title'],
            date = current_story.val()['date'],
            text = "no branches",
            description = current_story.val()['description'])
            story_list.append(new_story)


@writHub.command(name="view")
async def view (ctx):
    list_display = ''
    for i in range(len(story_list)):
        list_display = list_display + "**"+f'{i+1}'+"**. " + story_list[i].title
        if i != len(story_list) - 1:
            list_display = list_display +  "\n"

    embed = discord.Embed(
        title = "list of stories", 
        description = list_display,
        colour = discord.Colour(0x8d32e3))
    
    await ctx.send(embed = embed)

#Command that takes in a poll of which branch to merge into the main branch
#poll start --> request for data --> display data --> allow vote
#vote --> vote for list entry
#poll end --> embed saying which one was selected --> manages database

@writHub.command(name="poll")
async def poll (ctx, arg, story_num=-1):
    global poll_state
    global users_voted
    global firebase
    global db
    global stories
    global branch_keys
    global branch_list
    global story_keys
    global story_list
    global branch_polls
    print("Poll command received")
    print(story_num)
    if arg == "start" and story_num in range(1,len(story_list) + 1) and not poll_state:
        branch_keys = []
        branch_list = []
        users_voted = []
        branch_polls = {}
        selected_story = story_list[story_num - 1]
        branch_path = db.child("stories").child(story_keys[story_num - 1]).child("text").get()
        for branch_item in branch_path.each():
            branch_keys.append(branch_item.key())
            print(branch_item.key())
        
        for key in branch_keys:
            current_branch = db.child("stories").child(story_keys[story_num - 1]).child("text").child(key).get()
            date_val = current_branch.val()['date']
            text_val = current_branch.val()['text']

            new_branch = branch(
            date = date_val,
            text = text_val,
            ID = key)
            branch_list.append(new_branch)

        list_display = ''
        for i in range(len(branch_list  ) - 1):
            list_display = list_display + "**"+f'{i+1}'+"**. " + branch_list[i+1].text
            if i != len(story_list) - 1:
                list_display = list_display +  "\n"

        embed = discord.Embed(
            title = "Here are the proposed changes:", 
            description = list_display,
            colour = discord.Colour(0x8d32e3))

        await ctx.send('Poll has started for story: ' + str(selected_story.title) + '\nHere is what is the original text:\n' + str(branch_list[0].text))
        await ctx.send(embed = embed)
        await ctx.send("To vote, use w!vote <branch number>")
        poll_state = True
        
        for i in range(len(branch_list) - 1):
            branch_polls.update({i:0})
    
    elif arg == "end" and poll_state:
        await ctx.send("Poll has ended, here are the results:")
        
        display = ''
        for i in range(len(branch_list) - 1): 
            display = display + "**"+f'{i+1}'+"**. " + branch_list[i+1].text + " **has " + str(branch_polls.get(i)) + " vote(s)**" 
            if i != len(story_list) - 1:
                display = display +  "\n"
            
        embed = discord.Embed(
            title = "Here are the results!",
            description = display,
            colour = discord.Colour(0x8d32e3))
            
        await ctx.send(embed = embed)
        poll_state = False

    elif arg =="start" and poll_state:
        await ctx.send("A Poll is already running! Please use w!poll end to end that poll if it is a mistake!")
    
    elif arg =="end" and not poll_state:
        await ctx.send("No polls running")

@writHub.command(name="vote")
async def vote (ctx,arg):
    global poll_state
    global users_voted
    global branch_polls 
    print(branch_polls)
    if poll_state:
        if not ctx.message.author in users_voted:
            await ctx.send("Thank you for your vote!")
            print(branch_polls.get(int(arg) - 1))
            new_value = branch_polls.get(int(arg) - 1) + 1
            print(new_value)
            users_voted.append(ctx.message.author)
            branch_polls.update({int(arg) - 1: new_value})
            print(branch_polls)
        else:
            await ctx.send(f'{ctx.message.author}' + " has already voted!") 
    else:
        await ctx.send("Please start a poll first!")

writHub.run(TOKEN)