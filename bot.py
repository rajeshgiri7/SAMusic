import discord
from discord.ext import commands, tasks
from discord.utils import get
from random import choice

client = commands.Bot(command_prefix=commands.when_mentioned_or(";"),help_command=commands.DefaultHelpCommand(no_category = 'Other'))
client.load_extension('cogs.music')
status = ['लङुर बुर्जा','बाघ चाल','आफै सँग','डन्डीबियो','भाडाकुटी']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is Ready.')
    
@client.command(name='prefix',help='This command return the prefix')
async  def prefix(ctx):
    await ctx.send(embed=(discord.Embed(title='🌀 The prefix of this bot is ```;```',
                                    color=discord.Color.purple())
                        ))

# @client.event
# async def on_message(message):
#     await client.delete_message("```elm\nSearching\n```",delay=7)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'```css\nCommand not Available\n```')
        return
    raise error

@client.command(name='ping',help='This command return the latency')
async  def ping(ctx):
    await ctx.send(f'```yml\nPing:{round(client.latency*1000)}ms\n```')

@client.command(name='credits',help='This command returns the credits')
async def credits(ctx):
        await ctx.send('```yml\nडेवलपरहरु : राजेश गिरी & साजन श्रेष्ठ\n```')
    
@client.command(name='helpers',help='This command returns the helpers')
async def helper(ctx):
        await ctx.send('```yml\nसहयोगीहरु : उज्ज्वल खनाल & सन्दिप नेपाल\n```')

@tasks.loop(seconds=696)
async def change_status():
       await client.change_presence(activity=discord.Game(choice(status)))
client.run('Nzg1ODQ0MzA4NDY0MTA3NTIy.X89wiw.e8zMgTtiMnAaflmezeVN109Aj1w')
