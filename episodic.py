#!/usr/bin/env python3

import os
import re
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import click

CONFIG_FILENAME = "rename_config.txt"
SUPPORTED_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}

def get_episode_titles(show, season):
    search_url = f"https://www.imdb.com/find/?q={quote(show)}&s=tt&ttype=tv"
    
    try:
        click.echo(f"🔍 Searching for '{show}' on IMDB...")
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
            click.echo("❌ No search results found")
            click.echo("🔧 Try a different show name or check spelling")
            return []
        
        click.echo(f"🔍 Found {len(results)} search results")
        
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
                    
                    click.echo(f"✅ Found show: {show_url}")
                    break
        
        if not show_url:
            click.echo("❌ No valid show found in results")
            return []
        
        # Get episodes for the season
        episodes_url = f"{show_url}episodes/?season={season}"
        click.echo(f"🔍 Getting episodes for season {season}...")
        
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
            click.echo(f"✅ Found {len(titles)} episode titles")
            return titles[:50]  # Limit to reasonable number
        else:
            click.echo("❌ No episodes found for this season")
            click.echo("🔧 Try checking if the season number is correct")
            return []
            
    except requests.RequestException as e:
        click.echo(f"❌ Network error: {e}")
        return []
    except Exception as e:
        click.echo(f"❌ Parsing error: {e}")
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

def generate_mapping(files, titles, double=False):
    mapping = {}
    ep = 1
    
    for f in files:
        ext = os.path.splitext(f)[1]
        
        if double:
            if ep < len(titles):
                new_name = f"Episode {ep:02d}-{ep+1:02d} - {titles[ep-1]} + {titles[ep]}{ext}"
                ep += 2
            else:
                new_name = ""
            mapping[f] = new_name
        else:
            if ep <= len(titles):
                new_name = f"Episode {ep:02d} - {titles[ep-1]}{ext}"
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
    
    if filename == CONFIG_FILENAME:
        click.echo(f"⚠️ Not enough titles. Config saved to {cfg_path}")
        click.echo("📝 Edit the file and run again with -c")
    else:
        click.echo(f"💾 Configuration saved to: {cfg_path}")
        click.echo(f"📝 Edit the file and run: episodic -p {path} -c {filename}")

def load_config(config_path):
    if not os.path.exists(config_path):
        click.echo(f"❌ Config file not found: {config_path}")
        return {}
    
    mapping = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if "->" not in line:
                click.echo(f"⚠️ Skipped line {line_num}: wrong format")
                continue
            
            parts = line.split("->", 1)
            if len(parts) != 2:
                click.echo(f"⚠️ Skipped line {line_num}: wrong format")
                continue
            
            old = parts[0].strip()
            new = parts[1].strip()
            mapping[old] = new
    
    return mapping

def apply_mapping(mapping, folder):
    success_count = 0
    skip_count = 0
    
    for old, new in mapping.items():
        if not new:
            click.echo(f"⚠️ Skipped: {old} (no new name)")
            skip_count += 1
            continue
        
        old_path = os.path.join(folder, old)
        new_path = os.path.join(folder, new)
        
        if not os.path.exists(old_path):
            click.echo(f"❌ File not found: {old}")
            continue
        
        if os.path.exists(new_path):
            click.echo(f"❌ File already exists: {new}")
            continue
        
        try:
            click.echo(f"📝 {old} -> {new}")
            os.rename(old_path, new_path)
            success_count += 1
        except OSError as e:
            click.echo(f"❌ Error renaming {old}: {e}")
    
    click.echo(f"\n✅ Done! Renamed: {success_count}, skipped: {skip_count}")

def preview_changes(mapping):
    click.echo("\n📋 Proposed changes:")
    click.echo("-" * 60)
    
    for old, new in mapping.items():
        if not new:
            click.echo(f"⚠️  {old} -> SKIPPED")
        else:
            click.echo(f"📝  {old}")
            click.echo(f"    -> {new}")
        click.echo()
    
    click.echo("-" * 60)

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-p', '--path', required=True, help='Path to folder with episodes')
@click.option('-s', '--show', help='Show name (as on IMDB)')
@click.option('-n', '--season', type=int, help='Season number (auto-detected if not specified)')
@click.option('-d', '--double', is_flag=True, help='Flag for double episodes (one file = two episodes)')
@click.option('-c', '--config', help='Use existing config file for renaming')
@click.option('-v', '--preview', is_flag=True, help='Only show changes without applying')
@click.option('--save-config', help='Save configuration to file without applying changes')
@click.version_option(version='1.0.0')
def main(path, show, season, double, config, preview, save_config):
    """episodic - TV Series File Renamer

Automatically rename TV series files using episode titles from IMDB.

Examples:\n
    episodic -p /path/to/episodes -s "Breaking Bad" -n 1\n
    episodic -p /path/to/episodes -s "Breaking Bad" -n 1 -d\n
    episodic -p /path/to/episodes -s "Breaking Bad"  # Auto-detect season\n
    episodic -p /path/to/episodes -c rename_config.txt\n
    episodic -p /path/to/episodes -s "Breaking Bad" --save-config my_config.txt\n
"""
    
    files = get_video_files(path)
    if not files:
        click.echo("❌ No video files found in specified folder")
        return
    
    click.echo(f"📁 Found {len(files)} video files")

    if config:
        mapping = load_config(config)
        if not mapping:
            return
        
        if save_config:
            # Save configuration to file
            dump_config(mapping, path, save_config)
            return
        
        preview_changes(mapping)
        
        if not preview:
            if click.confirm("\nRename files?"):
                apply_mapping(mapping, path)
            else:
                click.echo("❌ Cancelled.")
    else:
        if not show:
            click.echo("❌ Need to specify --show, or --config")
            return
        
        # Auto-detect season if not specified
        if not season:
            click.echo("🔍 Auto-detecting season number from file names...")
            season = detect_season_from_files(files)
            if season:
                click.echo(f"✅ Detected season {season}")
            else:
                click.echo("❌ Could not auto-detect season. Please specify with -n")
                return
        else:
            click.echo(f"📺 Using specified season: {season}")

        titles = get_episode_titles(show, season)
        
        if not titles:
            return
        
        mapping = generate_mapping(files, titles, double)

        missing_titles = sum(1 for new in mapping.values() if not new)
        if missing_titles > 0:
            click.echo(f"⚠️ Missing titles for {missing_titles} files")
            dump_config(mapping, path)
            return

        if save_config:
            # Save configuration to file
            dump_config(mapping, path, save_config)
            return

        preview_changes(mapping)
        
        if not preview:
            if click.confirm("\nRename files?"):
                apply_mapping(mapping, path)
            else:
                click.echo("❌ Cancelled.")

if __name__ == "__main__":
    main()