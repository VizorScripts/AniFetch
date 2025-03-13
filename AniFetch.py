import json
import discord
import logging
import os
import sys
import requests
import asyncio
import time
from datetime import datetime, timedelta
from dateutil import tz
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import app_commands

# ==================== INITIALIZATION ====================
def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('anifetch-debug.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    if sys.platform == 'win32':
        logging.getLogger().handlers[1].stream = sys.stdout

configure_logging()
logger = logging.getLogger('AniFetch')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_CHANNEL = int(os.getenv('COMMAND_CHANNEL'))
DUB_FEED_CHANNEL = int(os.getenv('DUB_FEED_CHANNEL'))
SUB_FEED_CHANNEL = int(os.getenv('SUB_FEED_CHANNEL'))
HENTAI_CHANNEL = os.getenv('HENTAI_CHANNEL', None)
EXCLUDE_HENTAI = os.getenv('EXCLUDE_HENTAI', 'True').lower() == 'true'
TIMEZONE = os.getenv('TIMEZONE', 'UTC')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'anime-schedule.p.rapidapi.com')

if HENTAI_CHANNEL:
    try:
        HENTAI_CHANNEL = int(HENTAI_CHANNEL)
    except ValueError:
        logger.error("Invalid HENTAI_CHANNEL format, disabling hentai features")
        HENTAI_CHANNEL = None
        EXCLUDE_HENTAI = True

# ==================== DATA MANAGEMENT ====================
class DataManager:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.schedules = {'dub': [], 'sub': [], 'hentai': [], 'rapidapi': []}
            cls._instance.feeds = {'dub': [], 'sub': [], 'hentai': [], 'rapidapi': []}
        return cls._instance

DATA_SOURCES = {
    'schedules': {
        'dub': 'https://raw.githubusercontent.com/RockinChaos/AniSchedule/master/raw/dub-schedule.json',
        'sub': 'https://raw.githubusercontent.com/RockinChaos/AniSchedule/master/raw/sub-schedule.json',
        'hentai': 'https://raw.githubusercontent.com/RockinChaos/AniSchedule/master/raw/hentai-episode-feed.json',
        'rapidapi': [
            f'https://{RAPIDAPI_HOST}/dub-schedule',
            f'https://{RAPIDAPI_HOST}/sub-schedule'
        ]
    },
    'feeds': {
        'dub': 'https://raw.githubusercontent.com/RockinChaos/AniSchedule/master/raw/dub-episode-feed.json',
        'sub': 'https://raw.githubusercontent.com/RockinChaos/AniSchedule/master/raw/sub-episode-feed.json',
        'hentai': 'https://raw.githubusercontent.com/RockinChaos/AniSchedule/master/raw/hentai-episode-feed.json'
    }
}

# ==================== BOT CONFIGURATION ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ==================== CORE FUNCTIONALITY ====================
def format_date(timestamp: [int, str]) -> str:
    try:
        if isinstance(timestamp, str):
            timestamp = int(datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp())
        dt = datetime.fromtimestamp(timestamp, tz.gettz(TIMEZONE))
        day = dt.strftime("%d").lstrip('0')
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(int(day), 'th')
        return dt.strftime(f"%b {day}{suffix} '%y {dt.hour % 12 or 12}:%M%p {dt.strftime('%Z')}")
    except Exception as e:
        logger.error(f"Date error: {str(e)}")
        return "Invalid Date"

# ==================== IMPROVED TITLE HANDLING ====================
def extract_titles(entry: dict) -> tuple:
    try:
        # Handle RapidAPI format
        if entry.get('source') == 'rapidapi':
            media = entry.get('media', {})
            title_data = media.get('title', {}) or media.get('english') or entry.get('title', {})
            cover_url = media.get('coverImage', {}).get('extraLarge')
        else:
            media = entry.get('media', {}).get('media', entry.get('media', {}))
            title_data = media.get('title', {}) or media.get('english') or entry.get('title', {})
            cover_url = (
                media.get('coverImage', {}).get('extraLarge')
                or media.get('coverImage', {}).get('large')
                or entry.get('coverImage', {}).get('extraLarge')
            )

        if isinstance(title_data, dict):
            english = title_data.get('english') or title_data.get('userPreferred')
            native = title_data.get('native') or title_data.get('romaji')
            romaji = title_data.get('romaji') or title_data.get('userPreferred')
        elif isinstance(title_data, str):
            english = native = romaji = title_data
        else:
            english = native = romaji = None

        # Enhanced MAL ID detection
        mal_id = entry.get('idMal') or media.get('idMal') or entry.get('media', {}).get('idMal')
        if not cover_url and mal_id:
            cover_url = f"https://cdn.myanimelist.net/images/anime/{mal_id}.jpg"

        if not english or english in ['', 'Untitled']:
            entry_id = str(media.get('id') or entry.get('id') or entry.get('idMal') or 'Unknown')
            return (f"Title Not Found (ID: {entry_id})", "", "", cover_url)

        return (
            english.strip(),
            native.strip() if native else english.strip(),
            romaji.strip() if romaji else english.strip(),
            cover_url
        )
        
    except Exception as e:
        logger.error(f"Title error: {str(e)}")
        return ('Title Extraction Failed', '', '', None)

# ==================== UNIFIED EMBED GENERATOR ====================
async def create_perfect_embed(entry: dict, entry_type: str) -> discord.Embed:
    try:
        english, _, _, cover_url = extract_titles(entry)
        if "title not found" in english.lower() or not english.strip():
            return None

        entry_type = entry_type.lower()
        future_episodes = []
        
        # Handle RapidAPI format
        if entry.get('source') == 'rapidapi':
            episodes = entry.get('episodes', [])
            for ep in episodes:
                try:
                    airing_at = ep.get('airing_at')
                    if isinstance(airing_at, str):
                        airing_at = datetime.fromisoformat(airing_at.replace('Z', '+00:00')).timestamp()
                    if airing_at and airing_at > time.time():
                        future_episodes.append({
                            'number': ep.get('episode'),
                            'time': airing_at
                        })
                except Exception as e:
                    logger.debug(f"RapidAPI episode error: {str(e)}")
        else:
            media = entry.get('media', {}).get('media', {}) or entry.get('media', {})
            schedule_nodes = media.get('airingSchedule', {}).get('nodes', []) or entry.get('airingSchedule', {}).get('nodes', [])
            for ep in schedule_nodes:
                try:
                    ep_number = ep.get('episode', ep.get('episodeNumber', 0))
                    airing_at = ep.get('airingAt', 0)
                    if isinstance(airing_at, str):
                        airing_at = datetime.fromisoformat(airing_at.replace('Z', '+00:00')).timestamp()
                    if airing_at and airing_at > time.time():
                        future_episodes.append({
                            'number': ep_number,
                            'time': airing_at
                        })
                except Exception as e:
                    logger.debug(f"Episode error: {str(e)}")

        description_lines = [f"**{english}**"]
        for ep in sorted(future_episodes, key=lambda x: x['number']):
            air_time = format_date(ep['time'])
            description_lines.append(f"Airing Ep {ep['number']} {entry_type.title()}bed -> **{air_time}**")

        if not description_lines:
            return None

        embed = discord.Embed(
            title="🎬",
            description="\n".join(description_lines),
            color=0x3498db if entry_type == 'dub' else 0xe74c3c
        )

        if cover_url:
            embed.set_thumbnail(url=cover_url)
            logger.debug(f"Set thumbnail for {english}: {cover_url}")
        else:
            logger.warning(f"No cover image for: {english} (ID: {entry.get('id')})")
            logger.debug(f"Entry structure: {json.dumps(entry, indent=2)}")

        return embed

    except Exception as e:
        logger.error(f"Embed failed: {str(e)}", exc_info=True)
        return None

# ==================== COMMAND HANDLERS ====================
async def handle_search(interaction: discord.Interaction, search_type: str, query: str):
    await interaction.response.defer()
    data = DataManager()
    results = []
    clean_query = query.strip().lower()
    
    combined_entries = data.schedules[search_type] + data.feeds[search_type] + data.feeds['rapidapi']
    
    for entry in combined_entries:
        try:
            english_title, native_title, romaji_title, _ = extract_titles(entry)
            if not english_title or "title not found" in english_title.lower():
                continue

            titles = [
                str(english_title).lower(),
                str(native_title).lower(),
                str(romaji_title).lower(),
                str(entry.get('id', '')),
                str(entry.get('idMal', '')),
                str(entry.get('media', {}).get('media', {}).get('title', '')).lower()
            ]
            if any(clean_query in title for title in titles if title):
                results.append(entry)
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
    
    if not results:
        return await interaction.followup.send(f"No results found", ephemeral=True)
    
    channel = bot.get_channel(COMMAND_CHANNEL)
    if channel:
        for entry in results[:5]:
            if embed := await create_perfect_embed(entry, search_type):
                await channel.send(embed=embed)
                await asyncio.sleep(0.5)
    
    await interaction.followup.send(f"Found {len(results)} {search_type} results", ephemeral=True)

@bot.tree.command(name="dub", description="Search dubbed anime")
@app_commands.describe(query="Search query")
async def dub_search(interaction: discord.Interaction, query: str):
    await handle_search(interaction, 'dub', query)

@bot.tree.command(name="sub", description="Search subbed anime")
@app_commands.describe(query="Search query")
async def sub_search(interaction: discord.Interaction, query: str):
    await handle_search(interaction, 'sub', query)

@bot.tree.command(name="hent", description="Search hentai episodes")
@app_commands.describe(query="Search query")
async def hent_search(interaction: discord.Interaction, query: str):
    if EXCLUDE_HENTAI or not HENTAI_CHANNEL:
        return await interaction.response.send_message("Hentai features are disabled", ephemeral=True)
    await handle_search(interaction, 'hentai', query)

# ==================== ENTRY VALIDATION ====================
def is_valid_entry(entry: dict) -> bool:
    english, _, _, _ = extract_titles(entry)
    entry_id = str(entry.get('id') or entry.get('_id') or entry.get('idMal') or '')
    
    if not entry_id.isdigit():
        return False
    
    return all([
        "title not found" not in english.lower(),
        "untitled" not in english.lower(),
        len(english) > 3,
        any(c.isalpha() for c in english),
        entry.get('episodes') or entry.get('airingSchedule')
    ])

# ==================== BACKGROUND TASKS ====================
@tasks.loop(minutes=15)
async def refresh_data():
    logger.info("Refreshing data...")
    data = DataManager()
    
    try:
        # Refresh RapidAPI data
        for url in DATA_SOURCES['schedules']['rapidapi']:
            try:
                feed_data = await fetch_data(url)
                if feed_data:
                    media_type = 'dub' if 'dub' in url else 'sub'
                    existing_ids = {str(e['id']) for e in data.feeds['rapidapi']}
                    new_entries = [e for e in feed_data if str(e.get('id')) not in existing_ids]
                    
                    for entry in new_entries:
                        entry['source'] = 'rapidapi'
                    
                    data.feeds['rapidapi'].extend(new_entries)
                    logger.info(f"Added {len(new_entries)} RapidAPI {media_type} entries")
            except Exception as e:
                logger.error(f"RapidAPI refresh failed: {str(e)}")

        # Refresh other sources
        for media_type in ['dub', 'sub', 'hentai']:
            if media_type == 'hentai' and (EXCLUDE_HENTAI or not HENTAI_CHANNEL):
                continue

            schedule_url = DATA_SOURCES['schedules'][media_type]
            if schedule_data := await fetch_data(schedule_url):
                data.schedules[media_type] = schedule_data

            feed_url = DATA_SOURCES['feeds'][media_type]
            if feed_data := await fetch_data(feed_url):
                existing_ids = {
                    'dub': {str(e['id']) for e in data.feeds['dub']},
                    'sub': {str(e['id']) for e in data.feeds['sub']},
                    'hentai': {str(e.get('id', e.get('_id'))) for e in data.feeds['hentai']}
                }
                
                new_entries = [
                    e for e in feed_data
                    if str(e.get('id', e.get('_id', ''))) not in existing_ids[media_type]
                ]
                valid_entries = [e for e in new_entries if is_valid_entry(e)]
                
                if valid_entries and (channel := bot.get_channel({
                    'dub': DUB_FEED_CHANNEL,
                    'sub': SUB_FEED_CHANNEL,
                    'hentai': HENTAI_CHANNEL
                }[media_type])):
                    valid_count = 0
                    for entry in valid_entries:
                        if embed := await create_perfect_embed(entry, media_type):
                            await channel.send(embed=embed)
                            valid_count += 1
                            await asyncio.sleep(1)
                    logger.info(f"Posted {valid_count} valid {media_type} entries")
                    data.feeds[media_type].extend(valid_entries)
    except Exception as e:
        logger.error(f"Refresh failed: {str(e)}")
        refresh_data.restart()

# ==================== UTILITIES ====================
async def fetch_data(url: str) -> list:
    try:
        headers = {}
        if 'rapidapi' in url:
            headers = {
                'X-RapidAPI-Key': RAPIDAPI_KEY,
                'X-RapidAPI-Host': RAPIDAPI_HOST
            }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json() if isinstance(response.json(), list) else []
    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return []

# ==================== BOT SETUP ====================
@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    try:
        await bot.tree.sync()
        logger.info("Commands synced")
        refresh_data.start()
    except Exception as e:
        logger.error(f"Start error: {str(e)}")

if __name__ == '__main__':
    required_vars = ['DISCORD_TOKEN', 'COMMAND_CHANNEL', 'DUB_FEED_CHANNEL', 'SUB_FEED_CHANNEL']
    if missing := [var for var in required_vars if not os.getenv(var)]:
        logger.critical(f"Missing required variables: {', '.join(missing)}")
        sys.exit(1)
        
    bot.run(TOKEN)