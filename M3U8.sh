#!/bin/bash

echo $(dirname $0)

python3 -m pip install requests streamlink beautifulsoup4 selenium yt-dlp youtube-dl

python3 $(dirname $0)/GLOBO.py
python3 $(dirname $0)/it.py



echo Done!
