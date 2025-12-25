#!/usr/bin/env python3
"""
EVE Online Ship Asset Downloader

Downloads official ship renders from CCP's Image Server for use in Minmatar Rebellion.
These assets are provided by CCP for fan projects under their community license.

Image Server Docs: https://docs.esi.evetech.net/docs/image_server.html
"""

import os
import urllib.request
import urllib.error
import time

# EVE Type IDs for ships used in the game
SHIP_TYPE_IDS = {
    # Minmatar (Player ships)
    'rifter': 587,
    'wolf': 11379,
    'jaguar': 11377,

    # Amarr Frigates
    'executioner': 589,
    'punisher': 597,
    'tormentor': 591,
    'crucifier': 2161,
    'magnate': 29248,
    'inquisitor': 594,

    # Amarr Destroyers
    'coercer': 2015,
    'dragoon': 3756,

    # Amarr Cruisers
    'omen': 2006,
    'maller': 624,
    'arbitrator': 628,
    'augoror': 625,

    # Amarr Battlecruisers
    'harbinger': 24696,
    'prophecy': 24700,

    # Amarr Battleships
    'apocalypse': 642,
    'abaddon': 24690,
    'armageddon': 643,

    # Amarr Industrial
    'bestower': 1944,

    # Amarr HAC/T2
    'zealot': 12003,
    'sacrilege': 12004,

    # Drones
    'drone': 2173,  # Warrior I
    'heavy_drone': 2175,  # Hammerhead I

    # Interceptors
    'interceptor': 11184,  # Crusader

    # Bombers
    'bomber': 12034,  # Purifier
}

# Additional boss/capital ships
CAPITAL_TYPE_IDS = {
    'avatar': 11567,  # Titan
    'archon': 23757,  # Carrier
    'aeon': 23913,   # Supercarrier
    'revelation': 19720,  # Dreadnought
}

def download_ship_render(ship_name, type_id, output_dir, size=512):
    """Download a ship render from CCP's image server"""
    url = f"https://images.evetech.net/types/{type_id}/render?size={size}"
    output_path = os.path.join(output_dir, f"{ship_name}.png")

    # Skip if already exists
    if os.path.exists(output_path):
        print(f"  [SKIP] {ship_name} already exists")
        return True

    try:
        print(f"  [DOWNLOAD] {ship_name} (ID: {type_id})...")
        urllib.request.urlretrieve(url, output_path)
        print(f"  [OK] {ship_name} saved")
        return True
    except urllib.error.URLError as e:
        print(f"  [ERROR] {ship_name}: {e}")
        return False

def download_ship_icon(ship_name, type_id, output_dir, size=64):
    """Download a ship icon from CCP's image server"""
    url = f"https://images.evetech.net/types/{type_id}/icon?size={size}"
    output_path = os.path.join(output_dir, f"{ship_name}_icon.png")

    if os.path.exists(output_path):
        print(f"  [SKIP] {ship_name} icon already exists")
        return True

    try:
        print(f"  [DOWNLOAD] {ship_name} icon...")
        urllib.request.urlretrieve(url, output_path)
        print(f"  [OK] {ship_name} icon saved")
        return True
    except urllib.error.URLError as e:
        print(f"  [ERROR] {ship_name} icon: {e}")
        return False

def main():
    print("=" * 60)
    print("EVE Online Ship Asset Downloader")
    print("Downloading official renders from CCP's Image Server")
    print("=" * 60)

    # Create output directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    renders_dir = os.path.join(base_dir, "assets", "eve_renders")
    icons_dir = os.path.join(base_dir, "assets", "eve_icons")

    os.makedirs(renders_dir, exist_ok=True)
    os.makedirs(icons_dir, exist_ok=True)

    print(f"\nOutput directories:")
    print(f"  Renders: {renders_dir}")
    print(f"  Icons: {icons_dir}")

    # Download regular ships
    print(f"\n--- Downloading {len(SHIP_TYPE_IDS)} ship renders ---")
    success_count = 0
    for ship_name, type_id in SHIP_TYPE_IDS.items():
        if download_ship_render(ship_name, type_id, renders_dir):
            success_count += 1
        time.sleep(0.2)  # Rate limiting

    # Download capital ships
    print(f"\n--- Downloading {len(CAPITAL_TYPE_IDS)} capital ship renders ---")
    for ship_name, type_id in CAPITAL_TYPE_IDS.items():
        if download_ship_render(ship_name, type_id, renders_dir):
            success_count += 1
        time.sleep(0.2)

    # Download icons for player ships
    print("\n--- Downloading player ship icons ---")
    player_ships = ['rifter', 'wolf', 'jaguar']
    for ship_name in player_ships:
        type_id = SHIP_TYPE_IDS[ship_name]
        download_ship_icon(ship_name, type_id, icons_dir)
        time.sleep(0.2)

    total = len(SHIP_TYPE_IDS) + len(CAPITAL_TYPE_IDS)
    print(f"\n{'=' * 60}")
    print(f"Download complete: {success_count}/{total} ships")
    print(f"\nAssets saved to:")
    print(f"  {renders_dir}")
    print(f"\nNote: These are official CCP assets for fan projects.")
    print(f"See: https://developers.eveonline.com/license-agreement")
    print("=" * 60)

if __name__ == "__main__":
    main()
