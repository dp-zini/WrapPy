# WrapPy

Uses VLC log file to find play history and wraps it up for you.

## Installation
You need to set up VLC logging. Open VLC -> Tools -> Preferences, Select All settings in the bottom right of the menu, logger, create log file, set log settings to debug and you're ready.

You can dump the vlc_media.db on android from Settings -> Advanced -> Dump Media Database.
From there you can get the file from the root of your device and run the script with it.

``` python
pip install mutagen pandas
```
## Usage
``` python
$ python wrap.py
```
From the CLI:
- Enter log file path
- You're done!

## Contributions
Feel free to contribute.

## License
Licensed under the MIT License, for more info see [LICENSE](https://github.com/dp-zini/WrapPy/blob/main/LICENSE)

Not affiliated with Spotify, at all.
