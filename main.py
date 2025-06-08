import re
import shutil
import time
import webbrowser
from pathlib import Path

# Paths
failed_folder = Path(__file__).parent / "failed"
downloading_file = Path(__file__).parent / "downloading.txt"

# Ensure the failed folder exists
if not failed_folder.exists():
    failed_folder.mkdir(parents=True, exist_ok=True)

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

# Save all numbers to downloading.txt (sorted)
numbers_sorted = [str(num) for num, _ in osz_files]
with open(downloading_file, "w") as f:
    f.write("\n".join(numbers_sorted))

total = len(osz_files)
progress_bar_length = 30  # Length of the progress bar in characters
for idx, (number, file) in enumerate(osz_files, 1):
    url = f"https://api.nerinyan.moe/d/{number}"
    percent = int((idx / total) * 100) if total else 100
    num_hashes = int((idx / total) * progress_bar_length) if total else progress_bar_length
    num_dots = progress_bar_length - num_hashes
    progress_bar = f"[{'#' * num_hashes}{'.' * num_dots}]"
    print(f"Opening: {url}")
    print(f"Status: {idx}/{total} downloaded {progress_bar} {percent}%")
    webbrowser.open(url)

    # Wait for download to start (adjust as needed)
    time.sleep(5)

    # Wait a bit before next download
    time.sleep(2)

# Clear the downloading.txt file after all downloads
with open(downloading_file, "w") as f:
    f.write("")