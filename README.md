# episodic 🎬

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-episodic-red.svg)](https://pypi.org/project/episodic/)

**episodic** - A powerful tool for automatically renaming TV series files using episode titles from IMDB.

## ✨ Features

- 🎯 **Automatic episode title fetching** from IMDB
- 🔍 **Auto-detection of seasons** from folder structure or file names
- 📺 **Double episodes support** (one file = two episodes)
- 🎨 **Beautiful interface** with colored output and progress bars
- 📝 **Preview mode** for changes
- ⚙️ **Flexible configuration** through files
- 🚀 **Process all seasons** with one command
- 🎬 **Multiple video format support**

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/br3nd4nt/episodic.git
cd episodic

# Install in development mode
pip install -e .
```

After installation, the `episodic` command will be available from any directory.

## 📖 Usage

### Basic Commands

```bash
# Rename episodes in current directory
episodic -s "Breaking Bad" -n 1

# Specify path to episodes folder
episodic -p /path/to/episodes -s "Breaking Bad" -n 1

# Auto-detect season
episodic -p /path/to/episodes -s "Breaking Bad"
```

### Double Episodes

```bash
# Process double episodes (one file = two episodes)
episodic -p /path/to/episodes -s "Breaking Bad" -n 1 -d

# Auto-detect double episodes format
episodic -p /path/to/episodes -s "Breaking Bad" -n 1
```

### Process All Seasons

```bash
# Process all seasons in series folder
episodic -p /path/to/series -s "Breaking Bad" --all-seasons

# Specific season from series folder
episodic -p /path/to/series -s "Breaking Bad" -n 2
```

### Preview and Configuration

```bash
# Preview changes only
episodic -p /path/to/episodes -s "Breaking Bad" -n 1 -v

# Use configuration file
episodic -p /path/to/episodes -c rename_config.txt

# Save configuration without applying changes
episodic -p /path/to/episodes -s "Breaking Bad" --save-config my_config.txt
```

### Additional Options

```bash
# Verbose output for debugging
episodic -p /path/to/episodes -s "Breaking Bad" -n 1 --verbose

# Help
episodic -h
```

## 📁 Supported Formats

**Video files:** `mkv`, `mp4`, `avi`, `mov`, `wmv`, `flv`, `webm`

**Folder structure:**
```
Series/
├── Season 1/
│   ├── episode1.mkv
│   └── episode2.mkv
├── Season 2/
│   ├── episode1.mkv
│   └── episode2.mkv
└── ...
```

## 📝 Output Format

### Regular Episodes
```
Episode 01 - Pilot.mkv
Episode 02 - Cat's in the Bag....mkv
Episode 03 - ...And the Bag's in the River.mkv
```

### Double Episodes
```
Episode 01-02 - Pilot + Cat's in the Bag....mkv
Episode 03-04 - ...And the Bag's in the River + Cancer Man.mkv
```

## ⚙️ Configuration Files

If episode titles are missing, a configuration file is generated:

```
# Configuration for file renaming
# Format: old_file -> new_file
# Leave empty after -> to skip file

old_file.mp4 -> Episode 01 - Pilot.mp4
old_file2.mp4 -> Episode 02 - The Heist.mp4
old_file3.mp4 ->
```

Edit the file and run with `--config` parameter.

## 🎨 Interface Features

- 🌈 **Colored output** for better perception
- 📊 **Progress bars** for long operations
- 🎯 **Auto-clear screen** for better UX
- ⚠️ **Warnings and errors** with color indication
- 🔍 **Detailed diagnostics** in verbose mode

## 🔧 Auto-detection

### Seasons
- From folder names: `Season 1`, `S01`, `1`
- From file names: `S01E01`, `1x01`, `1.01`

### Double Episodes
- `S01E01E02`, `E01E02`, `1x01-02`
- `Ep01-02`, `Episode01-02`

## 📋 Usage Examples

### Example 1: Regular Series
```bash
# Rename Breaking Bad season 1 episodes
episodic -p ~/Videos/Breaking_Bad_S01 -s "Breaking Bad" -n 1
```

### Example 2: Double Episodes
```bash
# Process double episodes
episodic -p ~/Videos/Show_S01 -s "Your Show" -n 1 -d
```

### Example 3: All Seasons
```bash
# Process all seasons of a series
episodic -p ~/Videos/Complete_Series -s "Breaking Bad" --all-seasons
```

### Example 4: Preview Mode
```bash
# Preview what will be renamed without applying
episodic -p ~/Videos/Show -s "Your Show" -n 1 -v
```

## 🐛 Troubleshooting

### Problem: Show not found on IMDB
- Check the spelling of the show name
- Try alternative show names
- Ensure internet connection is available

### Problem: Episodes not found
- Check the season number is correct
- Ensure files have supported extensions
- Check folder structure

### Problem: Wrong titles
- Use preview mode (`-v`)
- Edit configuration file manually
- Check double episodes format

## 🤝 Contributing

We welcome contributions! Please create issues and pull requests.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Click](https://click.palletsprojects.com/) - for creating CLI interface
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - for HTML parsing
- [Colorama](https://github.com/tartley/colorama) - for colored output
- [IMDB](https://www.imdb.com/) - for providing series data

---

**Created with ❤️ for the TV series community**