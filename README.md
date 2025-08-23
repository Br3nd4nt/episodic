# episodic 🎬

Automatically rename TV series files using episode titles from IMDB.

## Features

- Fetch episode titles from IMDB
- Support for double episodes (one file = two episodes)
- Manual config editing when needed
- Preview mode
- Multiple video formats support

## Usage

```bash
# Basic usage
python episodic.py -p /path/to/episodes -s "Breaking Bad" -n 1

# Double episodes
python episodic.py -p /path/to/episodes -s "Breaking Bad" -n 1 -d

# Preview only
python episodic.py -p /path/to/episodes -s "Breaking Bad" -n 1 --preview

# Use config file
python episodic.py -p /path/to/episodes --config rename_config.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Output Format

```
Episode 01 - Pilot.mkv
Episode 02 - Cat's in the Bag....mkv
Episode 03 - ...And the Bag's in the River.mkv
```

## Config File

If episode titles are missing, a config file is generated:

```
old_file.mp4 -> Episode 01 - Pilot.mp4
old_file2.mp4 -> Episode 02 - The Heist.mp4
old_file3.mp4 ->
```

Edit the file and run with `--config`.

## Supported Formats

mkv, mp4, avi, mov, wmv, flv, webm