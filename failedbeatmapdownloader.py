import re
import shutil
import sys
import time
import webbrowser
import os
import urllib.request
from pathlib import Path

# Paths
failed_folder = Path(__file__).parent / "failed"
downloads_folder = Path(__file__).parent / "downloads"
downloading_file = Path(__file__).parent / "downloading.txt"

# Ensure the failed folder exists
if not failed_folder.exists():
    failed_folder.mkdir(parents=True, exist_ok=True)

# Ensure the downloads folder exists
if not downloads_folder.exists():
    downloads_folder.mkdir(parents=True, exist_ok=True)

def display_menu(selected=0):
    """Display the download source menu."""
    sources = [
        "BeatConnect (https://beatconnect.io/b/)",
        "Nerinyan (https://api.nerinyan.moe/d/)"
    ]
    
    print("\n" + "="*60)
    print("Choose a download source:")
    print("="*60)
    
    for i, source in enumerate(sources):
        marker = "► " if i == selected else "  "
        key = str(i + 1)
        print(f"{marker}[{key}] {source}")
    
    print("="*60)

def download_beatmap(url, beatmap_id, progress_callback=None):
    """Download a beatmap from the given URL with progress tracking."""
    try:
        filename = downloads_folder / f"{beatmap_id}.osz"
        
        def report_hook(blocknum, blocksize, totalsize):
            """Hook for tracking download progress."""
            if totalsize > 0:
                downloaded = blocknum * blocksize
                if downloaded > totalsize:
                    downloaded = totalsize
                progress = downloaded / totalsize
                if progress_callback:
                    progress_callback(progress)
        
        urllib.request.urlretrieve(url, filename, reporthook=report_hook)
        if progress_callback:
            progress_callback(1.0)  # Ensure 100%
        return True
    except Exception as e:
        print(f"\nError downloading {beatmap_id}: {e}")
        return False

def get_menu_selection(timeout=5):
    """Get user menu selection with timeout and arrow key support (Windows)."""
    import msvcrt
    
    selected = 0
    last_selected = 0
    user_interacted = False
    start_time = time.time()
    
    display_menu(selected)
    source_names = ["BeatConnect", "Nerinyan"]
    
    while True:
        if not user_interacted:
            remaining = timeout - (time.time() - start_time)
            
            if remaining <= 0:
                print("Auto-selecting: BeatConnect (default)")
                return selected
            
            sys.stdout.write(f"\rPress 1-2 or use arrow keys, then press Enter. Auto-selecting the recommended option in {int(remaining)}s...")
        else:
            sys.stdout.write(f"\rSelected: {source_names[selected]} | Press Enter to confirm, use arrows to select.")
        
        sys.stdout.flush()
        
        if msvcrt.kbhit():
            user_interacted = True
            key = msvcrt.getch()
            
            try:
                key_char = key.decode('utf-8', errors='ignore')
            except:
                key_char = chr(key[0]) if key else ''
            
            # Numeric keys 1 or 2
            if key_char == '1':
                print("\n")
                return 0
            elif key_char == '2':
                print("\n")
                return 1
            # Enter key
            elif key_char == '\r':
                print("\n")
                return selected
            # Arrow keys (Windows special key sequence)
            elif key == b'\xe0':
                next_key = msvcrt.getch()
                if next_key == b'H':  # Up arrow
                    selected = (selected - 1) % 2
                elif next_key == b'P':  # Down arrow
                    selected = (selected + 1) % 2
                
                # Redraw menu if selection changed
                if selected != last_selected:
                    os.system('cls')
                    display_menu(selected)
                    last_selected = selected
        
        time.sleep(0.05)

# Regex to extract number from filename
number_re = re.compile(r"(\d+)")

# Find all .osz files and extract numbers
osz_files = []
numbers = []
for file in failed_folder.glob("*.osz"):
    match = number_re.search(file.name)
    if match:
        num = int(match.group(1))
        osz_files.append((num, file))
        numbers.append(str(num))

# Sort by number
osz_files.sort()

if not osz_files:
    print("No .osz files found in the 'failed' folder.")
else:
    # Get the selected download source
    selected = get_menu_selection(timeout=5)
    
    base_urls = [
        "https://beatconnect.io/b/",
        "https://api.nerinyan.moe/d/"
    ]
    source_names = ["BeatConnect", "Nerinyan"]
    
    base_url = base_urls[selected]
    source_name = source_names[selected]
    
    print(f"\nUsing {source_name}")
    print(f"Starting to download from: {base_url}\n")
    
    # Save all numbers to downloading.txt (sorted)
    numbers_sorted = [str(num) for num, _ in osz_files]
    with open(downloading_file, "w") as f:
        f.write("\n".join(numbers_sorted))

    total = len(osz_files)
    progress_bar_length = 30  # Length of the progress bar in characters
    downloaded = 0
    skipped = 0
    failed = 0
    min_file_size = 20480  # 20 KB in bytes
    
    for idx, (number, file) in enumerate(osz_files, 1):
        url = f"{base_url}{number}"
        filename = downloads_folder / f"{number}.osz"
        
        # Check if file already exists and is valid
        if filename.exists():
            file_size = filename.stat().st_size
            if file_size >= min_file_size:
                print(f"\nSkipping: {url} (already exists, {file_size} bytes)")
                skipped += 1
                continue
        
        print(f"\nDownloading: {url}")
        
        def make_progress_callback(beatmap_number, list_index, total_count):
            """Create a progress callback for the current download."""
            def callback(progress):
                num_hashes = int(progress * progress_bar_length)
                num_dots = progress_bar_length - num_hashes
                progress_bar = f"[{'#' * num_hashes}{'.' * num_dots}]"
                percent = int(progress * 100)
                sys.stdout.write(f"\rFile {list_index}/{total_count}: {progress_bar} {percent}%")
                sys.stdout.flush()
            return callback
        
        progress_cb = make_progress_callback(number, idx, total)
        download_beatmap(url, number, progress_callback=progress_cb)
        
        # Check file size after download
        if filename.exists():
            file_size = filename.stat().st_size
            if file_size < min_file_size:
                print(f" - File too small ({file_size} bytes), likely bot-blocked. Deleting...")
                filename.unlink()
                failed += 1
            else:
                downloaded += 1
        else:
            failed += 1

        # Wait a bit between downloads
        time.sleep(1)

    # Clear the downloading.txt file after all downloads
    with open(downloading_file, "w") as f:
        f.write("")
    
    # Display summary with colors
    print("\n" + "="*60)
    print("Download Summary:")
    print("="*60)
    
    # ANSI color codes
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    succeeded = downloaded + skipped
    print(f"{GREEN}{BOLD}✓ Succeeded: {succeeded} ({downloaded} downloaded + {skipped} skipped){RESET}")
    print(f"{RED}{BOLD}✗ Failed: {failed}{RESET}")
    print("="*60)
    
    # Auto-close countdown
    import msvcrt
    countdown = 10
    
    start_time = time.time()
    while countdown > 0:
        remaining = 10 - int(time.time() - start_time)
        if remaining <= 0:
            break
        
        sys.stdout.write(f"\rClosing in {remaining} seconds... (press any key to exit now)")
        sys.stdout.flush()
        
        if msvcrt.kbhit():
            msvcrt.getch()
            break
        
        time.sleep(0.1)