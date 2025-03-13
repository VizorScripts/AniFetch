<a id="readme-top"></a>
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/yourusername/AniFetch">
    <img src="https://i.pinimg.com/736x/e2/02/14/e202142258d3dbd64b4dd5aacd7fca5e.jpg" alt="AniFetch Logo" width="80" height="80">
  </a>

  <h3 align="center">AniFetch Discord Bot</h3>

  <p align="center">
    Your go-to Discord bot for anime episode schedules and updates!<br />
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#launch-instructions">Launch Instructions</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
<p align="center">
AniFetch is a versatile Discord bot designed to fetch and display anime episode schedules and updates directly in your server. Whether you're looking for dubbed, subbed, or even hentai episodes (if enabled), AniFetch delivers the latest information in beautifully formatted embeds! 🤖✨

<p align="right">(<a href="#readme-top">back to top</a>)</p>

   <p align="center">
  <img src="https://github.com/user-attachments/assets/fd7763af-350f-491a-ab78-e55b71277f86">
</div>

   <p align="center">
  <img src="https://github.com/user-attachments/assets/a013b94e-3cfb-4e8b-a79e-46d97d8ec0f0">
</div>

### Built With

* [Python](https://www.python.org/)
* [discord.py](https://discordpy.readthedocs.io/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [python-dateutil](https://dateutil.readthedocs.io/)
* [Requests](https://docs.python-requests.org/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Follow these steps to get a local copy of AniFetch up and running.

### Prerequisites

- **Python 3.8+** installed on your system.
- A Discord bot token and the IDs for the channels where the bot will operate.
- Required Python packages:

 
  ```bash
  pip install discord.py python-dotenv python-dateutil requests
<p align="center">
  
## Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/VizorScripts/AniFetch.git
   
2. **Navigate to the project directory:**
   ```sh
   cd AniFetch
   
3. **Create a .env file in the root directory with the following content (replace placeholder values):**
   ```sh
   DISCORD_TOKEN=your_discord_bot_token
    COMMAND_CHANNEL=your_command_channel_id
    DUB_FEED_CHANNEL=your_dub_feed_channel_id
    SUB_FEED_CHANNEL=your_sub_feed_channel_id
    # Optional: Enable and specify the hentai channel
    HENTAI_CHANNEL=your_hentai_channel_id
    EXCLUDE_HENTAI=True  # Set to False to enable hentai features
    TIMEZONE=your_timezone   # e.g., UTC, America/New_York, etc.
    RAPIDAPI_KEY=your_rapidapi_key
    RAPIDAPI_HOST=anime-schedule.p.rapidapi.com

   
1. **Verify Environment Variables:** (DISCORD_TOKEN, COMMAND_CHANNEL, DUB_FEED_CHANNEL, SUB_FEED_CHANNEL)

   Ensure that all required variables are set correctly.
   The bot will exit if any are missing.

## Usage
Slash Commands:
Use the following commands within Discord to search for anime episodes:


- /dub [query] – Search for dubbed anime episodes.
- /sub [query] – Search for subbed anime episodes.
- /hent [query] – Search for hentai episodes (if enabled).

**Automatic Updates:**
AniFetch auto refreshes its data every 15 minutes, ensuring the latest episode information is always available.

**Rich Embeds:**
Detailed anime information is presented using visually appealing embeds, complete with cover images and formatted airing times.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Features
- 🔄 Automatic Data Refresh:
    - Updates schedules and episode feeds every 15 minutes from multiple sources.

- 🔍 Slash Command Search:
    - Easily search for dubbed, subbed, or hentai anime episodes directly from Discord.

- 🎨 Rich Embeds:
    - Presents detailed anime information with formatted dates, cover images, and episode airing times.

- 🌐 Multiple Data Sources:
    - Integrates with GitHub-hosted JSON feeds and RapidAPI endpoints for comprehensive data.

- 🛠️ Robust Logging & Error Handling:
    - Logs are output to both the console and a debug log file (anifetch-debug.log) to assist in troubleshooting.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Launch Instructions

- Windows
  - Using run.bat (Recommended): Simply double-click the run.bat file in the project directory to launch the bot.
[OR]
  - Using Command Prompt or PowerShell:
      1. Open Command Prompt or PowerShell.
      2. Navigate to the bot's directory: cd path\to\AniFetch
      3. Run the bot: python your_bot_file.py


 - macOS / Linux
      1. Open your Terminal
      2. Navigate to the bot's directory: cd cd /path/to/AniFetch
      3. Run the bot: python3 your_bot_file.py
         - (Use python if your system is configured to use Python 3 by default.)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap
 * Enhanced Error Reporting: More detailed logging and error notifications.
 * Additional Data Sources: Integration with more APIs and data feeds.

## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.
If you have suggestions to improve AniFetch, please fork the repository and create a pull request. You can also open an issue with the tag "enhancement".
    1. Fork the Project
    2. Create your Feature Branch: git checkout -b feature/AniFetch
    3. Commit your Changes: git commit -m 'Add some AniFetch'
    4. Push to the Branch: git push origin feature/AniFetch
    5. Open a Pull Request!
  <p align="right">(<a href="#readme-top">back to top</a>)</p>

  ## License
  Distributed under the MIT License. See the LICENSE file for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Contact
Vizor - vizordynamics@gmail.com
Project Link: https://github.com/vizorscripts/AniFetch

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments
  - **Inspiration:** AniFetch was inspired by various anime schedule projects and the growing need for dynamic Discord integrations.
  - **Community:** Thanks to the developers and maintainers of discord.py and other open source projects that made this bot possible.
  - **Assets:** All images, logos, or icons used are courtesy of their respective owners.
  - **[emargi & others](https://github.com/othneildrew/Best-README-Template/tree/main)** for making this README.MD look this nice.
<p align="right">(<a href="#readme-top">back to top</a>)</p> 


<p align="center">
Contact
Vizor - vizordynamics@gmail.com
<p align="right">(<a href="#readme-top">back to top</a>)</p>
<p align="center"> .vizor
