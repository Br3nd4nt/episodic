#!/usr/bin/env python3

import os
import re
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import click
import time
import sys

# Color support
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback colors for terminals that support ANSI
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    
    class Back:
        RED = '\033[101m'
        GREEN = '\033[102m'
        YELLOW = '\033[103m'
        BLUE = '\033[104m'
        MAGENTA = '\033[105m'
        CYAN = '\033[106m'
        WHITE = '\033[107m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        NORMAL = '\033[22m'
        RESET_ALL = '\033[0m'

CONFIG_FILENAME = "rename_config.txt"
SUPPORTED_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a beautiful header"""
    click.echo(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")
    click.echo(f"{Fore.YELLOW}{Style.BRIGHT}🎬 {title}{Style.RESET_ALL}")
    click.echo(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}{Style.RESET_ALL}")

def print_progress(current, total, prefix="Progress"):
    """Print a progress bar"""
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = f"{Fore.GREEN}{'█' * filled_length}{Style.RESET_ALL}{Fore.WHITE}{'░' * (bar_length - filled_length)}{Style.RESET_ALL}"
    click.echo(f'\r{Fore.BLUE}{prefix}{Style.RESET_ALL}: [{bar}] {current}/{total} ({current/total*100:.1f}%)', nl=False)
    if current == total:
        click.echo()  # New line when complete

def colored_echo(message, color=Fore.WHITE, style=Style.NORMAL):
    """Print colored message"""
    click.echo(f"{color}{style}{message}{Style.RESET_ALL}")

def success_echo(message):
    """Print success message in green"""
    colored_echo(message, Fore.GREEN, Style.BRIGHT)

def error_echo(message):
    """Print error message in red"""
    colored_echo(message, Fore.RED, Style.BRIGHT)

def warning_echo(message):
    """Print warning message in yellow"""
    colored_echo(message, Fore.YELLOW, Style.BRIGHT)

def info_echo(message):
    """Print info message in blue"""
    colored_echo(message, Fore.BLUE, Style.BRIGHT)

def highlight_echo(message):
    """Print highlighted message in cyan"""
    colored_echo(message, Fore.CYAN, Style.BRIGHT)

def find_show_on_imdb(show):
    """Find show URL on IMDB"""
    search_url = f"https://www.imdb.com/find/?q={quote(show)}&s=tt&ttype=tv"
    
    try:
        info_echo(f"🔍 Searching for '{show}' on IMDB...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple selectors for search results
        results = (
            soup.find_all("td", class_="result_text") or
            soup.find_all("li", class_="find-result-item") or
            soup.find_all("li", class_="ipc-metadata-list-summary-item") or
            soup.find_all("div", class_="titleResult")
        )
        
        if not results:
            error_echo("❌ No search results found")
            warning_echo("🔧 Try a different show name or check spelling")
            return None
        
        info_echo(f"🔍 Found {len(results)} search results")
        
        show_url = None
        for result in results[:5]:  # Check more results
            # Try different link selectors
            link = (
                result.find("a") or
                result.find("a", class_="ipc-metadata-list-summary-item__t") or
                result.find("h3", class_="ipc-title__text")
            )
            
            if link:
                href = link.get("href", "")
                if "/title/" in href:
                    if not href.startswith("http"):
                        show_url = "https://www.imdb.com" + href
                    else:
                        show_url = href
                    
                    # Clean up URL - remove query parameters
                    if "?" in show_url:
                        show_url = show_url.split("?")[0]
                    
                    success_echo(f"✅ Found show: {show_url}")
                    return show_url
        
        error_echo("❌ No valid show found in results")
        return None
        
    except Exception as e:
        error_echo(f"❌ Error searching IMDB: {e}")
        return None

def get_episode_titles(show_url, season):
    """Get episode titles for a specific season using existing show URL"""
    try:
        # Get episodes for the season
        episodes_url = f"{show_url}episodes/?season={season}"
        click.echo(f"🔍 Getting episodes for season {season}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(episodes_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        titles = []
        
        # Try multiple selectors for episode titles
        episode_selectors = [
            "div.info strong a",
            "div.info h4 a", 
            "h4 a",
            ".episode-item-wrapper .info strong a",
            ".episode-item .info strong a",
            "article h4 a",
            ".titleColumn a"
        ]
        
        for selector in episode_selectors:
            episode_links = soup.select(selector)
            if episode_links:
                click.echo(f"🎯 Using selector: {selector}")
                for link in episode_links:
                    title = link.get_text(strip=True)
                    if title and len(title) > 1:
                        # Clean up title - remove episode numbers and extra formatting
                        title = re.sub(r'^S\d+\.E\d+\s*∙\s*', '', title)  # Remove S1.E1 ∙
                        title = re.sub(r'^\d+\.\s*', '', title)  # Remove "1. "
                        title = re.sub(r'^Episode\s+\d+:\s*', '', title, flags=re.IGNORECASE)  # Remove "Episode 1: "
                        title = title.strip()
                        if title:
                            titles.append(title)
                break
        
        # Alternative: try to find episode titles in different structure
        if not titles:
            # Look for any links that might be episode titles
            all_links = soup.find_all("a")
            for link in all_links:
                href = link.get("href", "")
                if "/title/" in href and "season-" in href.lower():
                    title = link.get_text(strip=True)
                    if title and len(title) > 2 and not title.isdigit():
                        # Clean up title
                        title = re.sub(r'^S\d+\.E\d+\s*∙\s*', '', title)
                        title = re.sub(r'^\d+\.\s*', '', title)
                        title = re.sub(r'^Episode\s+\d+:\s*', '', title, flags=re.IGNORECASE)
                        title = title.strip()
                        if title:
                            titles.append(title)
        
        if titles:
            success_echo(f"✅ Found {len(titles)} episode titles")
            return titles[:50]  # Limit to reasonable number
        else:
            error_echo("❌ No episodes found for this season")
            warning_echo("🔧 Try checking if the season number is correct")
            return []
            
    except requests.RequestException as e:
        error_echo(f"❌ Network error: {e}")
        return []
    except Exception as e:
        error_echo(f"❌ Parsing error: {e}")
        return []

def get_video_files(folder_path):
    if not os.path.exists(folder_path):
        click.echo(f"❌ Folder does not exist: {folder_path}")
        return []
    
    files = []
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                files.append(f)
    
    return sorted(files)

def get_season_folders(series_path):
    """Get list of season folders in series directory"""
    if not os.path.exists(series_path):
        return []
    
    season_folders = []
    for item in os.listdir(series_path):
        item_path = os.path.join(series_path, item)
        if os.path.isdir(item_path):
            # Check if folder name suggests it's a season
            if any(pattern in item.lower() for pattern in ['season', 's', 'сезон']):
                season_folders.append(item)
    
    return sorted(season_folders)

def get_all_episodes_from_series(series_path):
    """Get all episodes from all season folders"""
    season_folders = get_season_folders(series_path)
    
    if not season_folders:
        # If no season folders, treat as single season
        return get_video_files(series_path), None
    
    all_files = []
    season_mapping = {}
    
    for season_folder in season_folders:
        season_path = os.path.join(series_path, season_folder)
        files = get_video_files(season_path)
        
        if files:
            # Detect season number from folder name
            season_num = detect_season_from_folder_name(season_folder)
            if season_num:
                season_mapping[season_num] = {
                    'path': season_path,
                    'files': files
                }
                all_files.extend(files)
    
    # If no valid season folders found, treat as single season
    if not season_mapping:
        return get_video_files(series_path), None
    
    return all_files, season_mapping

def detect_season_from_folder_name(folder_name):
    """Detect season number from folder name"""
    season_patterns = [
        r'S(\d{1,2})',           # S01, S1, S12
        r'Season\s*(\d{1,2})',   # Season 1, Season01
        r'^(\d{1,2})$',          # 1, 01, 12 (exact match only)
    ]
    
    for pattern in season_patterns:
        match = re.search(pattern, folder_name, re.IGNORECASE)
        if match:
            season_num = int(match.group(1))
            if 1 <= season_num <= 99:
                return season_num
    
    return None

def rename_season_folders(series_path, yes=False):
    """Rename season folders to standard format (Season 1, Season 2, etc.)"""
    if not os.path.exists(series_path):
        error_echo(f"❌ Series path does not exist: {series_path}")
        return False
    
    season_folders = get_season_folders(series_path)
    if not season_folders:
        info_echo("📁 No season folders found to rename")
        return True
    
    rename_mapping = {}
    
    for folder_name in season_folders:
        season_num = detect_season_from_folder_name(folder_name)
        if season_num:
            new_name = f"Season {season_num}"
            if folder_name != new_name:
                rename_mapping[folder_name] = new_name
    
    if not rename_mapping:
        info_echo("✅ All season folders already have standard names")
        return True
    
    # Show proposed changes
    highlight_echo("\n📁 Proposed folder renames:")
    click.echo(f"{Fore.CYAN}{'-' * 60}{Style.RESET_ALL}")
    
    for old_name, new_name in rename_mapping.items():
        info_echo(f"📝  {old_name}")
        success_echo(f"    -> {new_name}")
        click.echo()
    
    click.echo(f"{Fore.CYAN}{'-' * 60}{Style.RESET_ALL}")
    
    # Confirm and apply
    if yes or click.confirm("\nRename season folders?"):
        success_count = 0
        error_count = 0
        
        for old_name, new_name in rename_mapping.items():
            old_path = os.path.join(series_path, old_name)
            new_path = os.path.join(series_path, new_name)
            
            try:
                info_echo(f"📁 {old_name} -> {new_name}")
                os.rename(old_path, new_path)
                success_count += 1
            except OSError as e:
                error_echo(f"❌ Error renaming folder {old_name}: {e}")
                error_count += 1
        
        # Summary
        click.echo()
        if success_count > 0:
            success_echo(f"✅ Successfully renamed: {success_count} folders")
        if error_count > 0:
            error_echo(f"❌ Errors: {error_count} folders")
        
        if error_count == 0 and success_count > 0:
            success_echo("🎉 All season folders renamed successfully!")
        elif error_count > 0:
            warning_echo("💡 Some folders had issues. Check the errors above.")
        
        return True
    else:
        warning_echo("❌ Folder renaming cancelled.")
        return False

def detect_season_from_files(files):
    """Auto-detect season number from file names"""
    if not files:
        return None
    
    # Common patterns for season detection
    season_patterns = [
        r'S(\d{1,2})',           # S01, S1, S12
        r'Season\s*(\d{1,2})',   # Season 1, Season01
        r'(\d{1,2})x\d{1,2}',    # 1x01, 12x05
        r'(\d{1,2})\.\d{1,2}',   # 1.01, 12.05
        r'(\d{1,2})-\d{1,2}',    # 1-01, 12-05
    ]
    
    detected_seasons = []
    
    for filename in files:
        for pattern in season_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                season_num = int(match.group(1))
                if 1 <= season_num <= 99:  # Reasonable season range
                    detected_seasons.append(season_num)
                break
    
    if detected_seasons:
        # Return most common season number
        from collections import Counter
        season_counts = Counter(detected_seasons)
        most_common = season_counts.most_common(1)[0]
        
        if most_common[1] >= len(files) * 0.5:  # At least 50% of files match
            return most_common[0]
    
    return None

def detect_episode_format(files):
    """Auto-detect if episodes are double (one file = two episodes)"""
    if not files:
        return False
    
    # Patterns that suggest double episodes
    double_patterns = [
        r'S\d{1,2}E(\d{1,2})E(\d{1,2})', # S03E01E02 (most specific first)
        r'E(\d{1,2})E(\d{1,2})',     # E01E02
        r'E(\d{1,2})-E(\d{1,2})',    # E01-E02
        r'(\d{1,2})x(\d{1,2})',      # 1x01-02
        r'(\d{1,2})-(\d{1,2})',      # 1-01-02
        r'Ep(\d{1,2})-(\d{1,2})',    # Ep01-02
        r'Episode(\d{1,2})-(\d{1,2})', # Episode01-02
        r'ep(\d{1,2})-E(\d{1,2})',   # ep1-E02
        r'(\d{1,2})-E(\d{1,2})',     # 1-E02
        # Removed (\d{1,2})E(\d{1,2}) as it's too generic and matches S06E01
    ]
    
    double_count = 0
    total_files = len(files)
    
    for filename in files:
        for pattern in double_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                double_count += 1
                break
    
    # If more than 30% of files match double episode patterns, consider it double
    return double_count >= total_files * 0.3

def clean_filename(title):
    """Clean episode title for safe filename creation"""
    import re
    
    # Replace problematic characters with safe alternatives
    replacements = {
        '/': ' and ',
        '\\': ' and ',
        ':': ' - ',
        '*': '',
        '?': '',
        '"': '',
        '<': '',
        '>': '',
        '|': ' - ',
        '+': ' and ',
        '&': ' and ',
    }
    
    # Apply replacements
    for char, replacement in replacements.items():
        title = title.replace(char, replacement)
    
    # Remove multiple spaces and dashes
    title = re.sub(r'\s+', ' ', title)
    title = re.sub(r'-+', '-', title)
    
    # Remove leading/trailing spaces and dashes
    title = title.strip(' -')
    
    return title

def generate_mapping(files, titles, double=False):
    mapping = {}
    ep = 1
    
    for f in files:
        ext = os.path.splitext(f)[1]
        
        if double:
            if ep + 1 <= len(titles):
                # For double episodes, use both titles in one filename
                # Format: Episode 01-02 - Title1 + Title2
                title1 = clean_filename(titles[ep-1])
                title2 = clean_filename(titles[ep])
                new_name = f"Episode {ep:02d}-{ep+1:02d} - {title1} and {title2}{ext}"
                ep += 2
            else:
                new_name = ""
            mapping[f] = new_name
        else:
            if ep <= len(titles):
                title = clean_filename(titles[ep-1])
                new_name = f"Episode {ep:02d} - {title}{ext}"
                ep += 1
            else:
                new_name = ""
            mapping[f] = new_name
    
    return mapping

def dump_config(mapping, path, filename=None):
    if filename is None:
        filename = CONFIG_FILENAME
    
    cfg_path = os.path.join(path, filename)
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write("# Configuration for file renaming\n")
        f.write("# Format: old_file -> new_file\n")
        f.write("# Leave empty after -> to skip file\n\n")
        
        for old, new in mapping.items():
            f.write(f"{old} -> {new}\n")
    
    # Check if this is a save-config operation (filename is not None) vs auto-save due to missing titles
    if filename is not None:
        success_echo(f"💾 Configuration saved to: {cfg_path}")
        info_echo(f"📝 Edit the file and run: episodic -p {path} -c {filename}")
    else:
        warning_echo(f"⚠️ Not enough titles. Config saved to {cfg_path}")
        info_echo("📝 Edit the file and run again with -c")

def load_config(config_path):
    if not os.path.exists(config_path):
        error_echo(f"❌ Config file not found: {config_path}")
        return {}
    
    mapping = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if "->" not in line:
                warning_echo(f"⚠️ Skipped line {line_num}: wrong format")
                continue
            
            parts = line.split("->", 1)
            if len(parts) != 2:
                warning_echo(f"⚠️ Skipped line {line_num}: wrong format")
                continue
            
            old = parts[0].strip()
            new = parts[1].strip()
            mapping[old] = new
    
    return mapping

def apply_mapping(mapping, folder):
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for old, new in mapping.items():
        if not new:
            warning_echo(f"⚠️ Skipped: {old} (no new name)")
            skip_count += 1
            continue
        
        old_path = os.path.join(folder, old)
        new_path = os.path.join(folder, new)
        
        if not os.path.exists(old_path):
            error_echo(f"❌ File not found: {old}")
            error_count += 1
            continue
        
        if os.path.exists(new_path):
            error_echo(f"❌ File already exists: {new}")
            error_count += 1
            continue
        
        try:
            info_echo(f"📝 {old} -> {new}")
            os.rename(old_path, new_path)
            success_count += 1
        except OSError as e:
            error_echo(f"❌ Error renaming {old}: {e}")
            error_count += 1
        except Exception as e:
            error_echo(f"❌ Unexpected error renaming {old}: {e}")
            error_count += 1
    
    # Summary with better formatting
    click.echo()
    if success_count > 0:
        success_echo(f"✅ Successfully renamed: {success_count} files")
    if skip_count > 0:
        warning_echo(f"⚠️ Skipped: {skip_count} files")
    if error_count > 0:
        error_echo(f"❌ Errors: {error_count} files")
    
    if error_count == 0 and success_count > 0:
        success_echo("🎉 All files processed successfully!")
    elif error_count > 0:
        warning_echo("💡 Some files had issues. Check the errors above.")

def preview_changes(mapping):
    highlight_echo("\n📋 Proposed changes:")
    click.echo(f"{Fore.CYAN}{'-' * 60}{Style.RESET_ALL}")
    
    for old, new in mapping.items():
        if not new:
            warning_echo(f"⚠️  {old} -> SKIPPED")
        else:
            info_echo(f"📝  {old}")
            success_echo(f"    -> {new}")
        click.echo()
    
    click.echo(f"{Fore.CYAN}{'-' * 60}{Style.RESET_ALL}")

@click.command(
    name='episodic',
    context_settings=dict(help_option_names=['-h', '--help']),
    help='Automatically rename TV series files using episode titles from IMDB.'
)
@click.option('-p', '--path', default='.', help='Path to folder with episodes (default: current directory)')
@click.option('-s', '--show', help='Show name (as on IMDB)')
@click.option('-n', '--season', type=int, help='Season number (auto-detected if not specified)')
@click.option('-d', '--double', is_flag=True, default=None, help='Force double episodes format (auto-detected if not specified)')
@click.option('-c', '--config', help='Use existing config file for renaming')
@click.option('-v', '--preview', is_flag=True, help='Only show changes without applying')
@click.option('--save-config', is_flag=True, help='Save configuration to file without applying changes')
@click.option('--config-file', default='rename_config.txt', help='Configuration filename (default: rename_config.txt)')
@click.option('--all-seasons', is_flag=True, help='Process all seasons automatically')
@click.option('--verbose', is_flag=True, help='Show detailed output for all operations')
@click.option('--yes', is_flag=True, help='Automatically confirm all rename operations without prompting')
@click.option('--rename-folders', is_flag=True, help='Rename season folders to standard format (Season 1, Season 2, etc.)')
@click.version_option(version='1.0.0')
def main(path, show, season, double, config, preview, save_config, config_file, all_seasons, verbose, yes, rename_folders):
    """episodic - TV Series File Renamer

    Automatically rename TV series files using episode titles from IMDB.

    Examples:
        episodic -s "Breaking Bad" -n 1                    # Use current directory
        episodic -p /path/to/episodes -s "Breaking Bad" -n 1
        episodic -s "Breaking Bad" -n 1 -d                 # Double episodes
        episodic -p /path/to/episodes -s "Breaking Bad" -n 1 -d
        episodic -s "Breaking Bad"                          # Auto-detect season
        episodic -p /path/to/episodes -s "Breaking Bad"
        episodic -s "Breaking Bad" --all-seasons           # Process all seasons
        episodic -p /path/to/series -s "Breaking Bad" --all-seasons
        episodic -s "Breaking Bad" -n 2                    # Specific season
        episodic -p /path/to/series -s "Breaking Bad" -n 2
        episodic -c rename_config.txt                       # Use config file
        episodic -p /path/to/episodes -c rename_config.txt
        episodic -s "Breaking Bad" --save-config           # Save config only
        episodic -p /path/to/episodes -s "Breaking Bad" --save-config
    """
    
    # Check if this is a series folder with multiple seasons
    all_files, season_mapping = get_all_episodes_from_series(path)
    
    # Handle folder renaming if requested
    if rename_folders:
        print_header("Renaming Season Folders")
        if not rename_season_folders(path, yes):
            return
        # Refresh season mapping after folder renaming
        all_files, season_mapping = get_all_episodes_from_series(path)
    
    if not all_files:
        click.echo("❌ No video files found in specified folder")
        return
    
    if season_mapping:
        # Multiple seasons found
        highlight_echo(f"📺 Found {len(season_mapping)} season folders:")
        for season_num in sorted(season_mapping.keys()):
            season_info = season_mapping[season_num]
            info_echo(f"   Season {season_num}: {len(season_info['files'])} episodes")
        info_echo(f"📁 Total: {len(all_files)} episodes")
    else:
        # Single season or flat structure
        files = all_files  # Use files already found by get_all_episodes_from_series
        info_echo(f"📁 Found {len(files)} video files in single folder")

    if config:
        mapping = load_config(config)
        if not mapping:
            return
        
        if save_config:
            # Save configuration to file
            dump_config(mapping, path, config_file)
            return
        
        preview_changes(mapping)
        
        if not preview:
            if yes or click.confirm("\nRename files?"):
                apply_mapping(mapping, path)
            else:
                warning_echo("❌ Cancelled.")
    else:
        if not show and not rename_folders:
            error_echo("❌ Need to specify --show, or --config, or --rename-folders")
            return
        
        # If only rename_folders is specified, exit after folder renaming
        if rename_folders and not show:
            return
        
        if all_seasons and season_mapping:
            # Process all seasons
            print_header("Processing All Seasons")
            
            # Find show URL once for all seasons
            show_url = find_show_on_imdb(show)
            if not show_url:
                error_echo("❌ Failed to find show on IMDB. Exiting.")
                return
            
            total_renamed = 0
            total_skipped = 0
            total_seasons = len(season_mapping)
            
            highlight_echo(f"🚀 Processing {total_seasons} seasons automatically...")
            
            for i, season_num in enumerate(sorted(season_mapping.keys()), 1):
                season_info = season_mapping[season_num]
                season_path = season_info['path']
                season_files = season_info['files']
                
                # Clear screen for interactive experience
                if not verbose:
                    clear_screen()
                    print_header(f"Processing Season {season_num}")
                    print_progress(i, total_seasons, "Seasons")
                
                info_echo(f"\n📺 Processing Season {season_num}...")
                
                # Auto-detect episode format for this season
                season_double = detect_episode_format(season_files)
                if season_double:
                    highlight_echo(f"🎬 Detected double episodes format for Season {season_num}")
                else:
                    highlight_echo(f"🎬 Detected single episodes format for Season {season_num}")
                
                titles = get_episode_titles(show_url, season_num)
                if not titles:
                    warning_echo(f"⚠️ Skipping season {season_num} - no titles found")
                    continue
                
                # Use season-specific format detection, but allow manual override
                use_double = double if double is not None else season_double
                mapping = generate_mapping(season_files, titles, use_double)
                
                if save_config:
                    # Use config_file for filename
                    config_filename = f"season_{season_num}_{config_file}"
                    dump_config(mapping, season_path, config_filename)
                    
                    if verbose:
                        success_echo(f"💾 Configuration saved for Season {season_num}")
                    continue
                
                if preview:
                    if verbose:
                        preview_changes(mapping)
                else:
                    if yes or click.confirm(f"Rename files in Season {season_num}?"):
                        apply_mapping(mapping, season_path)
                        total_renamed += sum(1 for new in mapping.values() if new)
                        total_skipped += sum(1 for new in mapping.values() if not new)
                    else:
                        warning_echo(f"❌ Skipped Season {season_num}")
                
                # Small delay for better UX
                if not verbose:
                    time.sleep(0.5)
            
            if not preview and not save_config:
                success_echo(f"\n🎉 All seasons processed!")
                info_echo(f"📊 Total renamed: {total_renamed}, skipped: {total_skipped}")
            
            # Final cleanup - clear screen and show summary
            if not verbose:
                clear_screen()
                print_header("Processing Complete")
                success_echo(f"🎉 All {total_seasons} seasons processed successfully!")
                info_echo(f"📊 Total renamed: {total_renamed}, skipped: {total_skipped}")
                if save_config:
                    success_echo("💾 All configurations saved to respective season folders")
            return
        
        # Single season processing
        if not season:
            if season_mapping:
                # Multiple seasons found, but no specific season specified
                info_echo("🔍 Multiple seasons found. Please specify season with -n or use --all-seasons")
                info_echo("Available seasons:")
                for season_num in sorted(season_mapping.keys()):
                    highlight_echo(f"   -n {season_num}")
                return
            else:
                # Single season, auto-detect from file names
                info_echo("🔍 Auto-detecting season number from file names...")
                season = detect_season_from_files(files)
                if season:
                    success_echo(f"✅ Detected season {season}")
                else:
                    error_echo("❌ Could not auto-detect season. Please specify with -n")
                    return
        else:
            highlight_echo(f"📺 Using specified season: {season}")
            
            # If we have season mapping, get files from specific season
            if season_mapping and season in season_mapping:
                season_info = season_mapping[season]
                files = season_info['files']
                season_path = season_info['path']
                info_echo(f"📁 Using files from Season {season} folder")
                
                # Auto-detect episode format for this season
                season_double = detect_episode_format(files)
                if season_double:
                    highlight_echo(f"🎬 Detected double episodes format for Season {season}")
                else:
                    highlight_echo(f"🎬 Detected single episodes format for Season {season}")
                
                # Use season-specific format detection, but allow manual override
                use_double = double if double is not None else season_double
            elif season_mapping:
                error_echo(f"❌ Season {season} not found. Available seasons:")
                for season_num in sorted(season_mapping.keys()):
                    highlight_echo(f"   -n {season_num}")
                return
            else:
                # Single season mode, use manual flag
                use_double = double

        # Find show URL
        show_url = find_show_on_imdb(show)
        if not show_url:
            error_echo("❌ Failed to find show on IMDB. Exiting.")
            return
        
        titles = get_episode_titles(show_url, season)
        
        if not titles:
            return
        
        if verbose:
            info_echo(f"🔍 Generating mapping with {len(files)} files, {len(titles)} titles, double={use_double}")
        mapping = generate_mapping(files, titles, use_double)
        if verbose:
            info_echo(f"📝 Generated mapping with {len(mapping)} entries")

        missing_titles = sum(1 for new in mapping.values() if not new)
        if missing_titles > 0:
            warning_echo(f"⚠️ Missing titles for {missing_titles} files")
            dump_config(mapping, path)
            return

        if save_config:
            # Save configuration to file
            dump_config(mapping, path, config_file)
            return

        if verbose:
            preview_changes(mapping)
        
        if not preview:
            if yes or click.confirm("\nRename files?"):
                apply_mapping(mapping, path)
            else:
                warning_echo("❌ Cancelled.")

if __name__ == "__main__":
    main()