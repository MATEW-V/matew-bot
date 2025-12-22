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
    print(f"live and ready: {bot.user.name}")
    
@bot.event
async def on_message(message): #any message response here
    if message.author==bot.user:
        return
    if "67" in message.content.lower(): #SIX SEVENN
        await message.channel.send(f"{message.author.mention} - SIXXX SEEVENNNNN")
    await bot.process_commands(message)

#STUDYWATCH FEATURE + LOGGING
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "studywatch.json")

def save_session(seconds):
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

def get_filtered_stats(timeframe):
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    now = datetime.now().date()
    filtered_data = {}
    total_seconds = 0
    
    # Sort dates for average calculation and graphing
    sorted_all_dates = sorted(data.keys())
    if not sorted_all_dates:
        return None

    for date_str, sessions in data.items():
        day_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_total = sum(sessions)
        delta = (now - day_date).days

        if timeframe == "week" and delta <= 7:
            filtered_data[date_str] = day_total
            total_seconds += day_total
        elif timeframe == "month" and delta <= 30:
            filtered_data[date_str] = day_total
            total_seconds += day_total
        elif timeframe == "6month" and delta <= 180:
            filtered_data[date_str] = day_total
            total_seconds += day_total
        elif timeframe == "all":
            filtered_data[date_str] = day_total
            total_seconds += day_total

    return total_seconds, filtered_data, sorted_all_dates

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
    start_time = time.time()
    view = StudyView()
    
    embed = discord.Embed(
        title="📖 Study Session Active",
        description="Time Elapsed: `00:00:00`",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed, view=view)

    # The Loop
    while view.status == "running":
        await asyncio.sleep(5) # Shorter sleep for better responsiveness
        elapsed = int(time.time() - start_time)
        h, r = divmod(elapsed, 3600)
        m, s = divmod(r, 60)
        
        embed.description = f"Current Session: `{h:02}:{m:02}:{s:02}`"
        try:
            # We pass view=view here to keep the buttons active during updates
            await message.edit(embed=embed, view=view)
        except discord.NotFound:
            view.status = "cancelled"
            break

    final_seconds = int(time.time() - start_time)
    
    if view.status == "stopped":
        save_session(final_seconds)
        h, r = divmod(final_seconds, 3600)
        m, s = divmod(r, 60)
        
        embed.title = "✅ Session Ended & Saved"
        embed.color = discord.Color.green()
        embed.description = f"Total Time: **{h}h {m}m {s}s**\n*Saved to your history.*"
    else:
        embed.title = "🚫 Session Cancelled"
        embed.color = discord.Color.red()
        embed.description = "This session was discarded."

    # This line is crucial: view=None REMOVES the buttons from Discord
    await message.edit(embed=embed, view=None)

class StatsView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx

    def build_embed(self, timeframe):
        """Helper to create the embed with Current and Record streaks."""
        result = get_filtered_stats(timeframe)
        if not result:
            return discord.Embed(description="No data found for this period.", color=discord.Color.red())
        
        total_seconds, filtered_data, all_dates = result
        now = datetime.now().date()
        
        #logic for Current and Record Streaks usign all dates sorted (ts a leetcode problem)
        full_date_list = sorted({datetime.strptime(d, "%Y-%m-%d").date() for d in all_dates})
        
        current_streak = 0
        record_streak = 0
        temp_streak = 0
        
        # Calculate Record Streak (Longest gap-less sequence)
        if full_date_list:
            temp_streak = 1
            record_streak = 1
            for i in range(1, len(full_date_list)):
                # Check if the current date is exactly 1 day after the previous date
                if (full_date_list[i] - full_date_list[i-1]).days == 1:
                    temp_streak += 1
                else:
                    temp_streak = 1
                
                if temp_streak > record_streak:
                    record_streak = temp_streak

            # Calculate Current Streak
            check_date = now
            # Grace period: if you haven't studied today, check if yesterday's streak is still alive
            if now not in full_date_list:
                check_date -= timedelta(days=1)
            
            while check_date in full_date_list:
                current_streak += 1
                check_date -= timedelta(days=1)

        # graphing logic in a relative scale
        graph_lines = []
        sorted_keys = sorted(filtered_data.keys())
        display_dates = sorted_keys[-15:] if timeframe == "all" else sorted_keys
        
        if filtered_data:
            max_val = max(filtered_data.values()) if filtered_data.values() else 1
            for d_str in display_dates:
                seconds = filtered_data[d_str]
                temp_date = datetime.strptime(d_str, "%Y-%m-%d")
                clean_date = temp_date.strftime("%b %d, '%y")
                bar_len = max(1, int((seconds / max_val) * 12)) if seconds > 0 else 0
                bar = "█" * bar_len
                graph_lines.append(f"{clean_date} | {bar} {seconds/3600:.1f}h")
        
        graph_text = "```\n" + ("\n".join(graph_lines) if graph_lines else "No data logged.") + "\n```"

        # 3. Dynamic Daily Average
        range_start = datetime.strptime(sorted_keys[0], "%Y-%m-%d").date() if sorted_keys else now
        days_in_range = (now - range_start).days + 1
        avg_seconds = total_seconds / days_in_range

        # 4. Embed Construction
        title_map = {"week": "Weekly", "month": "Monthly", "6month": "6-Month", "all": "All-Time"}
        embed = discord.Embed(title=f"📈 {title_map.get(timeframe, 'Study')} Stats", color=discord.Color.gold())
        
        def format_time(s):
            h, r = divmod(int(s), 3600); m, _ = divmod(r, 60)
            return f"{h}h {m}m"

        embed.add_field(name="Total Time", value=f"**{format_time(total_seconds)}**", inline=True)
        embed.add_field(name="Daily Average", value=f"**{format_time(avg_seconds)}**", inline=True)
        
        # Streak Row
        embed.add_field(name="Current Streak", value=f"🔥 **{current_streak} Days**", inline=True)
        embed.add_field(name="Record Streak", value=f"🏆 **{record_streak} Days**", inline=True)
        
        embed.add_field(name="Timeline", value=graph_text, inline=False)
        return embed

    #buttons
    async def handle_update(self, interaction, timeframe):
        embed = self.build_embed(timeframe)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="7 Days", style=discord.ButtonStyle.blurple)
    async def week_btn(self, interaction, button):
        await self.handle_update(interaction, "week")

    @discord.ui.button(label="30 Days", style=discord.ButtonStyle.blurple)
    async def month_btn(self, interaction, button):
        await self.handle_update(interaction, "month")

    @discord.ui.button(label="6 Months", style=discord.ButtonStyle.blurple)
    async def sixmonth_btn(self, interaction, button):
        await self.handle_update(interaction, "6month")

    @discord.ui.button(label="All Time", style=discord.ButtonStyle.grey)
    async def all_btn(self, interaction, button):
        await self.handle_update(interaction, "all")
        
@bot.command()
async def stats(ctx):
    if not os.path.exists(DATA_FILE):
        return await ctx.send("❌ No study data found yet. Start your first session with `!studywatch`!")

    view = StatsView(ctx)
    initial_embed = view.build_embed("all")
    
    await ctx.send(embed=initial_embed, view=view)
    

bot.run(token, log_handler=handler, log_level=logging.DEBUG)