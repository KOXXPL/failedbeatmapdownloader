import re
import shutil
import sys
import time
import webbrowser
import os
import urllib.request
import platform
from pathlib import Path
from threading import Thread
from queue import Queue

# Paths
failed_folder = Path(__file__).parent / "failed"
downloads_folder = Path(__file__).parent / "downloads"
downloading_file = Path(__file__).parent / "downloading.txt"

# Platform detection
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"

# Ensure the failed folder exists
if not failed_folder.exists():
    failed_folder.mkdir(parents=True, exist_ok=True)

# Ensure the downloads folder exists
if not downloads_folder.exists():
    downloads_folder.mkdir(parents=True, exist_ok=True)

def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    os.system('cls' if IS_WINDOWS else 'clear')

def get_single_key_input(timeout=None):
    """
    Get a single key input in a cross-platform way.
    Returns the key character or None if timeout expires.
    """
    if IS_WINDOWS:
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                return key.decode('utf-8', errors='ignore')
            except:
                return None
        return None
    else:
        # For Linux/Unix, use stdin with timeout
        import select
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None

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
    """Get user menu selection with timeout and keyboard support (cross-platform)."""
    selected = 0
    source_names = ["BeatConnect", "Nerinyan"]
    
    display_menu(selected)
    start_time = time.time()
    
    # Enable non-blocking input on Linux
    if not IS_WINDOWS:
        import tty
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
        except:
            pass
    
    try:
        while True:
            remaining = timeout - (time.time() - start_time)
            
            if remaining <= 0:
                print("\nAuto-selecting: BeatConnect (default)")
                return 0
            
            # Display status
            sys.stdout.write(f"\rPress 1-2 or arrows, then Enter to confirm. Auto-selecting in {int(remaining)}s...")
            sys.stdout.flush()
            
            # Check for input
            if IS_WINDOWS:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    try:
                        key_char = key.decode('utf-8', errors='ignore')
                    except:
                        key_char = None
                    
                    if key_char == '1':
                        print("\n")
                        return 0
                    elif key_char == '2':
                        print("\n")
                        return 1
                    elif key_char in ('\r', '\n'):
                        print("\n")
                        return selected
                    elif key == b'\xe0':  # Arrow key prefix on Windows
                        next_key = msvcrt.getch()
                        if next_key == b'H':  # Up arrow
                            selected = (selected - 1) % 2
                            clear_screen()
                            display_menu(selected)
                        elif next_key == b'P':  # Down arrow
                            selected = (selected + 1) % 2
                            clear_screen()
                            display_menu(selected)
            else:
                # Linux/Unix input handling
                import select
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    char = sys.stdin.read(1)
                    if char == '1':
                        print("\n")
                        return 0
                    elif char == '2':
                        print("\n")
                        return 1
                    elif char in ('\r', '\n'):
                        print("\n")
                        return selected
                    elif char == '\x1b':  # Escape sequence for arrow keys
                        # Read the rest of the escape sequence
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            char = sys.stdin.read(1)
                            if char == '[':
                                if select.select([sys.stdin], [], [], 0.1)[0]:
                                    char = sys.stdin.read(1)
                                    if char == 'A':  # Up arrow
                                        selected = (selected - 1) % 2
                                        clear_screen()
                                        display_menu(selected)
                                    elif char == 'B':  # Down arrow
                                        selected = (selected + 1) % 2
                                        clear_screen()
                                        display_menu(selected)
            
            time.sleep(0.05)
    finally:
        # Restore terminal settings on Linux
        if not IS_WINDOWS:
            try:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass

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
    min_file_size = 30720  # 30 KB in bytes
    
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
                print(f" - File too small ({file_size} bytes), likely IP-blocked. Deleting...")
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
    
    # Auto-close countdown (cross-platform)
    countdown = 10
    start_time = time.time()
    
    # Enable non-blocking input on Linux for countdown
    if not IS_WINDOWS:
        import tty
        import termios
        old_settings = None
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except:
            pass
    
    try:
        while countdown > 0:
            remaining = 10 - int(time.time() - start_time)
            if remaining <= 0:
                break
            
            sys.stdout.write(f"\rClosing in {remaining} seconds... (press any key to exit now)")
            sys.stdout.flush()
            
            # Check for key press
            key_pressed = False
            if IS_WINDOWS:
                import msvcrt
                if msvcrt.kbhit():
                    msvcrt.getch()
                    key_pressed = True
            else:
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    try:
                        sys.stdin.read(1)
                        key_pressed = True
                    except:
                        pass
            
            if key_pressed:
                break
            
            time.sleep(0.1)
    finally:
        # Restore terminal settings on Linux
        if not IS_WINDOWS and old_settings:
            try:
                import termios
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except:
                pass
        print("\n")
