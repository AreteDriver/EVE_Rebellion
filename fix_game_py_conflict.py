#!/usr/bin/env python3
"""Fix the merge conflict in game.py by keeping both sets of imports"""

import sys

def fix_conflict(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    in_conflict = False
    conflict_section = []
    
    for line in lines:
        if line.startswith('<<<<<<< HEAD'):
            in_conflict = True
            conflict_section = []
        elif line.startswith('======='):
            continue  # Skip the separator
        elif line.startswith('>>>>>>>'):
            in_conflict = False
            # We've collected all the conflict lines, now add them properly
            fixed_lines.extend(conflict_section)
        elif in_conflict:
            # Collect lines from both sides of the conflict
            conflict_section.append(line)
        else:
            fixed_lines.append(line)
    
    with open(filename, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed {filename}")

if __name__ == '__main__':
    fix_conflict('game.py')
