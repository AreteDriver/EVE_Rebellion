"""
capital_ship_enemy.py
=======================

This module defines a new enemy class for Minmatar Rebellion: a capital‑class
Amarr supercarrier.  It extends the existing ``Enemy`` class from the
``sprites`` module and exposes additional behaviour such as multiple
turrets that fire salvos of laser fire.  Use this class in a custom
stage (e.g. ``capital_ship_assault.json``) to introduce a late‑game boss
fight.

The existing game architecture loads enemies by name from ``constants.ENEMY_STATS``
and instantiates ``sprites.Enemy`` for each spawn.  To integrate this
class seamlessly, add an entry for ``"amarr_capital"`` in
``constants.ENEMY_STATS`` and update your wave definitions to spawn
``"amarr_capital"`` as the boss.  Alternatively, you can spawn this class
directly in your stage logic and manage its lifecycle manually.
"""

import random

import pygame

from sprites import Enemy, EnemyBullet


class CapitalShipEnemy(Enemy):
    """A massive Amarr capital ship with multiple turrets.

    This class extends the standard :class:`sprites.Enemy` to provide
    behaviour specific to a capital ship boss.  It spawns additional
    bullets from several turrets positioned along its hull.  The class
    expects that an entry for ``"amarr_capital"`` exists in
    ``constants.ENEMY_STATS`` with appropriate stats (health, size,
    fire rate, etc.).

    Parameters
    ----------
    x : int
        Horizontal spawn position.  The ship will start just above the
        visible screen and drift into view.
    difficulty : dict[str, float]
        Difficulty multipliers as passed to the base ``Enemy`` class.

    Attributes
    ----------
    turret_offsets : list[tuple[int, int]]
        Relative positions of the turrets from the capital ship's
        centre.  Bullets will spawn at these offsets.
    salvo_interval : int
        Milliseconds between turret salvos.
    last_salvo : int
        Timestamp (in pygame ticks) of the last salvo fired.
    """

    def __init__(self, x: int, difficulty: dict[str, float] | None = None) -> None:
        # Start off‑screen vertically so the capital ship slides into view
        super().__init__('amarr_capital', x, y=-200, difficulty=difficulty or {})

        # Define turret positions along the hull.  These offsets are relative
        # to the enemy sprite's centre (centre x, centre y).  Adjust to
        # match the size defined in constants.ENEMY_STATS['amarr_capital']['size'].
        self.turret_offsets: list[tuple[int, int]] = [
            (-80, 60),  # left turret
            (0, 80),    # centre turret
            (80, 60)    # right turret
        ]

        # Control firing cadence for salvos
        self.salvo_interval: int = self.fire_rate  # Use base fire rate as interval
        self.last_salvo: int = pygame.time.get_ticks()

    def update(self, *args, **kwargs) -> None:
        """
        Update the capital ship position and potentially fire salvos.

        This method overrides the base ``Enemy.update`` to call the
        superclass implementation and then handle additional turret fire.

        Returns
        -------
        None
        """
        # Call base class update (handles movement, phase changes, etc.)
        super().update(*args, **kwargs)

        # Fire salvos periodically
        now = pygame.time.get_ticks()
        if now - self.last_salvo >= self.salvo_interval:
            self.last_salvo = now
            self._fire_turret_salvo()

    def _fire_turret_salvo(self) -> None:
        """Spawn bullets from each turret.

        Creates ``EnemyBullet`` objects for each turret and adds them to the
        same sprite group as the capital ship (``self.groups()[0]``) so
        they are updated and drawn automatically by Pygame.  Bullets
        inherit damage from the ``Enemy`` class.
        """
        # Determine the parent sprite group to insert bullets into.
        # If this enemy is not added to any group yet, bail out.
        groups = self.groups()
        if not groups:
            return
        group = groups[0]

        # Loop through turret offsets and spawn bullets
        for offset in self.turret_offsets:
            # Compute absolute position for bullet spawn
            bx = self.rect.centerx + offset[0]
            by = self.rect.centery + offset[1]

            # Bullets travel downwards with slight horizontal variance
            dx = random.uniform(-1.0, 1.0)
            dy = 3.0  # constant downward speed

            bullet = EnemyBullet(bx, by, dx, dy, damage=20)  # Capital ship turret damage
            group.add(bullet)

        # Optionally play a sound effect here (requires sound manager)
