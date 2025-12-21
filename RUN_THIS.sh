#!/bin/bash
# One-Command Migration for EVE Rebellion
# Run this and answer the prompts - everything is automated!

echo "╔════════════════════════════════════════════════════════╗"
echo "║   EVE Rebellion - One-Command GitHub Migration        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "This script will:"
echo "  ✓ Create EVE_Ships repository structure"
echo "  ✓ Create EVE_Rebellion repository structure"  
echo "  ✓ Set up build scripts for AppImage + Windows exe"
echo "  ✓ Push everything to GitHub (optional)"
echo ""
echo "Your GitHub username: AreteDriver"
echo ""
read -p "Press Enter to start, or Ctrl+C to cancel..."
echo ""

# Run the migration script
bash migrate_everything.sh
