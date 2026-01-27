"""
Skill point upgrade screen for Minmatar Rebellion.

Allows players to spend accumulated skill points on permanent upgrades
defined in data/upgrades.json.

This screen shows a list of upgrades and their costs and tracks
purchased upgrades via the progression module.
"""

import json
from typing import Dict, List

import progression
import pygame

from constants import COLOR_HUD_BG, COLOR_TEXT


class UpgradeDefinition:
    def __init__(self, uid: str, data: Dict):
        self.uid = uid
        self.name = data.get("name", uid)
        self.description = data.get("description", "")
        self.cost = data.get("cost", 0)
        self.effect = data.get("effect", {})


class UpgradeScreen:
    def __init__(self, gsm, upgrade_file: str = "data/upgrades.json"):
        self.gsm = gsm
        with open(upgrade_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.upgrades = [UpgradeDefinition(uid, d) for uid, d in raw.items()]
        self.selected_index = 0
        data = progression.load_progress()
        self.sp_available = data.get("total_sp", 0)
        self.purchased = data.get("purchased_upgrades", [])
        self.progress_data = data
        self.font_title = pygame.font.SysFont("consolas", 32)
        self.font_item = pygame.font.SysFont("consolas", 24)
        self.font_desc = pygame.font.SysFont("consolas", 18)
        self.margin_top = 60
        self.item_height = 50

    def _save(self):
        progression.save_progress(
            sp=self.sp_available,
            unlocked_ships=self.progress_data.get("unlocked_ships", []),
            wolf_unlocked=self.progress_data.get("wolf_unlocked", False),
            jaguar_unlocked=self.progress_data.get("jaguar_unlocked", False),
            total_kills=self.progress_data.get("total_kills", 0),
            highest_stage=self.progress_data.get("highest_stage", 0),
        )
        self.progress_data["purchased_upgrades"] = self.purchased
        try:
            with open(progression.SAVE_FILE, "r+", encoding="utf-8") as f:
                save_data = json.load(f)
                save_data["purchased_upgrades"] = self.purchased
                save_data["total_sp"] = self.sp_available
                f.seek(0)
                json.dump(save_data, f, indent=2)
                f.truncate()
        except Exception:
            pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.gsm.pop()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.selected_index = (self.selected_index - 1) % len(self.upgrades)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_index = (self.selected_index + 1) % len(self.upgrades)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._purchase()

    def _purchase(self):
        up = self.upgrades[self.selected_index]
        if up.uid in self.purchased or self.sp_available < up.cost:
            return
        self.sp_available -= up.cost
        self.purchased.append(up.uid)
        self._save()

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((10, 10, 20))
        title = self.font_title.render("Skill Upgrades", True, (255, 200, 50))
        screen.blit(title, (20, 20))
        sp_txt = self.font_item.render(f"SP: {self.sp_available}", True, (200, 200, 200))
        screen.blit(sp_txt, (screen.get_width() - 150, 20))
        y = self.margin_top
        for i, up in enumerate(self.upgrades):
            selected = i == self.selected_index
            name_color = (255, 220, 120) if selected else (255, 255, 255)
            cost_color = (150, 150, 150) if up.uid in self.purchased else (120, 220, 120)
            name = self.font_item.render(up.name, True, name_color)
            screen.blit(name, (40, y))
            if up.uid in self.purchased:
                status = self.font_item.render("Purchased", True, (150, 150, 150))
            else:
                status = self.font_item.render(f"Cost: {up.cost}", True, cost_color)
            screen.blit(status, (400, y))
            y += self.item_height
        selected_up = self.upgrades[self.selected_index]
        lines = self._wrap(selected_up.description, 60)
        desc_y = screen.get_height() - (len(lines) + 1) * 20 - 20
        pygame.draw.rect(
            screen, COLOR_HUD_BG, (20, desc_y - 10, screen.get_width() - 40, (len(lines) + 1) * 22)
        )
        for line in lines:
            surf = self.font_desc.render(line, True, COLOR_TEXT)
            screen.blit(surf, (30, desc_y))
            desc_y += 20
        prompt = self.font_desc.render("Esc: Back   Enter: Purchase", True, (180, 180, 180))
        screen.blit(prompt, (20, screen.get_height() - 30))

    def _wrap(self, text: str, max_chars: int) -> List[str]:
        words = text.split()
        lines = []
        current = ""
        for w in words:
            if len(current) + len(w) + 1 <= max_chars:
                current = (current + " " + w).strip()
            else:
                lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines
