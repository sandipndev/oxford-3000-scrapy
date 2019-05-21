import discord
from discord.ext import commands
from classword import Word

cctwordplaintextmeanings = []

# Enter your Discord token here
TOKEN = ""
client = commands.Bot(command_prefix = 'a/')

async def statchanger():
	await client.wait_until_ready()
	await client.change_presence(game=discord.Game(name=" Oxford 3000"))

@client.event
async def on_ready():
	print ("Bot is online and ready!")

@client.command(pass_context = True)
async def mean(ctx, *words):
	for thisword in words:
		print ("Asked meaning of {}".format(thisword))
		ob = Word()
		ob.setname(thisword)
		for x in ob.return_embeds(ctx):
			await client.send_message(ctx.message.channel, embed = x)

client.loop.create_task(statchanger())
client.run(TOKEN)