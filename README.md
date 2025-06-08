# Beatmap Downloader

This utility automates the process of re-downloading failed osu! beatmap files by opening their download links in the default web browser. It is intended to assist users in efficiently retrying downloads for beatmaps that previously failed to import.

## How It Works

1. **Failed Beatmaps Folder:**
   - Place all failed `.osz` files in the `failed` folder, located in the same directory as `main.py`. In osu!, the failed import folder is found in the Songs directory and is named `failed`. If you do not have a `failed` folder, it means none of your imports have failed.

2. **Extracting Beatmap IDs:**
   - The program scans the `failed` folder for `.osz` files and extracts the numeric beatmap IDs from their filenames.
   - The IDs are sorted in ascending order.

3. **Download List:**
   - All sorted beatmap IDs are written to `downloading.txt` prior to initiating the download process.

4. **Automated Download:**
   - For each beatmap ID, the program opens the corresponding download URL (`https://api.nerinyan.moe/d/{id}`) in the default web browser.
   - A status bar is displayed in the terminal, showing the current progress as a hash-based progress bar, the number of downloads completed, and the percentage finished.
   - The program waits a few seconds between each download to allow the browser to initiate the download.

5. **Cleanup:**
   - After all downloads are attempted, the `downloading.txt` file is cleared.

## Usage

1. Ensure Python 3 is installed on your system.
2. Place your failed `.osz` files in the `failed` folder.
3. Run the script:
   ```sh
   python main.py
   ```
4. The browser will automatically open each download link in sequence.

## Notes
- Adjust the sleep durations in the script if your downloads start too slowly or too quickly.
- The script does not verify if the downloads succeed; it simply opens the links.
- The `downloading.txt` file is used for tracking and is cleared after the script completes.

## Requirements
- Python 3.x
- A web browser installed and set as default, with a configured default download location

---

You may modify the script to better suit your workflow as needed.
