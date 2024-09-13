#133451761522-h0lf3pchn4job63osticc976qlrik2cj.apps.googleusercontent.com

import discord
from discord.ext import tasks, commands
import datetime
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz
import os
import ChurchBot.webserver as webserver

# Add your previous Google Calendar API integration here (as explained above)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import datetime
from googleapiclient.discovery import build

# Scopes to access Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_google_calendar_events():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret_133451761522-378d1k1uk5acs3pigp4fmh5sh38qjn2f.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API to fetch upcoming events
    now = datetime.datetime.now(ZoneInfo('America/New_York')).isoformat()
    events_result = service.events().list(calendarId='pastor@washingtonipc.org', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"Event: {event['summary']}, Start Time: {start}")
        return events

###################################################################################################################################################

# Call the function to retrieve events
get_google_calendar_events()

# Create the bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents = intents)

# Specify your Discord channel ID
discord_channel_id = 689970151764000769
DISCORD_TOKEN = os.enviorn('discordkey')

@tasks.loop(minutes=60)  # Check every hour
async def announce_events():
    channel = bot.get_channel(discord_channel_id)
    
    # Get upcoming events from Google Calendar
    events = get_google_calendar_events()

    # Get the current date
    today = datetime.date.today()
    
    # Loop through events and announce any that match today's date
    for event in events:
        start_date = event['start'].get('dateTime', event['start'].get('date'))
        event_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S%z').date()
        
        event_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S%z')
        tz = pytz.timezone('America/New_York')
        event_datetime = event_datetime.astimezone(tz)
        event_time = event_datetime.strftime('%I:%M %p')

        if event_date == today:
            if(event['summary'] == 'Rise and Shine Program'):
                await channel.send(f"@everyone \nReminder: **{event['summary']}** is happening today at {event_time}!\nTry to make it on time <:__:1275646122790228019>")
            else:
                await channel.send(f"@everyone \nReminder: **{event['summary']}** is happening today at {event_time}!\nTry to make it on time!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    announce_events.start()

webserver.keep_alive()
bot.run(DISCORD_TOKEN)