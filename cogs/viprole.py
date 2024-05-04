import discord
from discord.commands import slash_command, SlashCommandGroup
from discord.commands import Option
from discord.ext import commands
import json
import requests
from data_access import read_file, write_file

role_id = "ROLE_ID_HERE"

template = {
    "name": "default",
    "colour": "",
    "emoji": "",
    "roleid": ""
}

def get_emoji_url(text: str):
    if text.startswith("<:") or text.startswith("<a:") and text.endswith(">"): 
        [first, _, third] = text.split(":")
        emojiId = third.replace(">", "")
        # Only returns the png version of the emoji, Role icons only work for png, jpg and apngs (not gif)
        return f"https://cdn.discordapp.com/emojis/{emojiId}.png" 
        # This code is to support animate emojis but it doesn't work due to ^ above 
        # if first.startswith("<a"): 
        #     return f"https://cdn.discordapp.com/emojis/{emojiId}.gif" # Currently doesn't work correctly since Discord only accepts apngs and not gifs 
        # else: 
        #     return f"https://cdn.discordapp.com/emojis/{emojiId}.png"

def read_file():
    with open("data.json", "r") as file:
        return json.load(file)

def write_file(json_object):
    json_object = json.dumps(json_object, indent=4)
    with open("data.json", "w") as outfile:
        outfile.write(json_object)


class role(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    role = SlashCommandGroup("role", "Config Commands")

    @role.command(description='Update Role Name')
    async def name(
            self,
            ctx,
            parameter: Option(str, "Enter Name for the Role", required=True)): # type: ignore
        await ctx.response.defer(ephemeral=True)

        if any(r.id == int(role_id) for r in ctx.author.roles):

            main_file_content = read_file()

            if str(ctx.author.id) in main_file_content:
                already_content = main_file_content[str(ctx.author.id)]
                oldname = already_content['name']
                oldid = already_content['roleid']
                already_content['name'] = str(parameter)
                main_file_content[str(ctx.author.id)] = already_content
                write_file(main_file_content)               

                role = ctx.guild.get_role(int(already_content['roleid']))
                await role.edit(name = parameter, reason=f"Role Edit by {ctx.author.name}")

                embed = discord.Embed(
                    description=f"Role Name Updated from `{oldname}` to <@&{oldid}>", color=0x2E3136)
                await ctx.respond(embed=embed)
            else:
                main_file_content = read_file()
                newtemp = template
                newtemp['name']  = parameter

                role = await ctx.guild.create_role(name=parameter, reason=f"VIP Role Creation by {ctx.author.name}")


                await role.edit(position=45)
                await ctx.author.add_roles(role)
                newtemp["roleid"] = str(role.id)
                main_file_content[str(ctx.author.id)] = newtemp 
                write_file(main_file_content)

                embed = discord.Embed(
                    description=f"<@&{str(role.id)}> Role Created for {str(ctx.author.name)}", color=0x2E3136)
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="You do not have an Active VIP Membership", color=0x2E3136)
            await ctx.respond(embed=embed)

    @role.command(description='Add Colour to Role')
    async def colour(
            self,
            ctx,
            parameter: Option(str, "Enter HexColour for the Role", required=True)): # type: ignore
        await ctx.response.defer(ephemeral=True)

        parameter = parameter.replace('#', '').replace('0x', '')
        parameter = "0x" + parameter

        if any(r.id == int(role_id) for r in ctx.author.roles):
            main_file_content = read_file()

            if str(ctx.author.id) in main_file_content:
                already_content = main_file_content[str(ctx.author.id)]
                already_content['colour'] = str(parameter)
                oldid = already_content['roleid']

                main_file_content[str(ctx.author.id)] = already_content
                write_file(main_file_content)

                #role colour update 
                await ctx.guild.get_role(int(oldid)).edit(color=int(parameter, 16), reason=f"Role Colour Edit by {ctx.author.name}")

                embed = discord.Embed(
                    description=f"Role Colour Updated to #{parameter.replace('0x', '')} <@&{oldid}>", color=0x2E3136)
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                    title="Please use `/role name` command first!", color=0x2E3136)
                await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="You do not have an Active VIP Membership", color=0x2E3136)
            await ctx.respond(embed=embed)

    @role.command(description="Add Icon to Custom Role")
    async def icon(self, ctx, parameter: Option(str, "Enter an Emoji", required=True)): # type: ignore

        await ctx.response.defer(ephemeral=True)
        eparameter = parameter
        parameter = parameter.split(':')[-1].replace('>','')
        main_file_content = read_file()

        if any(r.id == int(role_id) for r in ctx.author.roles):
            if str(ctx.author.id) in main_file_content:
                try:
                    url = get_emoji_url(eparameter)
                    if url is None: 
                        already_content = main_file_content[str(ctx.author.id)]
                        already_content['emoji'] = eparameter
                        rlid = already_content['roleid']
                        await ctx.guild.get_role(int(rlid)).edit(unicode_emoji=eparameter)

                        main_file_content[str(ctx.author.id)] = already_content
                        write_file(main_file_content)

                        embed = discord.Embed(description=f"Role Icon Updated to {eparameter}", color=0x2E3136)
                        embed.set_footer(text=f"Send a message in any channel to test your role icon. \n\nIf you're unable to see your role icon, make sure you've used the command correctly")
                        return await ctx.respond(embed=embed)
                    already_content = main_file_content[str(ctx.author.id)]

                    response = requests.get(url)
                    data = response.content

                    already_content['emoji'] = url

                    rlid = already_content['roleid']
                    await ctx.guild.get_role(int(rlid)).edit(icon=(data))

                    main_file_content[str(ctx.author.id)] = already_content
                    write_file(main_file_content)

                    embed = discord.Embed(description=f"Role Icon Updated to {url}", color=0x2E3136)
                    await ctx.respond(embed=embed)

                except Exception as e:
                    print(e)
                    embed = discord.Embed(
                        title="Icon Set Successfully :white_check_mark:", color=0x2E3136)
                    embed.set_footer(text=f"Send a message in any channel to test your role icon. \n\nIf you're unable to see your role icon, make sure you've used the command correctly")
                    await ctx.respond(embed=embed)



            else:
                embed = discord.Embed(
                    title="Please use `/role name` command first!", color=0x2E3136)
                await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="You do not have an Active VIP Membership", color=0x2E3136)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(role(bot))
