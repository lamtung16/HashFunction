import csv
import re

def parse_id_list(s):
    if not s or s.strip() == "[]":
        return []
    return re.findall(r'\d+', s)

# Load sources.csv into dict keyed by server_id
sources = {}
with open("sources.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sources[row["server_id"]] = row

# Prepare output
m3u_lines = ['#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"\n']

# Read channels.csv
with open("channels.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        group = row["group"]
        channel = row["channel"]
        tvg_id = row["tvg_id"]

        for source_name in reader.fieldnames[3:]:
            ids = parse_id_list(row[source_name])
            if not ids:
                continue
            
            src = sources[source_name]
            host = src["host"]
            username = src["username"]
            password = src["password"]
            url_format = src["url_format"]
            
            for cid in ids:
                url = url_format.format(host=host, username=username, password=password,channel_id=cid)                
                extinf = (f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{group}", {channel} ({source_name[0]})')
                m3u_lines.append(extinf)
                m3u_lines.append(url)
                m3u_lines.append("")

# Write output file
with open("list.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(m3u_lines))




import re
import urllib.request

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/categories/sports.m3u"
LOCAL_FILE = "list.m3u"
TARGET_CHANNELS = [
    "Canal+ Sport SK", 
    "Canal+ Sport 2 SK",
    "Canal+ Sport 3 SK",
    "Canal+ Sport 4 SK",
    "Canal+ Sport 5 SK",
    "Canal+ Sport 6 SK",
    "Canal+ Sport 7 SK",
    "Canal+ Sport 8 SK",
    "ESPN (Brazil) (1080p)",
    "ESPN Latin America (1080p)",
    "Setanta Sports 1 Eurasia (1080p)",
]
NEW_GROUP_TITLE = "Extra"


def fetch_remote_playlist(url):
    """Downloads and decodes the remote M3U file."""
    print(f"Downloading playlist from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        return response.read().decode("utf-8")


def set_group_title(extinf_line, group_name):
    """Updates or adds the group-title attribute in an #EXTINF line."""
    if 'group-title="' in extinf_line:
        return re.sub(
            r'group-title="[^"]*?"', f'group-title="{group_name}"', extinf_line
        )
    else:
        return extinf_line.replace("#EXTINF:", f'#EXTINF:-1 group-title="{group_name}",', 1)


def parse_and_extract_channels(playlist_content, target_names, group_name):
    """Parses M3U content, extracts entries matching target names, and updates their group title."""
    lines = playlist_content.splitlines()
    extracted_entries = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            for name in target_names:
                if name.lower() in line.lower():
                    # Scan ahead, skipping any intermediate directive/option lines (starting with '#') 
                    # until we find the stream URL line.
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith("#"):
                        j += 1
                    
                    if j < len(lines):
                        # Collect the #EXTINF line, any intermediate lines, and the stream URL
                        entry_lines = [set_group_title(line, group_name)]
                        for k in range(i + 1, j + 1):
                            entry_lines.append(lines[k])
                        
                        extracted_entries.append("\n".join(entry_lines))
                        print(f"Found channel: {name}")
                    break
        i += 1

    return extracted_entries


def append_to_local_playlist(filename, entries):
    """Appends the extracted entries to the local M3U file."""
    if not entries:
        print("No matching channels found to add.")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    with open(filename, "a", encoding="utf-8") as f:
        if not content.strip():
            f.write("#EXTM3U\n")
            print(f"Initialized new {filename} with #EXTM3U header.")

        for entry in entries:
            f.write("\n" + entry + "\n")


try:
    playlist_content = fetch_remote_playlist(SOURCE_URL)
    matched_entries = parse_and_extract_channels(
        playlist_content, TARGET_CHANNELS, NEW_GROUP_TITLE
    )
    append_to_local_playlist(LOCAL_FILE, matched_entries)
except Exception as e:
    print(f"An error occurred: {e}")