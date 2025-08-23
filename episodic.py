import os
import argparse
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote

CONFIG_FILENAME = "rename_config.txt"
SUPPORTED_EXTENSIONS = {'.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'}

def get_episode_titles(show, season):
    search_url = f"https://www.imdb.com/find/?q={quote(show)}&s=tt&ttype=tv"
    
    try:
        print(f"🔍 Searching for '{show}' on IMDB...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = soup.find_all("td", class_="result_text")
        if not results:
            print("❌ No search results found")
            return []
        
        show_url = None
        for result in results[:3]:
            link = result.find("a")
            if link and "/title/" in link.get("href", ""):
                show_url = "https://www.imdb.com" + link["href"]
                break
        
        if not show_url:
            print("❌ No valid show found")
            return []
        
        print(f"✅ Found show: {show_url}")
        
        episodes_url = f"{show_url}episodes?season={season}"
        print(f"🔍 Getting episodes for season {season}...")
        
        response = requests.get(episodes_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        titles = []
        episode_items = soup.find_all("div", class_="info")
        
        for item in episode_items:
            title_link = item.find("strong").find("a") if item.find("strong") else None
            if title_link:
                title = title_link.get_text(strip=True)
                if title:
                    titles.append(title)
        
        if titles:
            print(f"✅ Found {len(titles)} episode titles")
            return titles
        else:
            print("❌ No episodes found for this season")
            return []
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return []

def get_video_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"❌ Folder does not exist: {folder_path}")
        return []
    
    files = []
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                files.append(f)
    
    return sorted(files)

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

def dump_config(mapping, path):
    cfg_path = os.path.join(path, CONFIG_FILENAME)
    with open(cfg_path, "w", encoding="utf-8") as f:
        f.write("# Configuration for file renaming\n")
        f.write("# Format: old_file -> new_file\n")
        f.write("# Leave empty after -> to skip file\n\n")
        
        for old, new in mapping.items():
            f.write(f"{old} -> {new}\n")
    
    print(f"⚠️ Not enough titles. Config saved to {cfg_path}")
    print("📝 Edit the file and run again with --config")

def load_config(config_path):
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return {}
    
    mapping = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if "->" not in line:
                print(f"⚠️ Skipped line {line_num}: wrong format")
                continue
            
            parts = line.split("->", 1)
            if len(parts) != 2:
                print(f"⚠️ Skipped line {line_num}: wrong format")
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
            print(f"⚠️ Skipped: {old} (no new name)")
            skip_count += 1
            continue
        
        old_path = os.path.join(folder, old)
        new_path = os.path.join(folder, new)
        
        if not os.path.exists(old_path):
            print(f"❌ File not found: {old}")
            continue
        
        if os.path.exists(new_path):
            print(f"❌ File already exists: {new}")
            continue
        
        try:
            print(f"📝 {old} -> {new}")
            os.rename(old_path, new_path)
            success_count += 1
        except OSError as e:
            print(f"❌ Error renaming {old}: {e}")
    
    print(f"\n✅ Done! Renamed: {success_count}, skipped: {skip_count}")

def preview_changes(mapping, folder):
    print("\n📋 Proposed changes:")
    print("-" * 60)
    
    for old, new in mapping.items():
        if not new:
            print(f"⚠️  {old} -> SKIPPED")
        else:
            print(f"📝  {old}")
            print(f"    -> {new}")
        print()
    
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="episodic - TV Series File Renamer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -p /path/to/episodes -s "Breaking Bad" -n 1
  %(prog)s -p /path/to/episodes -s "Breaking Bad" -n 1 -d
  %(prog)s -p /path/to/episodes --config rename_config.txt
        """
    )
    
    parser.add_argument("-p", "--path", required=True, 
                       help="Path to folder with episodes")
    parser.add_argument("-s", "--show", 
                       help="Show name (as on IMDB)")
    parser.add_argument("-n", "--season", type=int, 
                       help="Season number")
    parser.add_argument("-d", "--double", action="store_true", 
                       help="Flag for double episodes (one file = two episodes)")
    parser.add_argument("--config", 
                       help="Use existing config file for renaming")
    parser.add_argument("--preview", action="store_true",
                       help="Only show changes without applying")
    
    args = parser.parse_args()

    files = get_video_files(args.path)
    if not files:
        print("❌ No video files found in specified folder")
        return
    
    print(f"📁 Found {len(files)} video files")

    if args.config:
        mapping = load_config(args.config)
        if not mapping:
            return
        
        preview_changes(mapping, args.path)
        
        if not args.preview:
            confirm = input("\nRename files? (y/n): ")
            if confirm.lower() in ['y', 'yes']:
                apply_mapping(mapping, args.path)
            else:
                print("❌ Cancelled.")
    else:
        if not args.show or not args.season:
            print("❌ Need to specify --show and --season, or --config")
            return

        titles = get_episode_titles(args.show, args.season)
        
        if not titles:
            return
        
        mapping = generate_mapping(files, titles, args.double)

        missing_titles = sum(1 for new in mapping.values() if not new)
        if missing_titles > 0:
            print(f"⚠️ Missing titles for {missing_titles} files")
            dump_config(mapping, args.path)
            return

        preview_changes(mapping, args.path)
        
        if not args.preview:
            confirm = input("\nRename files? (y/n): ")
            if confirm.lower() in ['y', 'yes']:
                apply_mapping(mapping, args.path)
            else:
                print("❌ Cancelled.")

if __name__ == "__main__":
    main()
