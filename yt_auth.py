import json
import os
import sys
from ytmusicapi import setup

def main():
    print("=" * 60)
    print("YouTube Music Browser Authentication Setup")
    print("=" * 60)
    print("Instructions:")
    print("1. Open Chrome/Firefox/Edge and go to https://music.youtube.com (logged in).")
    print("2. Open Developer Tools (F12) -> Network tab.")
    print("3. Click any song or playlist, or refresh the page.")
    print("4. Find a request to music.youtube.com (e.g. 'browse' or 'next').")
    print("5. Right-click it -> Copy -> Copy request headers.")
    print("6. Run this script and paste the copied headers, then press Enter and Ctrl+D (EOF).\n")
    
    try:
        setup(filepath="browser.json")
        print("\n✅ Successfully generated browser.json!")
    except Exception as e:
        print(f"\n❌ Error setting up authentication: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
