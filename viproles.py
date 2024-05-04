import discord
import json
import os
from data_access import read_file, write_file

bot = discord.Bot(intents=discord.Intents.all())

server_id = serverid


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# viprole.py

from data_access import read_file, write_file

from data_access import read_file, write_file

@bot.event
async def on_member_update(before, after):
    if "VIP Trainer" in [role.name for role in before.roles] and "VIP Trainer" not in [role.name for role in after.roles]:
        main_file_content = read_file()
        if str(after.id) in main_file_content:
            custom_role_id = main_file_content[str(after.id)].get("roleid")
            if custom_role_id:
                custom_role = discord.utils.get(bot.get_guild(server_id).roles, id=int(custom_role_id))
                if custom_role:
                    try:
                        await custom_role.delete()
                        print(f"Deleted Custom Role for {after.name}")
                        del main_file_content[str(after.id)]
                        write_file(main_file_content)
                    except discord.Forbidden:
                        print(f"Bot doesn't have permission to delete role for {after.name}")
                        await after.send("I need permission to delete your custom role.")
                    except Exception as e:
                        print(f"Error while deleting role: {e}")
                        await after.send("An unexpected error occurred while processing your request.")

for filename in os.listdir('./cogs'):
    if filename.endswith(".py"):
        bot.load_extension(f'cogs.{filename[:-3]}')
        print(f'Successfully Enabled cogs.{filename[:-3]}' + ' extension')

bot.run('TOKEN')
