# ForeFlight tracklog downloader, plotter

Downloader inspired by [Niner-Systems/ForeFlightKMLRetrieval](https://github.com/Niner-Systems/ForeFlightKMLRetrieval) and adpated to work with ForeFlight's current endpoints.

## Installation
```
pip install -r requirements.txt
```

## Usage 
1. As shown in [the other project's instructional video](https://youtu.be/kJTHsCT75Lc), use browser dev tools to extract a curl command which contains your ForeFlight authentication and put this command into the file `curl_command.sh`.
2. Run [download.py](./download.py) to download KMLs of all your ForeFlight tracklogs into the folder `tracklogs/`.
3. Run [plot.py](./plot.py) to draw a map of all tracklogs to `map.png`. Optionally specify parameters such as `--year 2025` to only plot tracks from that year.
