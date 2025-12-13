# Game Architecture Diagrams

## Game State Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      GAME STATE FLOW                         │
└─────────────────────────────────────────────────────────────┘

    ┌──────┐
    │ MENU │◄──────────────────────┐
    └───┬──┘                        │
        │ [Start Game]              │
        ↓                           │
   ┌─────────┐                      │
   │ PLAYING │                      │
   └────┬────┘                      │
        │                           │
    ┌───┴───┐                       │
    │       │                       │
    ↓       ↓                       │
[Stage   [Player                    │
Complete] Death]                    │
    │       │                       │
    ↓       ↓                       │
┌─────────┐ ┌───────────┐          │
│ UPGRADE │ │ GAME_OVER │──────────┘
└────┬────┘ └───────────┘
     │
     │ [Continue]
     │
     └──→ Back to PLAYING
```

## Entity Update Cycle

```
┌────────────────────────────────────────────────┐
│          FRAME UPDATE CYCLE (60 FPS)           │
├────────────────────────────────────────────────┤
│                                                 │
│  INPUT PHASE                                    │
│  ┌──────────────────────────────────────┐     │
│  │ • Keyboard events                     │     │
│  │ • Mouse events                        │     │
│  │ • State-specific routing              │     │
│  └──────────────────────────────────────┘     │
│           ↓                                     │
│  UPDATE PHASE (dt = delta time)                │
│  ┌──────────────────────────────────────┐     │
│  │ Player Update:                        │     │
│  │  • Position += velocity * dt          │     │
│  │  • Weapon cooldowns -= dt             │     │
│  │  • Bounds checking                    │     │
│  │                                        │     │
│  │ Enemy Update:                         │     │
│  │  • AI state machine tick              │     │
│  │  • Movement pattern execution         │     │
│  │  • Attack logic                       │     │
│  │                                        │     │
│  │ Bullet Update:                        │     │
│  │  • Position += velocity * dt          │     │
│  │  • Lifetime -= dt                     │     │
│  │  • Bounds check (despawn if off-screen)│   │
│  │                                        │     │
│  │ Collision Detection:                  │     │
│  │  • Player ↔ Enemy bullets             │     │
│  │  • Player bullets ↔ Enemies           │     │
│  │  • Player ↔ Powerups/Refugees         │     │
│  │                                        │     │
│  │ Spawn Logic:                          │     │
│  │  • Wave timer management              │     │
│  │  • Enemy spawning from stage data     │     │
│  └──────────────────────────────────────┘     │
│           ↓                                     │
│  RENDER PHASE                                   │
│  ┌──────────────────────────────────────┐     │
│  │ • Clear screen (black)                │     │
│  │ • Draw star field                     │     │
│  │ • Draw sprites (sorted by layer):     │     │
│  │   1. Bullets (bottom)                 │     │
│  │   2. Enemies                          │     │
│  │   3. Player                           │     │
│  │   4. Explosions                       │     │
│  │   5. Powerups (top)                   │     │
│  │ • Draw HUD (health, ammo, score)      │     │
│  │ • Apply screen shake offset           │     │
│  │ • Flip display buffer                 │     │
│  └──────────────────────────────────────┘     │
│           ↓                                     │
│  FRAME LIMITING                                 │
│  ┌──────────────────────────────────────┐     │
│  │ clock.tick(60)  # Cap at 60 FPS       │     │
│  └──────────────────────────────────────┘     │
│                                                 │
└────────────────────────────────────────────────┘
```

## Audio Synthesis Pipeline

```
┌────────────────────────────────────────────────┐
│       PROCEDURAL AUDIO SYNTHESIS FLOW          │
├────────────────────────────────────────────────┤
│                                                 │
│  Sound Event Triggered                          │
│  (e.g., player fires weapon)                    │
│           ↓                                     │
│  ┌─────────────────────────┐                   │
│  │  Waveform Generation    │                   │
│  │  • Sine wave            │                   │
│  │  • Sawtooth             │                   │
│  │  • Triangle             │                   │
│  │  • White noise          │                   │
│  │  → NumPy array          │                   │
│  └─────────────────────────┘                   │
│           ↓                                     │
│  ┌─────────────────────────┐                   │
│  │  ADSR Envelope          │                   │
│  │  • Attack (rise time)   │                   │
│  │  • Decay (drop)         │                   │
│  │  • Sustain (hold)       │                   │
│  │  • Release (fade)       │                   │
│  └─────────────────────────┘                   │
│           ↓                                     │
│  ┌─────────────────────────┐                   │
│  │  Effects Processing     │                   │
│  │  • Frequency sweep      │                   │
│  │  • Amplitude modulation │                   │
│  │  • Pitch bend           │                   │
│  │  • Filtering            │                   │
│  └─────────────────────────┘                   │
│           ↓                                     │
│  ┌─────────────────────────┐                   │
│  │  Format Conversion      │                   │
│  │  • Normalize [-1, 1]    │                   │
│  │  • Convert to int16     │                   │
│  │  • Make stereo          │                   │
│  │  → Pygame Sound object  │                   │
│  └─────────────────────────┘                   │
│           ↓                                     │
│  Play through Pygame mixer                      │
│                                                 │
└────────────────────────────────────────────────┘

Example: Autocannon
  1. Generate white noise (0.08s)
  2. Bandpass filter (200-800 Hz)
  3. ADSR: fast attack, quick release
  4. Frequency sweep (high→low)
  5. Output as 16-bit stereo
```

## Enemy AI State Machine

```
┌────────────────────────────────────────────────┐
│           ENEMY AI DECISION TREE               │
├────────────────────────────────────────────────┤
│                                                 │
│  ┌────────┐                                    │
│  │ SPAWN  │                                    │
│  └───┬────┘                                    │
│      │                                          │
│      ↓                                          │
│  ┌────────────┐                                │
│  │ ENTER      │ (Move from edge to position)   │
│  │ SCREEN     │                                │
│  └─────┬──────┘                                │
│        │                                        │
│        ↓                                        │
│  ┌──────────────────────────────┐             │
│  │   COMBAT LOOP                │             │
│  │   ┌──────────────────┐       │             │
│  │   │ State Selection  │       │             │
│  │   └────────┬─────────┘       │             │
│  │            │                  │             │
│  │     ┌──────┴──────┐           │             │
│  │     │             │           │             │
│  │     ↓             ↓           │             │
│  │  ATTACK       EVADE/FLANK    │             │
│  │     │             │           │             │
│  │     │    ┌────────┴────┐      │             │
│  │     │    │             │      │             │
│  │     │    ↓             ↓      │             │
│  │     │  CIRCLE      ZIGZAG     │             │
│  │     │    │             │      │             │
│  │     └────┴─────────────┘      │             │
│  │            │                  │             │
│  │            ↓                  │             │
│  │      Health Check             │             │
│  │            │                  │             │
│  │      ┌─────┴─────┐            │             │
│  │      │           │            │             │
│  │   HP > 0%    HP <= 0%         │             │
│  │      │           │            │             │
│  └──────┼───────────┼────────────┘             │
│         │           │                          │
│    Loop back    Explode & Destroy             │
│         │                                       │
│         ↓                                       │
│  ┌────────────┐                                │
│  │ EXIT       │ (Move off screen)              │
│  │ SCREEN     │                                │
│  └─────┬──────┘                                │
│        │                                        │
│        ↓                                        │
│  ┌────────┐                                    │
│  │ DESPAWN│                                    │
│  └────────┘                                    │
│                                                 │
│  Decision Factors:                             │
│  • Distance to player                          │
│  • Health % remaining                          │
│  • Attack cooldown                             │
│  • Formation position                          │
│  • Ship class (frigate/cruiser/boss)           │
│                                                 │
└────────────────────────────────────────────────┘
```

## Movement Patterns Detail

```
┌──────────────────────────────────────────┐
│        ENEMY MOVEMENT PATTERNS           │
├──────────────────────────────────────────┤
│                                           │
│  SINE WAVE                                │
│  ~~~~~~~~                                 │
│  x += speed * dt                          │
│  y += amplitude * sin(time * frequency)   │
│                                           │
│  ZIGZAG                                   │
│  /\/\/\                                   │
│  Direction changes at intervals           │
│  Sharp angle transitions                  │
│                                           │
│  SWOOP                                    │
│  ↘ ↗                                      │
│  Dive toward player                       │
│  Then arc back up                         │
│                                           │
│  FLANK                                    │
│  → ↓ ←                                    │
│  Approach from sides                      │
│  Try to get behind player                 │
│                                           │
│  CIRCLE                                   │
│  ⭕                                        │
│  Orbital strafe around player             │
│  Maintain distance while firing           │
│                                           │
└──────────────────────────────────────────┘
```

## Collision Detection Flow

```
┌──────────────────────────────────────┐
│    COLLISION DETECTION SYSTEM        │
├──────────────────────────────────────┤
│                                       │
│  For each frame:                      │
│                                       │
│  1. Player Bullets ↔ Enemies         │
│     ┌───────────────────────┐        │
│     │ pygame.sprite.        │        │
│     │ groupcollide()        │        │
│     │ • Rect collision      │        │
│     │ • dokill for both     │        │
│     └───────────────────────┘        │
│            ↓                          │
│     Apply damage to enemy             │
│     Create explosion                  │
│     Play sound                        │
│     Update score                      │
│                                       │
│  2. Enemy Bullets ↔ Player           │
│     ┌───────────────────────┐        │
│     │ pygame.sprite.        │        │
│     │ spritecollide()       │        │
│     └───────────────────────┘        │
│            ↓                          │
│     Apply damage to player            │
│     Play hit sound (shield/armor/hull)│
│     Screen shake                      │
│                                       │
│  3. Player ↔ Powerups                │
│     ┌───────────────────────┐        │
│     │ Simple rect overlap   │        │
│     └───────────────────────┘        │
│            ↓                          │
│     Apply powerup effect              │
│     Play pickup sound                 │
│     Remove powerup sprite             │
│                                       │
│  4. Player ↔ Refugees                │
│     Same as powerups                  │
│            ↓                          │
│     Increment refugee count           │
│     Play rescue sound                 │
│                                       │
└──────────────────────────────────────┘
```

## Data-Driven Stage System

```
┌─────────────────────────────────────────┐
│         STAGE PROGRESSION FLOW          │
├─────────────────────────────────────────┤
│                                          │
│  constants.py defines:                   │
│  STAGES = [                              │
│    {                                     │
│      'name': 'Stage 1',                  │
│      'waves': [                          │
│        {                                 │
│          'time': 2.0,                    │
│          'enemies': [                    │
│            {'type': 'Executioner', ...}, │
│          ]                               │
│        },                                │
│        ...                               │
│      ]                                   │
│    },                                    │
│    ...                                   │
│  ]                                       │
│           ↓                              │
│  Game loads current stage                │
│           ↓                              │
│  ┌─────────────────────┐                │
│  │ Wave Timer Running  │                │
│  └──────────┬──────────┘                │
│             │                            │
│    ┌────────┴────────┐                  │
│    │                 │                  │
│  Time for       Wait for next           │
│  next wave?       wave                  │
│    │                                     │
│    ↓                                     │
│  Spawn enemies from wave definition     │
│    │                                     │
│    ↓                                     │
│  Enemies enter screen                    │
│    │                                     │
│    ↓                                     │
│  Combat                                  │
│    │                                     │
│    ↓                                     │
│  All waves complete?                     │
│    │                                     │
│  ┌─┴───┐                                │
│  │     │                                 │
│ YES   NO                                 │
│  │     │                                 │
│  │     └──→ Continue spawning            │
│  │                                       │
│  ↓                                       │
│ Stage Complete                           │
│  ↓                                       │
│ Show Upgrade Screen                      │
│  ↓                                       │
│ Next Stage                               │
│                                          │
└─────────────────────────────────────────┘
```
