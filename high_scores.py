"""
Minmatar Rebellion - High Score System
Persistent score tracking with leaderboard
"""

import json
import os
from datetime import datetime


class HighScoreManager:
    """Manages high scores with persistent storage"""

    SAVE_FILE = "highscores.json"
    MAX_SCORES = 10

    def __init__(self):
        self.scores = []
        self.load()

    def load(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.SAVE_FILE):
                with open(self.SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.scores = data.get('scores', [])
        except (json.JSONDecodeError, IOError):
            self.scores = []

    def save(self):
        """Save high scores to file"""
        try:
            with open(self.SAVE_FILE, 'w') as f:
                json.dump({'scores': self.scores}, f, indent=2)
        except IOError:
            pass

    def add_score(self, score, refugees, stage, wave, ship, difficulty, berserk_stats=None):
        """
        Add a new score to the leaderboard.
        Returns (rank, is_new_high) tuple - rank is 1-indexed, or 0 if not in top 10
        """
        entry = {
            'score': score,
            'refugees': refugees,
            'stage': stage,
            'wave': wave,
            'ship': ship,
            'difficulty': difficulty,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'berserk': berserk_stats or {}
        }

        # Find insertion position
        insert_pos = len(self.scores)
        for i, existing in enumerate(self.scores):
            if score > existing['score']:
                insert_pos = i
                break

        # Check if it's a new high score
        is_new_high = insert_pos == 0 and (not self.scores or score > self.scores[0]['score'])

        # Insert and trim to max
        self.scores.insert(insert_pos, entry)
        self.scores = self.scores[:self.MAX_SCORES]

        self.save()

        # Return rank (1-indexed) if in top 10, else 0
        rank = insert_pos + 1 if insert_pos < self.MAX_SCORES else 0
        return rank, is_new_high

    def get_high_score(self):
        """Get the current high score, or 0 if none"""
        if self.scores:
            return self.scores[0]['score']
        return 0

    def get_top_scores(self, count=5):
        """Get top N scores"""
        return self.scores[:count]

    def is_high_score(self, score):
        """Check if a score would make the leaderboard"""
        if len(self.scores) < self.MAX_SCORES:
            return True
        return score > self.scores[-1]['score']

    def clear(self):
        """Clear all high scores"""
        self.scores = []
        self.save()


class AchievementManager:
    """Manages achievements and unlocks"""

    SAVE_FILE = "achievements.json"

    # Achievement definitions
    ACHIEVEMENTS = {
        # Combat achievements
        'first_blood': {
            'name': 'First Blood',
            'desc': 'Destroy your first enemy',
            'icon': 'skull',
            'hidden': False
        },
        'centurion': {
            'name': 'Centurion',
            'desc': 'Destroy 100 enemies in a single run',
            'icon': 'star',
            'hidden': False
        },
        'exterminator': {
            'name': 'Exterminator',
            'desc': 'Destroy 500 enemies in a single run',
            'icon': 'star2',
            'hidden': False
        },

        # Berserk achievements
        'up_close': {
            'name': 'Up Close and Personal',
            'desc': 'Get 10 extreme range kills in a run',
            'icon': 'fire',
            'hidden': False
        },
        'berserker': {
            'name': 'Berserker',
            'desc': 'Maintain a x3+ average multiplier',
            'icon': 'rage',
            'hidden': False
        },
        'death_wish': {
            'name': 'Death Wish',
            'desc': 'Get 50 extreme range kills in a run',
            'icon': 'skull2',
            'hidden': False
        },

        # Refugee achievements
        'liberator': {
            'name': 'Liberator',
            'desc': 'Rescue 50 refugees in a single run',
            'icon': 'people',
            'hidden': False
        },
        'freedom_fighter': {
            'name': 'Freedom Fighter',
            'desc': 'Rescue 200 refugees in a single run',
            'icon': 'flag',
            'hidden': False
        },

        # Progression achievements
        'survivor': {
            'name': 'Survivor',
            'desc': 'Complete Stage 1',
            'icon': 'shield',
            'hidden': False
        },
        'veteran': {
            'name': 'Veteran',
            'desc': 'Complete Stage 3',
            'icon': 'medal',
            'hidden': False
        },
        'rebel_hero': {
            'name': 'Rebel Hero',
            'desc': 'Complete the game on Normal or harder',
            'icon': 'trophy',
            'hidden': False
        },
        'nightmare_slayer': {
            'name': 'Nightmare Slayer',
            'desc': 'Complete the game on Nightmare',
            'icon': 'crown',
            'hidden': True
        },

        # Ship achievements
        'wolf_pack': {
            'name': 'Wolf Pack',
            'desc': 'Complete a run with the Wolf',
            'icon': 'wolf',
            'hidden': False
        },
        'speed_demon': {
            'name': 'Speed Demon',
            'desc': 'Complete a run with the Jaguar',
            'icon': 'lightning',
            'hidden': False
        },

        # Score achievements
        'high_roller': {
            'name': 'High Roller',
            'desc': 'Score over 50,000 points',
            'icon': 'coin',
            'hidden': False
        },
        'score_master': {
            'name': 'Score Master',
            'desc': 'Score over 100,000 points',
            'icon': 'gem',
            'hidden': False
        },

        # Secret achievements
        'no_upgrades': {
            'name': 'Purist',
            'desc': 'Complete Stage 3 without buying upgrades',
            'icon': 'zen',
            'hidden': True
        },
        'pacifist_run': {
            'name': 'Close Quarters Only',
            'desc': 'Complete a stage with only extreme/close kills',
            'icon': 'fist',
            'hidden': True
        }
    }

    def __init__(self):
        self.unlocked = set()
        self.stats = {
            'total_kills': 0,
            'total_refugees': 0,
            'games_played': 0,
            'victories': 0
        }
        self.pending_unlocks = []  # Achievements unlocked this session
        self.load()

    def load(self):
        """Load achievements from file"""
        try:
            if os.path.exists(self.SAVE_FILE):
                with open(self.SAVE_FILE, 'r') as f:
                    data = json.load(f)
                    self.unlocked = set(data.get('unlocked', []))
                    self.stats = data.get('stats', self.stats)
        except (json.JSONDecodeError, IOError):
            pass

    def save(self):
        """Save achievements to file"""
        try:
            with open(self.SAVE_FILE, 'w') as f:
                json.dump({
                    'unlocked': list(self.unlocked),
                    'stats': self.stats
                }, f, indent=2)
        except IOError:
            pass

    def unlock(self, achievement_id):
        """Unlock an achievement. Returns True if newly unlocked."""
        if achievement_id in self.ACHIEVEMENTS and achievement_id not in self.unlocked:
            self.unlocked.add(achievement_id)
            self.pending_unlocks.append(achievement_id)
            self.save()
            return True
        return False

    def is_unlocked(self, achievement_id):
        """Check if an achievement is unlocked"""
        return achievement_id in self.unlocked

    def get_pending_unlocks(self):
        """Get and clear pending unlock notifications"""
        pending = self.pending_unlocks.copy()
        self.pending_unlocks.clear()
        return pending

    def check_achievements(self, game_stats):
        """Check and unlock achievements based on game stats"""
        newly_unlocked = []

        kills = game_stats.get('total_kills', 0)
        refugees = game_stats.get('refugees', 0)
        score = game_stats.get('score', 0)
        stage = game_stats.get('stage', 0)
        victory = game_stats.get('victory', False)
        ship = game_stats.get('ship', 'Rifter')
        difficulty = game_stats.get('difficulty', 'normal')
        berserk = game_stats.get('berserk', {})

        extreme_kills = berserk.get('kills_by_range', {}).get('EXTREME', 0)
        avg_mult = berserk.get('avg_multiplier', 1.0)

        # Combat achievements
        if kills >= 1:
            if self.unlock('first_blood'):
                newly_unlocked.append('first_blood')
        if kills >= 100:
            if self.unlock('centurion'):
                newly_unlocked.append('centurion')
        if kills >= 500:
            if self.unlock('exterminator'):
                newly_unlocked.append('exterminator')

        # Berserk achievements
        if extreme_kills >= 10:
            if self.unlock('up_close'):
                newly_unlocked.append('up_close')
        if extreme_kills >= 50:
            if self.unlock('death_wish'):
                newly_unlocked.append('death_wish')
        if avg_mult >= 3.0 and kills >= 20:
            if self.unlock('berserker'):
                newly_unlocked.append('berserker')

        # Refugee achievements
        if refugees >= 50:
            if self.unlock('liberator'):
                newly_unlocked.append('liberator')
        if refugees >= 200:
            if self.unlock('freedom_fighter'):
                newly_unlocked.append('freedom_fighter')

        # Progression achievements
        if stage >= 1:
            if self.unlock('survivor'):
                newly_unlocked.append('survivor')
        if stage >= 3:
            if self.unlock('veteran'):
                newly_unlocked.append('veteran')

        # Victory achievements
        if victory:
            if difficulty in ['normal', 'hard', 'nightmare']:
                if self.unlock('rebel_hero'):
                    newly_unlocked.append('rebel_hero')
            if difficulty == 'nightmare':
                if self.unlock('nightmare_slayer'):
                    newly_unlocked.append('nightmare_slayer')
            if ship == 'Wolf':
                if self.unlock('wolf_pack'):
                    newly_unlocked.append('wolf_pack')
            if ship == 'Jaguar':
                if self.unlock('speed_demon'):
                    newly_unlocked.append('speed_demon')

        # Score achievements
        if score >= 50000:
            if self.unlock('high_roller'):
                newly_unlocked.append('high_roller')
        if score >= 100000:
            if self.unlock('score_master'):
                newly_unlocked.append('score_master')

        # Update persistent stats
        self.stats['total_kills'] += kills
        self.stats['total_refugees'] += refugees
        self.stats['games_played'] += 1
        if victory:
            self.stats['victories'] += 1
        self.save()

        return newly_unlocked

    def get_achievement_info(self, achievement_id):
        """Get info about an achievement"""
        return self.ACHIEVEMENTS.get(achievement_id)

    def get_all_achievements(self, include_hidden=False):
        """Get list of all achievements with unlock status"""
        result = []
        for aid, info in self.ACHIEVEMENTS.items():
            if info.get('hidden') and not include_hidden and aid not in self.unlocked:
                continue
            result.append({
                'id': aid,
                'unlocked': aid in self.unlocked,
                **info
            })
        return result

    def get_progress(self):
        """Get achievement progress as (unlocked, total)"""
        total = len([a for a in self.ACHIEVEMENTS.values() if not a.get('hidden')])
        unlocked = len([a for a in self.unlocked if not self.ACHIEVEMENTS.get(a, {}).get('hidden')])
        return unlocked, total
