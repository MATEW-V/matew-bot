import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import time
import asyncio
import json
from datetime import datetime, timedelta

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log',encoding='utf-8',mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!',intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go ,{bot.user.name}")
    
@bot.event
async def on_message(message): #any message response here
    if message.author==bot.user:
        return
    if "67" in message.content.lower(): #SIX SEVENN
        await message.channel.send(f"{message.author.mention} - SIXXX SEEVENNNNN")
    await bot.process_commands(message)

#STUDYWATCH FEATURE + LOGGING
DATA_FILE = "studywatch.json" 
def save_session(seconds):
    """Saves a single session duration to the daily list."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    today = str(datetime.now().date())
    if today not in data:
        data[today] = []
    
    data[today].append(seconds)
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
def get_stats_data():
    """Calculates all-time, monthly, and weekly totals."""
    if not os.path.exists(DATA_FILE):
        return 0, 0, 0, {}

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    now = datetime.now().date()
    all_time = 0
    past_week = 0
    past_month = 0
    weekly_dict = {}

    for date_str, sessions in data.items():
        day_total = sum(sessions)
        day_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        all_time += day_total
        
        if now - day_date <= timedelta(days=7):
            past_week += day_total
            weekly_dict[date_str] = day_total
            
        if now - day_date <= timedelta(days=30):
            past_month += day_total

    return all_time, past_week, past_month, weekly_dict

class StudyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.status = "running"

    @discord.ui.button(label="Stop & Save", style=discord.ButtonStyle.green, emoji="💾")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.status = "stopped"
        await interaction.response.send_message("Finishing and saving session...", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.status = "cancelled"
        await interaction.response.send_message("Session discarded.", ephemeral=True)
        self.stop()
        
@bot.command()
async def studywatch(ctx):
    """Starts a live-updating stopwatch with Stop/Cancel options."""
    start_time = time.time()
    view = StudyView()
    
    embed = discord.Embed(
        title="📖 Study Session Active",
        description="Time Elapsed: `00:00:00`",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed, view=view)

    while view.status == "running":
        elapsed = int(time.time() - start_time)
        h, r = divmod(elapsed, 3600)
        m, s = divmod(r, 60)
        
        embed.description = f"Current Session: `{h:02}:{m:02}:{s:02}`"
        try:
            await message.edit(embed=embed)
        except discord.NotFound:
            view.status = "cancelled"
            break
        
        await asyncio.sleep(10) # Refresh rate

    final_seconds = int(time.time() - start_time)
    
    if view.status == "stopped":
        save_session(final_seconds)
        h, r = divmod(final_seconds, 3600)
        m, s = divmod(r, 60)
        embed.title = "✅ Session Saved"
        embed.color = discord.Color.green()
        embed.description = f"Added **{h}h {m}m {s}s** to your daily logs."
    else:
        embed.title = "🚫 Session Cancelled"
        embed.color = discord.Color.red()
        embed.description = "This session was not recorded."

    await message.edit(embed=embed, view=None)

@bot.command()
async def swstats(ctx):
    """Displays a personal dashboard with a text-based bar graph."""
    all_t, week_t, month_t, daily_dict = get_stats_data()

    def format_time(seconds):
        h, r = divmod(seconds, 3600)
        m, _ = divmod(r, 60)
        return f"{int(h)}h {int(m)}m"

    # Generate Text Graph
    if not daily_dict:
        graph = "No data recorded in the last 7 days."
    else:
        graph_lines = []
        max_val = max(daily_dict.values()) if daily_dict.values() else 1
        for d_str in sorted(daily_dict.keys()):
            bar_len = int((daily_dict[d_str] / max_val) * 10)
            bar = "█" * bar_len
            hours = daily_dict[d_str] / 3600
            graph_lines.append(f"{d_str[5:]} | {bar} {hours:.1f}h")
        graph = "```\n" + "\n".join(graph_lines) + "\n```"

    embed = discord.Embed(title=f"📈 {ctx.author.display_name}'s Study Stats", color=discord.Color.gold())
    embed.add_field(name="Total", value=format_time(all_t), inline=True)
    embed.add_field(name="30 Days", value=format_time(month_t), inline=True)
    embed.add_field(name="7 Days", value=format_time(week_t), inline=True)
    embed.add_field(name="Weekly Progress", value=graph, inline=False)

    await ctx.send(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)