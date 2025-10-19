from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

def open_browser_window():
    # Open PokePaste in the default web browser
    url = "https://pokepast.es/"
    QDesktopServices.openUrl(QUrl(url))

# Define the function to open the Pokémon Showdown Team Builder
def open_team_builder():
    # Specify the URL of the Pokémon Showdown Team Builder
    team_builder_url = "https://play.pokemonshowdown.com/teambuilder"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(team_builder_url))

def rate_addon_url():
    # Specify the URL of the Anki addon
    rating_url = "https://ankiweb.net/shared/review/1908235722"

    # Open the Anki addon in the default web browser
    QDesktopServices.openUrl(QUrl(rating_url))

def report_bug():
    # Specify the URL of the Ankimon issue tracker
    bug_url = "https://github.com/h0tp-ftw/ankimon/issues"

    # Open the Ankimon issue tracker in the default web browser
    QDesktopServices.openUrl(QUrl(bug_url))

def join_discord_url():
    # Specify the URL of the discord invite
    discord_url = "https://discord.gg/hcq53X5mcu"

    # Open the discord invite in the default web browser
    QDesktopServices.openUrl(QUrl(discord_url))

def open_leaderboard_url():
    # Specify the URL of the Ankimon leaderboard
    leaderboard_url = "https://leaderboard.ankimon.com/"

    # Open the leaderboard in the default web browser
    QDesktopServices.openUrl(QUrl(leaderboard_url))