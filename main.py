from matplotlib import pyplot as plt
from discord.ext import commands
import datetime
import discord
import asyncio
import json
import time
import ast
import os


client = commands.AutoShardedBot(command_prefix=commands.when_mentioned_or("--"), help_command=None)
client.launch_time = datetime.datetime.utcnow()
botversion = "V1"
cnt = 0


@client.event
async def on_ready():
    global cnt
    print("Bot started as {0.user}".format(client))
    client.loop.create_task(game())
    while True:
        await pic_deleter()
        await not_existing_deleter()
        await updater()
        print(f"Updated {cnt} messages")
        cnt = 0
        await asyncio.sleep(60)


@client.event
async def on_guild_join(guild):
    nightslide = await client.fetch_user(264804347689304065)
    wow = client.guilds
    wau = wow[-1]
    membercount = guild.member_count
    region = guild.region
    embed = discord.Embed(
        title=" "
    )
    embed.add_field(name="Joined Server", value="**Name: **" + str(wau) + "\n" + "**Members: **" + str(membercount) + "\n" + "**Region: **" + str(region) + "\n")
    await nightslide.send(embed=embed)


async def updater():
    global cnt
    for file in os.listdir("/var/www/html/cdn/pcs"):
        pc_id = file.strip(".txt")
        with open("data.json", "r+") as f:
            j = json.load(f)
            try:
                channel = client.get_channel(j[pc_id]["channel_id"])
                msg = await channel.fetch_message(j[pc_id]["message_id"])
            except:
                continue
            current_time = round(time.time())
            last_updated_unix = await fetch_data(pc_id, "last_updated")
            if abs(current_time - last_updated_unix) >= 300:
                await exception_updater_not_running(msg)
                continue
            cpu_usage = await fetch_data(pc_id, 'cpu_usage')
            ram_usage = await fetch_data(pc_id, 'ram_usage')
            if int(cpu_usage) == 0 and int(ram_usage) == 0:
                await exception_no_data_received(msg)
                continue
            await create_network_graph(pc_id, current_time)
            embed = discord.Embed(
                title="Your Information"
            )
            embed.add_field(name=f"{emote_cpu}Avg. CPU usage", inline=True, value=f"{cpu_usage}%")
            embed.add_field(name=f"{emote_ram}Curr. RAM usage", inline=True, value=f"{ram_usage}%")
            embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote", icon_url="https://legende.cc/pfp.gif")
            embed.set_image(url=f"https://legende.cc/cdn/pcs/{pc_id}/network_graph{current_time}.png")
            await msg.edit(embed=embed)
            cnt += 1
            continue


async def exception_updater_not_running(msg):
    embed = discord.Embed(
        title="",
        color=0xec0e0e
    )
    embed.add_field(name=f"Error", inline=True,
                    value="Your Server is either down or the updater isn't running. If everything seems alright, check your internet connection.\n"
                          "You can download the updater [here](https://legende.cc/servermonitor.zip)\n"
                          "Still doesn't work? Join the [Support Server](https://discord.gg/D7sakzPyrk)\n"
                          "Find a tutorial [here](https://youtu.be/xo9DdeYm3Sk)")
    embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                     icon_url="https://legende.cc/pfp.gif")
    try:
        await msg.edit(embed=embed)
    except:
        pass


async def exception_no_data_received(msg):
    embed = discord.Embed(
        title="",
        color=0xec0e0e
    )
    embed.add_field(name=f"Error", inline=True,
                    value="Your data isn't on our server yet, please make sure the updater is running correctly.\n"
                          "You can download the updater [here](https://legende.cc/servermonitor.zip)\n"
                          "Find a tutorial [here](https://youtu.be/xo9DdeYm3Sk)")
    embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                     icon_url="https://legende.cc/pfp.gif")
    await msg.edit(embed=embed)


async def fetch_data(pc_id, data):
    with open("data.json") as file:
        j = json.load(file)
        return j[str(pc_id)][data]


async def pic_deleter():
    current_time = int(datetime.datetime.now().strftime("%M"))
    file_names = []
    for pc_id in os.listdir("/var/www/html/cdn/pcs"):
        for file_name in os.listdir(f"/var/www/html/cdn/pcs/{pc_id}"):
            if "network_graph" and ".png" in file_name:
                file_name = file_name.strip("network_graph")
                file_name = file_name.strip(".png")
                file_names.append(int(file_name))
                for i in file_names:
                    if abs(current_time - i) <= 300:
                        pass
                    else:
                        try:
                            os.remove(f"/var/www/html/cdn/pcs/{pc_id}/network_graph{i}.png")
                        except:
                            pass


async def not_existing_deleter():
    with open("data.json", "r+") as f:
        to_delete = []
        j = json.load(f)
        for pc_id in j:
            try:
                channel = client.get_channel(j[pc_id]["channel_id"])
                await channel.fetch_message(j[pc_id]["message_id"])
                continue
            except:
                to_delete.append(pc_id)
        for pc_id in to_delete:
            os.system(f"rm -r /var/www/html/cdn/pcs/{pc_id}")
            j.pop(str(pc_id))
            print("deleted" + pc_id)
        f.seek(0)
        f.truncate(0)
        json.dump(j, f, indent=4)


def emote(emotename, emoteid):
    return f"<:{emotename}:{emoteid}>"


emote_cpu = emote("cpu", 911638273166827560)
emote_ram = emote("ram", 911637963568472155)


async def create_network_graph(pc_id, time):
    try:
        with open(f"/var/www/html/cdn/pcs/{pc_id}/network_graph_data.txt") as file:
            f = file.read()
            f = ast.literal_eval(f)
            new_list = []
            for i in f:
                new_list.append(float(i))
            plt.plot(new_list)
            plt.xlabel("Time in seconds", color="white")
            plt.ylabel("Traffic in MBit/s", color="white")
            plt.tick_params(axis="x", colors="white")
            plt.tick_params(axis="y", colors="white")
            plt.title("Traffic of last 30 seconds", color="white")
            curr_time = datetime.datetime.now().strftime("%H:%M")
            ax = plt.gca()
            ax.text(0.95, -0.1, f'Last updated {curr_time} MEZ',
                    horizontalalignment='center',
                    verticalalignment='top',
                    transform=ax.transAxes,
                    color="white")
            plt.savefig(f"/var/www/html/cdn/pcs/{pc_id}/network_graph{time}.png", transparent=True)
            plt.clf()
    except FileNotFoundError:
        pass


@client.command()
async def setup(ctx, pc_id=None):
    if not pc_id:
        await pc_id_not_provided(ctx)
    else:
        embed = discord.Embed(
            title=""
        )
        embed.add_field(name="Your Information", inline=True, value="This message will be updated after the first update got posted by your updater.\n"
                                                                    "Find a tutorial [here](https://youtu.be/xo9DdeYm3Sk)")
        embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                         icon_url="https://legende.cc/pfp.gif")
        sent_message = await ctx.send(embed=embed)
        with open("data.json", "r") as json_file:
            json_decoded = json.load(json_file)
            json_decoded[pc_id] = {
                "cpu_usage": 0,
                "ram_usage": 0,
                "last_updated": 0,
                "message_id": 0,
                "guild_id": 0,
                "channel_id": 0
            }
        with open("data.json", 'w') as json_file:
            json.dump(json_decoded, json_file, indent=4)
        with open("data.json", "r+") as file:
            j = json.load(file)
            j[str(pc_id)]["message_id"] = sent_message.id
            j[str(pc_id)]["channel_id"] = sent_message.channel.id
            j[str(pc_id)]["guild_id"] = sent_message.guild.id
            file.seek(0)
            file.truncate(0)
            json.dump(j, file, indent=4)
        try:
            os.makedirs(f"/var/www/html/cdn/pcs/{pc_id}")
        except FileExistsError:
            embed = discord.Embed(
                title="",
                colour=0xec0e0e
            )
            embed.add_field(name="Error", inline=True, value="This PC-ID was already added. The old message(if still exists) won't be updated anymore.")
            embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                             icon_url="https://legende.cc/pfp.gif")
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(10)
            await msg.delete()


async def pc_id_not_provided(ctx):
    embed = discord.Embed(
        title="",
        color=0xec0e0e
    )
    embed.add_field(name="Error", inline=True,
                    value="Please provide your Computer-ID, given to you by the updater.\n"
                          "Don't have the updater? Download it [here](https://legende.cc/servermonitor.zip)\n"
                          "Find a tutorial [here](https://youtu.be/xo9DdeYm3Sk)")
    embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                     icon_url="https://legende.cc/pfp.gif")
    await ctx.send(embed=embed)


@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="ServerMonitor Help",
        colour=3066993
    )
    embed.add_field(name="Basic Information", inline=False, value="This bot allows you to get recent information of a server or pc. To get more information on how it works, check down below.\n \n")
    embed.add_field(name="Commands", inline=False,
                    value="*--setup [PC-ID]* - Set's up a message, which updates itself every 2 minutes. Example: --setup 92406901310\n"
                          "*--contact* - Will give you contact information to the bot owner \n"
                          "*--upvote* - If you want to support me :) \n"
                          "*--botinfo* - Gives you information about the bot connectivity etc. \n"
                          "**Here is a [video tutorial](https://youtu.be/xo9DdeYm3Sk) on how to set it up.** \n"
                          "You can download the updater(client, which runs on your server) [here](https://legende.cc/servermonitor.zip)\n\n"
                          "Click [here](https://discord.gg/D7sakzPyrk) for ServerMonitor's support discord server.\n"
                          "If you want the Bot on your own server: [Click here!](https://discord.com/api/oauth2/authorize?client_id=507569557326790656&permissions=8&scope=bot)")
    await ctx.send(embed=embed)


async def game():
    while True:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="--help"))
        await asyncio.sleep(60)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                               name=str(len(client.guilds)) + " Servers | --help"))
        await asyncio.sleep(60)
        await client.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name="--invite | --help"))
        await asyncio.sleep(60)


@client.command()
async def invite(ctx):
    embed = discord.Embed(
        title=" "
    )
    embed.add_field(name="Invite",
                    value="Click [here](https://discord.com/api/oauth2/authorize?client_id=507569557326790656&permissions=8&scope=bot) to invite the bot to your server")
    embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                     icon_url="https://legende.cc/pfp.gif")
    await ctx.send(embed=embed)


@client.command()
async def upvote(ctx):
    embed = discord.Embed(
        title=" ",
        colour=3066993
    )
    embed.add_field(name="Upvote",
                    value="Consider upvoting if you enjoy this bot :) For more information [Click here!](https://top.gg/bot/507569557326790656)")
    embed.set_footer(text="Made by Nightslide#4160",
                     icon_url="https://legende.cc/pfp.gif")
    await ctx.send(embed=embed)


@client.command()
async def botinfo(ctx):
    embed = discord.Embed(
        title="Bot Stats"
    )
    delta_uptime = datetime.datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed.add_field(name="Joined servers: ", value=str(len(client.guilds)), inline=True)
    embed.add_field(name="Created at: ", value="31.01.2022", inline=True)
    embed.add_field(name="Bot ping: ", value=str(round(client.latency * 100, 1)) + " ms", inline=True)
    embed.add_field(name="Discord.py Version: ", value="V " + str(discord.__version__), inline=True)
    embed.add_field(name="Uptime: ", value=f"{days}d, {hours}h, {minutes}m, {seconds}s", inline=True)
    embed.add_field(name="OS: ", value="Linux", inline=True)
    embed.add_field(name="Bot Version: ", value=botversion)
    embed.add_field(name="Invite: ",
                    value="If you want to invite the Bot: [Click here!](https://discord.com/api/oauth2/authorize?client_id=507569557326790656&permissions=8&scope=bot)",
                    inline=True)
    embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote",
                     icon_url="https://legende.cc/pfp.gif")
    await ctx.send(embed=embed)


@client.command()
async def contact(ctx):
    embed = discord.Embed(
        title=" ",
    )
    embed.add_field(name="Contact", value="You can join [my server](https://discord.gg/D7sakzPyrk) or add me on discord (Nightslide#4160).")
    embed.set_footer(text="Made by Nightslide#4160. Support me by using --upvote", icon_url="https://legende.cc/pfp.gif")
    await ctx.send(embed=embed)


@client.command()
async def bigcook(ctx):
    await ctx.bot.logout()


client.run("TOKEN HERE")

