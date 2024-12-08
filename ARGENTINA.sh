#!/bin/bash

echo $(dirname $0)

python3 -m pip install requests streamlink beautifulsoup4 selenium

python3 $(dirname $0)/scripts/ARGENTINA2.py

echo Done!
