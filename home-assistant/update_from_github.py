#!/usr/bin/env python3
"""
Auto-update Ashkelon Surf Sensor from GitHub
Usage: python3 update_from_github.py
"""

import os
import sys
import shutil
import urllib.request
from datetime import datetime
from pathlib import Path

# Configuration
GITHUB_REPO = "avielj/ashkelon-surf-report"
GITHUB_BRANCH = "main"
COMPONENT_NAME = "ashkelon_surf"
HA_CONFIG_DIR = os.environ.get("HA_CONFIG_DIR", "/config")

# Files to update
FILES = ["sensor.py", "__init__.py", "manifest.json"]
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/home-assistant"

def print_colored(message, color=""):
    """Print colored message"""
    colors = {
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[1;33m",
        "blue": "\033[0;34m",
        "reset": "\033[0m"
    }
    color_code = colors.get(color, "")
    reset_code = colors["reset"] if color else ""
    print(f"{color_code}{message}{reset_code}")

def main():
    print("🌊 Ashkelon Surf Sensor - Auto Updater")
    print("=" * 40)
    print()
    
    # Paths
    custom_components_dir = Path(HA_CONFIG_DIR) / "custom_components" / COMPONENT_NAME
    
    # Check if component exists
    if not custom_components_dir.exists():
        print_colored(f"❌ Component not found at: {custom_components_dir}", "red")
        print_colored("Please install the component first.", "yellow")
        sys.exit(1)
    
    print_colored(f"📍 Found component at: {custom_components_dir}", "green")
    print()
    
    # Create backup
    backup_dir = Path(HA_CONFIG_DIR) / "backups" / f"ashkelon_surf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print("💾 Creating backup...")
    try:
        shutil.copytree(custom_components_dir, backup_dir / COMPONENT_NAME)
        print_colored(f"✅ Backup saved to: {backup_dir}", "green")
    except Exception as e:
        print_colored(f"❌ Failed to create backup: {e}", "red")
        sys.exit(1)
    
    print()
    
    # Download files
    print("📥 Downloading latest version from GitHub...")
    
    all_success = True
    for file in FILES:
        print(f"  ⬇️  Downloading {file}...")
        url = f"{BASE_URL}/{file}"
        target_file = custom_components_dir / file
        
        try:
            urllib.request.urlretrieve(url, target_file)
            print_colored(f"  ✓ {file} updated", "green")
        except Exception as e:
            print_colored(f"  ✗ Failed to download {file}: {e}", "red")
            all_success = False
            break
    
    print()
    
    if all_success:
        print_colored("✅ All files updated successfully!", "green")
        print()
        print_colored("⚠️  Please restart Home Assistant for changes to take effect.", "yellow")
        print()
        print("Restart command:")
        print("  ha core restart")
        print()
        print(f"Backup location: {backup_dir}")
        print()
        print("To rollback if needed:")
        print(f"  rm -rf {custom_components_dir}")
        print(f"  cp -r {backup_dir}/{COMPONENT_NAME} {custom_components_dir}")
        print("  ha core restart")
    else:
        print_colored("❌ Update failed! Rolling back...", "red")
        try:
            shutil.rmtree(custom_components_dir)
            shutil.copytree(backup_dir / COMPONENT_NAME, custom_components_dir)
            print_colored("✅ Rollback successful", "green")
        except Exception as e:
            print_colored(f"❌ Rollback failed: {e}", "red")
            print_colored(f"Please manually restore from: {backup_dir}", "yellow")
        sys.exit(1)
    
    print()

if __name__ == "__main__":
    main()
