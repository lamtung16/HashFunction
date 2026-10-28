import urllib.request

# Configuration
SOURCE_URL = "https://iptv-org.github.io/iptv/categories/sports.m3u"
LOCAL_FILE = "list.m3u"
TARGET_CHANNELS = ["Canal+ Sport SK", "Canal+ Sport 2 SK"]


def fetch_remote_playlist(url):
  """Downloads and decodes the remote M3U file."""
  print(f"Downloading playlist from {url}...")
  req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  with urllib.request.urlopen(req) as response:
    return response.read().decode("utf-8")


def parse_and_extract_channels(playlist_content, target_names):
  """Parses M3U content and extracts entries matching the target channel names."""
  lines = playlist_content.splitlines()
  extracted_entries = []

  i = 0
  while i < len(lines):
    line = lines[i]
    # Check if the line is an M3U metadata entry (#EXTINF)
    if line.startswith("#EXTINF"):
      # Look for channel name in the metadata line
      for name in target_names:
        if name.lower() in line.lower():
          # The next line is typically the stream URL
          if i + 1 < len(lines):
            stream_url = lines[i + 1]
            extracted_entries.append(f"{line}\n{stream_url}\n")
            print(f"Found channel: {name}")
          break
    i += 1

  return extracted_entries


def append_to_local_playlist(filename, entries):
  """Appends the extracted entries to the local M3U file."""
  if not entries:
    print("No matching channels found to add.")
    return

  # Ensure the file starts with the M3U header if it's new or empty
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
      f.write(entry + "\n")

  print(f"Successfully added {len(entries)} channels to {filename}.")


def main():
  try:
    playlist_content = fetch_remote_playlist(SOURCE_URL)
    matched_entries = parse_and_extract_channels(
        playlist_content, TARGET_CHANNELS
    )
    append_to_local_playlist(LOCAL_FILE, matched_entries)
  except Exception as e:
    print(f"An error occurred: {e}")


if __name__ == "__main__":
  main()