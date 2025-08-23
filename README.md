# episodic 🎬

Automatically rename TV series files using episode titles from IMDB.

## Installation

```bash
pip install -e .
```

After installation, you can use `episodic` command from anywhere.

## Usage

```bash
# Basic usage
episodic -p /path/to/episodes -s "Breaking Bad" -n 1

# Auto-detect season
episodic -p /path/to/episodes -s "Breaking Bad"

# Double episodes
episodic -p /path/to/episodes -s "Breaking Bad" -n 1 -d

# Preview only
episodic -p /path/to/episodes -s "Breaking Bad" -n 1 -v

# Use config file
episodic -p /path/to/episodes -c rename_config.txt

# Save config without applying
episodic -p /path/to/episodes -s "Breaking Bad" --save-config my_config.txt

# Help
episodic -h
```

## Features

- Fetch episode titles from IMDB
- Support for double episodes (one file = two episodes)
- Manual config editing when needed
- Preview mode
- Multiple video formats support

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