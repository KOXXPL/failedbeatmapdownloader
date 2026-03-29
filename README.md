# Beatmap Downloader

This utility automates the process of re-downloading osu! beatmaps by directly downloading them from your choice of source. It intelligently handles bot-blocks and avoids re-downloading files that already exist.

## Important: Folder Setup

**This script creates and manages its own files and folders. It is recommended to keep it in a dedicated folder separate from other files.**

The script will automatically create and use the following folders and files after being opened for the first time:
- `failed/` - Place your failed `.osz` files here
- `downloads/` - Downloaded beatmaps are saved here
- `downloading.txt` - Tracks download progress (auto-cleared after completion)

## How It Works

1. **Setup:**
   - Place the `failedbeatmapdownloader.py` script in a dedicated folder
   - The script will automatically create the `failed` and `downloads` folders if they don't exist

2. **Add Failed Beatmaps:**
   - Place all failed `.osz` files in the `failed` folder
   - In osu!, the failed import folder is located in the Songs directory and is named `failed`
   - The program extracts numeric beatmap IDs from filenames and sorts them

3. **Choose Download Source:**
   - The program displays a menu with two options:
     - **Option 1: BeatConnect** (`https://beatconnect.io/b/`)
     - **Option 2: Nerinyan** (`https://api.nerinyan.moe/d/`)
   - **Default:** BeatConnect is auto-selected after 5 seconds of no input
   - **Navigation:** 
     - Press `1` or `2` to select directly
     - Use **arrow keys** to navigate and **Enter** to confirm
     - Any key press stops the countdown

4. **Download Process:**
   - The program downloads beatmaps directly to the `downloads` folder
   - **Progress Tracking:** Real-time visual progress bar showing download completion percentage
   - **Bot-Block Detection:** Files smaller than 20KB are detected as likely IP-blocked and automatically deleted
   - **Duplicate Avoidance:** Files that already exist in the `downloads` folder and are valid (≥20KB) are skipped
   - A delay of 1 second is added between downloads

5. **Download Summary:**
   - After all downloads complete, displays a color-coded summary:
     - **Succeeded**: Total valid files (downloaded + skipped) shown in green
     - **Failed**: Count of IP-blocked files shown in red
   - **Auto-Close:** The window automatically closes after 10 seconds
     - Press any key to exit immediately without waiting

6. **Handling IP Blocks:**
   - **What are IP blocks?** The download services use IP-based rate limiting to prevent bot abuse. Downloads smaller than 20KB indicate your IP has been temporarily blocked.
   - **BeatConnect:** Simply changing your IP address will bypass the block. You can use:
     - A VPN service
     - Reconnecting your router (if you have a dynamic IP)
     - A proxy service
   - **Nerinyan:** IP blocks typically only result in slower download speeds rather than complete blocking. Downloads should still complete, just more slowly.

7. **Cleanup:**
   - The `downloading.txt` file is cleared after the process completes

## Usage

1. Ensure Python 3 is installed on your system
2. Create a dedicated folder for this script
3. Place `main.py` in that folder
4. Place your failed `.osz` files in the `failed` folder (auto-created on first run)
5. Run the script:
   ```sh
   python main.py
   ```
6. Select your preferred download source
7. Wait for downloads to complete and check the results in the `downloads` folder

## Notes
- Adjust the 1-second delay between downloads in the script if needed (change `time.sleep(1)` value)
- The script validates downloaded files and automatically handles IP-blocked attempts
- Skipped files (already downloaded and valid) count toward your success total
- The script is safe to run multiple times; existing valid files won't be re-downloaded
- If you experience multiple failures, consider using a VPN or changing your IP address to bypass rate limiting

## Requirements
- Python 3.x
- Internet connection

---

You may modify the script to better suit your workflow as needed.
