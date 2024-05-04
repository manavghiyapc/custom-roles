import discord
from discord.commands import slash_command, SlashCommandGroup
from discord.commands import Option
from discord.ext import commands
import json
import requests
from data_access import read_file, write_file

template = {
    "name": "default",
    "colour": "",
    "emoji": "",
    "roleid": ""
}

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
            parameter: Option(str, "Enter Name for the Role", required=True)):
        await ctx.response.defer()

        if 'VIP Trainer' in str(ctx.author.roles):

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
            parameter: Option(str, "Enter HexColour for the Role", required=True)):
        await ctx.response.defer()

        parameter = parameter.replace('#', '').replace('0x', '')
        parameter = "0x" + parameter



        if 'VIP Trainer' in str(ctx.author.roles):

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
    async def icon(self,
            ctx,
            parameter: Option(str, "Enter an Emoji", required=True)):

        await ctx.response.defer()
        eparameter = parameter
        parameter = parameter.split(':')[-1].replace('>','')

        main_file_content = read_file()

        if 'VIP Trainer' in str(ctx.author.roles):
            if str(ctx.author.id) in main_file_content:
                try:
                    emoji = discord.utils.get(ctx.guild.emojis, id=int(parameter))
                    url = emoji.url
                    already_content = main_file_content[str(ctx.author.id)]

                    response = requests.get(url)
                    data = response.content

                    iconurl = data
                    url = data

                    already_content['emoji'] = url

                    rlid = already_content['roleid']
                    await ctx.guild.get_role(int(rlid)).edit(icon=(iconurl))

                    main_file_content[str(ctx.author.id)] = already_content
                    write_file(main_file_content)

                    embed = discord.Embed(description=f"Role Icon Updated to {eparameter}", color=0x2E3136)
                    await ctx.respond(embed=embed)

                except Exception as e:
                    print(e)
                    embed = discord.Embed(
                        title="Icon Set Successfully :white_check_mark:", color=0x2E3136)
                    embed.set_footer(text=f"Send a message in any channel to test your role icon. \n\nIf you're unable to see your role icon, make sure you've used the command correctly and the emoji belongs to this server")
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
