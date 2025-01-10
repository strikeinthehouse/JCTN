#!/bin/bash

echo $(dirname $0)

python3 -m pip install requests streamlink beautifulsoup4 selenium yt-dlp youtube-dl

python3 $(dirname $0)/scripts/TWITCH.py
python3 $(dirname $0)/scripts/TWITCH2.py
python3 $(dirname $0)/scripts/TWITCH3.py

echo Done!
