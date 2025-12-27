#!/usr/bin/env python3
"""
EVE Ship Render Bulk Downloader

Downloads ship renders and icons from the EVE Image Server for local use.

Usage:
    python fetch_ship_renders.py --output ./assets/ships
    python fetch_ship_renders.py --ships 587,593,621 --sizes 64,256
    python fetch_ship_renders.py --all-frigates --output ./ships
"""

import argparse
import asyncio
import httpx
from pathlib import Path
from typing import List, Dict, Optional
import json

# Common ship type IDs organized by class
SHIP_CLASSES = {
    "frigates": {
        "rifter": 587,
        "tristan": 593,
        "merlin": 603,
        "punisher": 597,
        "kestrel": 602,
        "incursus": 594,
        "slasher": 585,
        "condor": 583,
        "executioner": 589,
        "atron": 608,
        "breacher": 598,
        "tormentor": 591,
    },
    "destroyers": {
        "thrasher": 16242,
        "catalyst": 16240,
        "cormorant": 16238,
        "coercer": 16236,
        "talwar": 32872,
        "algos": 32875,
        "corax": 32876,
        "dragoon": 32874,
    },
    "cruisers": {
        "stabber": 622,
        "thorax": 627,
        "caracal": 621,
        "maller": 624,
        "rupture": 629,
        "vexor": 626,
        "moa": 623,
        "omen": 625,
        "bellicose": 630,
        "celestis": 633,
        "blackbird": 632,
        "arbitrator": 628,
    },
    "battlecruisers": {
        "hurricane": 24702,
        "brutix": 16229,
        "drake": 24690,
        "harbinger": 24696,
        "cyclone": 24700,
        "myrmidon": 24700,
        "ferox": 24688,
        "prophecy": 24692,
    },
    "battleships": {
        "tempest": 639,
        "megathron": 641,
        "raven": 638,
        "apocalypse": 642,
        "typhoon": 644,
        "dominix": 645,
        "rokh": 24688,
        "abaddon": 24692,
        "maelstrom": 24694,
        "hyperion": 24690,
        "scorpion": 640,
        "armageddon": 643,
    },
    "faction_battleships": {
        "machariel": 17738,
        "nightmare": 17736,
        "vindicator": 17740,
        "bhaalgorn": 17920,
    },
    "capitals": {
        "naglfar": 19724,
        "moros": 19720,
        "phoenix": 19726,
        "revelation": 19722,
        "archon": 23757,
        "thanatos": 23911,
        "chimera": 23915,
        "nidhoggur": 24483,
    },
    "supercapitals": {
        "hel": 22852,
        "nyx": 23913,
        "wyvern": 23917,
        "aeon": 23919,
        "avatar": 11567,
        "erebus": 671,
        "ragnarok": 11568,
        "leviathan": 3764,
    },
}

# Flatten for easy lookup
ALL_SHIPS: Dict[str, int] = {}
for class_ships in SHIP_CLASSES.values():
    ALL_SHIPS.update(class_ships)

IMAGE_SERVER = "https://images.evetech.net"
VALID_SIZES = [32, 64, 128, 256, 512, 1024]


async def download_image(
    client: httpx.AsyncClient,
    type_id: int,
    variation: str,
    size: int,
    output_dir: Path,
    name: Optional[str] = None
) -> bool:
    """Download a single image from the EVE Image Server."""
    url = f"{IMAGE_SERVER}/types/{type_id}/{variation}?size={size}"
    
    filename = f"{name or type_id}_{variation}_{size}.png"
    output_path = output_dir / filename
    
    if output_path.exists():
        print(f"  ⏭️  Skipped (exists): {filename}")
        return True
    
    try:
        response = await client.get(url, follow_redirects=True)
        
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            print(f"  ✅ Downloaded: {filename}")
            return True
        elif response.status_code == 302:
            print(f"  ⚠️  Not found (placeholder returned): {filename}")
            return False
        else:
            print(f"  ❌ Failed ({response.status_code}): {filename}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {filename} - {e}")
        return False


async def download_ship_set(
    ship_ids: List[int],
    sizes: List[int],
    variations: List[str],
    output_dir: Path,
    names: Optional[Dict[int, str]] = None
):
    """Download images for multiple ships."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📦 Downloading {len(ship_ids)} ships to {output_dir}")
    print(f"   Sizes: {sizes}")
    print(f"   Variations: {variations}")
    print("-" * 40)
    
    total = len(ship_ids) * len(sizes) * len(variations)
    success = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for ship_id in ship_ids:
            name = names.get(ship_id) if names else None
            print(f"\n🚀 {name or ship_id}:")
            
            for variation in variations:
                for size in sizes:
                    if await download_image(client, ship_id, variation, size, output_dir, name):
                        success += 1
                    else:
                        failed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {success} downloaded, {failed} failed, {total} total")
    
    # Save manifest
    manifest = {
        "ships": {names.get(sid, str(sid)): sid for sid in ship_ids} if names else ship_ids,
        "sizes": sizes,
        "variations": variations,
        "total_files": success
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"📝 Manifest saved: {manifest_path}")


def parse_ship_list(ships_str: str) -> List[int]:
    """Parse comma-separated ship IDs or names."""
    result = []
    for item in ships_str.split(","):
        item = item.strip().lower()
        if item.isdigit():
            result.append(int(item))
        elif item in ALL_SHIPS:
            result.append(ALL_SHIPS[item])
        else:
            print(f"⚠️  Unknown ship: {item}")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Download EVE ship renders from the Image Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ships rifter,tristan,caracal --output ./ships
  %(prog)s --all-frigates --sizes 64,256 --output ./frigates  
  %(prog)s --class cruisers --variations render,icon --output ./cruisers
  %(prog)s --all --sizes 512 --output ./all_ships

Available ship classes: frigates, destroyers, cruisers, battlecruisers, 
                        battleships, faction_battleships, capitals, supercapitals
        """
    )
    
    ships_group = parser.add_mutually_exclusive_group(required=True)
    ships_group.add_argument("--ships", type=str, help="Comma-separated ship names or type IDs")
    ships_group.add_argument("--class", dest="ship_class", choices=SHIP_CLASSES.keys(),
                            help="Download all ships in a class")
    ships_group.add_argument("--all-frigates", action="store_true", help="All T1 frigates")
    ships_group.add_argument("--all-cruisers", action="store_true", help="All T1 cruisers")
    ships_group.add_argument("--all", action="store_true", help="All defined ships")
    
    parser.add_argument("--output", "-o", type=Path, default=Path("./eve_ships"),
                       help="Output directory (default: ./eve_ships)")
    parser.add_argument("--sizes", type=str, default="256,512",
                       help="Comma-separated sizes (default: 256,512)")
    parser.add_argument("--variations", type=str, default="render",
                       help="Comma-separated variations: render,icon,bp (default: render)")
    parser.add_argument("--list", action="store_true", help="List available ships and exit")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n📋 Available Ships:\n")
        for class_name, ships in SHIP_CLASSES.items():
            print(f"  {class_name.upper()}:")
            for name, type_id in ships.items():
                print(f"    {name}: {type_id}")
            print()
        return
    
    # Parse sizes
    sizes = [int(s.strip()) for s in args.sizes.split(",")]
    for s in sizes:
        if s not in VALID_SIZES:
            print(f"⚠️  Invalid size {s}, using valid sizes only")
            sizes = [s for s in sizes if s in VALID_SIZES]
    
    # Parse variations
    variations = [v.strip() for v in args.variations.split(",")]
    
    # Determine ships to download
    if args.ships:
        ship_ids = parse_ship_list(args.ships)
        names = {v: k for k, v in ALL_SHIPS.items() if v in ship_ids}
    elif args.ship_class:
        ships = SHIP_CLASSES[args.ship_class]
        ship_ids = list(ships.values())
        names = {v: k for k, v in ships.items()}
    elif args.all_frigates:
        ships = SHIP_CLASSES["frigates"]
        ship_ids = list(ships.values())
        names = {v: k for k, v in ships.items()}
    elif args.all_cruisers:
        ships = SHIP_CLASSES["cruisers"]
        ship_ids = list(ships.values())
        names = {v: k for k, v in ships.items()}
    elif args.all:
        ship_ids = list(ALL_SHIPS.values())
        names = {v: k for k, v in ALL_SHIPS.items()}
    
    if not ship_ids:
        print("❌ No valid ships specified")
        return
    
    # Run download
    asyncio.run(download_ship_set(ship_ids, sizes, variations, args.output, names))


if __name__ == "__main__":
    main()
