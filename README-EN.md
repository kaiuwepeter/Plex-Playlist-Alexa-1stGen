# Plex Shuffle Playlist Generator

This Python script is designed to address a recurring challenge when using Plex playlists with Amazon Alexa, especially with older Echo devices. It dynamically generates a Plex playlist with its tracks arranged in a random order to enable a "pseudo-shuffle playback."

-----

## Table of Contents

1.  [The Problem: Alexa and Plex Shuffle](#1-the-problem-alexa-and-plex-shuffle)
    * [Alexa 1st Gen Limitations](#alexa-1st-gen-limitations)
    * [Plex Skill and Context Loss](#plex-skill-and-context-loss)
    * [The "Client Profile" Issue](#the-client-profile-issue)
2.  [The Solution: "Pseudo-Shuffled Playlist" via API](#2-the-solution-pseudo-shuffled-playlist-via-api)
    * [How It Works](#how-it-works)
    * [Advantages of This Method](#advantages-of-this-method)
    * [Limitations of This Method](#limitations-of-this-method)
3.  [Prerequisites](#3-prerequisites)
4.  [Installation](#4-installation)
5.  [Script Configuration](#5-script-configuration)
6.  [Running the Script](#6-running-the-script)
7.  [Usage with Alexa](#7-usage-with-alexa)
8.  [Automation with Cron (Linux) / Task Scheduler (Windows)](#8-automation-with-cron-linux--task-scheduler-windows)
    * [Important Note on Ongoing Playback During Automation](#important-note-on-ongoing-playback-during-automation)
9.  [Troubleshooting](#9-troubleshooting)
10. [Contribution](#10-contribution)
11. [License](#11-license)

-----

## 1\. The Problem: Alexa and Plex Shuffle

Users of Plex in conjunction with Amazon Alexa often face the challenge of playing playlists in shuffle mode. Although Plex offers native shuffle functionality and Alexa understands generic commands for it, the combination fails in specific scenarios.

### Alexa 1st Gen Limitations

A primary reason for these difficulties lies in the use of **Amazon Echo 1st Generation devices**. These devices no longer receive new feature updates and are often not fully compatible with the latest APIs and communication protocols of modern services like Plex. This leads to a fundamental problem in communication between the Echo and the Plex Media Server.

### Plex Skill and Context Loss

When attempting to activate shuffle mode via voice commands like `"Alexa, tell Plex to play playlist [Name] in shuffle mode"` or `"Alexa, tell Plex to enable shuffle mode"`, Alexa often responds with error messages such as "I didn't understand what you want to play" or simply ignores the command and plays the playlist linearly. This indicates that the Plex Skill loses context of the ongoing playback or cannot correctly interpret and forward the shuffle command to the server.

### The "Client Profile" Issue

In the Plex Media Server's debug log, the following message frequently appears:
`[Now] Unable to find client profile for device platform=Alexa, platformVersion=, device=Alexa, model=`

This message is a strong indicator of the core problem:

  * **Missing Device Information:** The Echo 1st Generation device does not transmit complete identification information (such as `platformVersion` and `model`) to the Plex Media Server.
  * **Disrupted Communication:** Without a proper "client profile," the Plex Server doesn't know how to optimally communicate with the Echo or provide advanced playback features like shuffle mode. The server falls back to a generic playback method that does not account for shuffling.
  * **Persistent Problem:** Since this message often appears permanently in the log, even during playback without active voice commands, it indicates a deep-seated compatibility issue at the protocol level that cannot be resolved with simple skill reinstallation or voice commands.

-----

## 2\. The Solution: "Pseudo-Shuffled Playlist" via API

Since Alexa has difficulty dynamically controlling Plex's shuffle function, we circumvent the problem by creating the playlist **pre-shuffled** on the Plex Media Server.

### How It Works

1.  **API Access:** The Python script uses the `plexapi` library to connect directly to your Plex Media Server.
2.  **Artist Selection:** You provide a list of your desired artists in the script.
3.  **Collect and Shuffle Tracks:** The script searches your music library for tracks by these artists, collects them, and then **shuffles** them into a random order.
4.  **Playlist Creation:** A new Plex playlist is created with the name you specify. The key feature is that the tracks are added to this playlist already in the shuffled order.
5.  **Alexa Playback:** When you then instruct Alexa to play this playlist, she doesn't need to activate a "shuffle" mode. She simply plays the playlist in the order the tracks are already arranged – i.e., in the fixed, random order.

### Advantages of This Method

  * **Bypasses Alexa Compatibility Issues:** Alexa doesn't need to interpret a complex "shuffle" command or deal with an incomplete client profile. She simply plays a pre-arranged list.
  * **Reliable "Random Playback":** The order of the tracks is guaranteed to be random, as it's determined by the script at the server level.
  * **Persistent:** The created playlist exists permanently on your Plex Media Server until it is deleted or overwritten by the script.

### Limitations of This Method

  * **"Pseudo-Shuffle":** The order is only random at the time of playlist creation. If you play the playlist again, it will always play in the **same fixed, random order**, not a *new* random order.
  * **Manual Refresh for New Random Order:** To get a new, fresh random order, you must run the script again. This deletes the old playlist and creates a new one with the same tracks in a newly shuffled order.
  * **Playback Interruption during Automation:** If the script runs while Alexa is playing this playlist, playback will be **interrupted** once the currently playing track ends. Alexa will stop playback because her internal playback queue refers to the old, now non-existent playlist. To use the newly generated playlist, playback must then be manually restarted.

-----

## 3\. Prerequisites

  * **Plex Media Server:** Must be installed and running.
  * **Python:** Version 3.x should be installed on the system where you run the script.
  * **`plexapi` Library:** A Python library for interacting with the Plex API.

-----

## 4\. Installation

1.  **Install Python:** If you haven't already, download Python 3.x from [python.org](https://www.python.org/downloads/) and install it. Make sure to select the "Add Python to PATH" option during installation.
2.  **Install `plexapi`:** Open a terminal or command prompt and run the following command:
    ```bash
    pip install plexapi
    ```

-----

## 5\. Script Configuration

Open the script file (`playlist.py`) with a text editor and adjust the following variables in the `--- CONFIGURATION ---` section:

  * **`PLEX_URL`**:

      * This is the full address of your Plex Media Server, including the port (default `32400`).
      * Example: `'http://192.168.1.100:32400'` (for local networks) or `'https://yourserver.dyndns.net:32400'` (if you're using a Dyndns address).
      * **Important:** Use `http://` or `https://` depending on how your server is configured.

  * **`PLEX_TOKEN`**:

      * Your personal Plex X-Plex-Token for authentication.
      * You can find it in the Plex Web App: Navigate to any page (e.g., a movie), press `F12` in your browser, go to the "Network" tab, reload the page, and look for any request. In the request header, you'll find the `X-Plex-Token`.

  * **`MUSIC_LIBRARY_NAME`**:

      * The **EXACT name** of your music library in Plex. Pay attention to case sensitivity and spaces.
      * Example: `'Music'`, `'My Songs'`, `'Audio'`.

  * **`NEW_PLAYLIST_NAME`**:

      * The name the newly created playlist will have in Plex.
      * Example: `'My Random Playlist'`, `'Rock Hits Mixed'`.

  * **`ARTISTS_TO_INCLUDE`**:

      * A list of artists (strings) whose tracks you want to include in the playlist.
      * The names must **EXACTLY** match how they appear in your Plex library (case sensitivity matters\!).
      * Example: `['Artist A', 'Artist B', 'Artist C']`

  * **`MAX_SONGS_PER_ARTIST`**:

      * (Optional) A maximum number of tracks to include per artist in the playlist. This prevents a single artist from dominating the playlist.
      * Set this value to `None` if you want to include **all** tracks from each specified artist.

-----

## 6\. Running the Script

1.  Save the script as a `.py` file (e.g., `playlist_generator.py`).
2.  Open a terminal or command prompt.
3.  Navigate to the directory where you saved the script file.
4.  Execute the script using the following command:
    ```bash
    python playlist_generator.py
    ```
5.  The script will output progress information and display the command you need to tell Alexa at the end.

-----

## 7\. Usage with Alexa

After the script has successfully run and the playlist is created in Plex, you can play it via Alexa.

  * **Give the command to your Echo device:**
    ```
    "Alexa, tell Plex to play playlist [NEW_PLAYLIST_NAME]"
    ```
    (Replace `[NEW_PLAYLIST_NAME]` with the name you set in the script configuration, e.g., `"Alexa, tell Plex to play playlist My Random Playlist"`)

The playlist will now play in the order that was randomly generated by the script at the time of creation.

-----

## 8\. Automation with Cron (Linux) / Task Scheduler (Windows)

You can automate the script to regularly update the playlist, ensuring a "fresh" random order.

### Important Note on Ongoing Playback During Automation

**The script deletes and recreates the playlist.** If the script runs while Alexa is playing this playlist, playback will be **interrupted** once the currently playing track ends. Alexa will stop playback because her internal playback queue refers to the old, non-existent playlist.

**This means:** To hear the newly shuffled order, you must **manually stop playback and then restart it** (using the command mentioned in Section 7) after the script has run in the background.

**Example for Cron (Linux):**

1.  Save the script to a fixed location, e.g., `/home/user/plex_scripts/playlist_generator.py`.
2.  Open the Cron editor: `crontab -e`
3.  Add a line to run the script every 2 hours, for example:
    ```cron
    0 */2 * * * /usr/bin/python3 /home/user/plex_scripts/playlist_generator.py >> /home/user/plex_scripts/playlist_log.log 2>&1
    ```
    (Adjust the path to Python and the script according to your system.)

**Example for Task Scheduler (Windows):**

1.  Save the script to a fixed location, e.g., `C:\PlexScripts\playlist_generator.py`.
2.  Open "Task Scheduler."
3.  Create a new task (Basic Task or Create Task...).
4.  **Trigger:** Choose "Daily" and set the time, or select "At a specific event," "At startup," etc., to define a regular execution.
5.  **Action:** Choose "Start a program."
      * **Program/script:** `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3X\python.exe` (Adjust the path to your Python installation)
      * **Add arguments (optional):** `C:\PlexScripts\playlist_generator.py` (Path to your script)
      * **Start in:** `C:\PlexScripts\` (The directory where your script is located)

-----

## 9\. Troubleshooting

  * **"Error: Music library named '[Name]' not found."**: Check the value of `MUSIC_LIBRARY_NAME` in the script. It must exactly match the name of your music library in Plex (case sensitivity, spaces).
  * **"Warning: Artist '[Name]' not found in library."**: Check the spelling of the artist's name in `ARTISTS_TO_INCLUDE`. It must exactly match the artist's name in your Plex library.
  * **"An unexpected error occurred:..."**: Check `PLEX_URL` and `PLEX_TOKEN`. Ensure your Plex Media Server is running and accessible from the script's machine (e.g., by opening the `PLEX_URL` in a browser). Your token should be correct.
  * **Playlist is created, but Alexa does not play in shuffle mode:** This is the core problem this script solves. Make sure you restart the playlist with the command given in Section 7 after the script has run.

-----

## 10\. Contribution

Suggestions for improvement or bug reports are welcome\!

-----

## 11\. License

This script is provided under the MIT License.

-----
