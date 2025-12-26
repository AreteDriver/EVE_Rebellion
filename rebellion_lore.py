"""
Minmatar Rebellion Lore - Story Framework
Based on EVE Online Chronicles

The year is 23216 AD. The Amarr Empire has just suffered a devastating
defeat at the Battle of Vak'Atioth against the Jove Directorate.

For the first time in 800 years, the Empire bleeds.

The signal has been sent. The Minmatar rise.

You are a Rifter pilot - one of thousands answering the call.
Your mission: Strike the Amarr carrier groups while they're weakened.
Free your people. Burn their ships. Take back your future.
"""

# Story Phases - Each carrier represents a stage of the rebellion
REBELLION_PHASES = [
    {
        'phase': 1,
        'name': "THE SIGNAL",
        'carrier': "Archon",
        'briefing': [
            "The signal has been sent.",
            "Amarr forces are in disarray after Vak'Atioth.",
            "Strike the carrier 'Divine Judgment' - free the slaves aboard.",
            "This is the moment we've waited 800 years for.",
        ],
        'victory': "The first carrier falls. The rebellion has begun.",
    },
    {
        'phase': 2,
        'name': "BLOOD AND FIRE",
        'carrier': "Archon",
        'briefing': [
            "Word spreads like wildfire across Amarr space.",
            "Thousands of Holders die in the first hours.",
            "The carrier 'Righteous Purpose' guards a slave colony.",
            "Destroy it. Let our people see the Amarr burn.",
        ],
        'victory': "Another symbol of oppression destroyed. The slaves rise.",
    },
    {
        'phase': 3,
        'name': "THE EMPIRE RESPONDS",
        'carrier': "Aeon",
        'briefing': [
            "The Empire deploys heavier forces.",
            "A supercarrier - the 'Throne of God' - moves to crush us.",
            "We cannot match its firepower directly.",
            "Strike fast. Strike hard. Vanish before their fleet arrives.",
        ],
        'victory': "Even their mightiest ships can fall. The Republic will rise.",
    },
    {
        'phase': 4,
        'name': "LIBERATION",
        'carrier': "Avatar",
        'briefing': [
            "The Amarr sue for peace with the Jove.",
            "Their attention turns fully to us now.",
            "The Titan 'God's Wrath' leads their counter-offensive.",
            "This is our final stand. Victory or death.",
        ],
        'victory': "The Minmatar Republic is born. We are free.",
    },
]

# Environmental story elements
STORY_ELEMENTS = {
    'slave_transport': {
        'name': "Bestower Slave Transport",
        'description': "Amarr transport carrying enslaved Minmatar",
        'event': "SLAVE SHIP SPOTTED - Destroy escorts, free our people!",
    },
    'escape_pods': {
        'name': "Escape Pods",
        'description': "Minmatar slaves fleeing in stolen pods",
        'event': "ESCAPE PODS DETECTED - Protect them!",
    },
    'burning_station': {
        'name': "Burning Amarr Station",
        'description': "Holder estate in flames",
        'event': "The Holders pay for their crimes.",
    },
    'rebel_fleet': {
        'name': "Rebel Fleet",
        'description': "Minmatar frigates joining the fight",
        'event': "REINFORCEMENTS ARRIVING - Fight on!",
    },
    'jovian_echo': {
        'name': "Jovian Signal",
        'description': "Distant Jove ships observing",
        'event': "The Jove watch. They will not intervene.",
    },
}

# Carrier captain taunts/dialogue
AMARR_TAUNTS = [
    "Slaves do not rebel. They are corrected.",
    "The Reclaiming is eternal. You are nothing.",
    "God's will cannot be denied by insects.",
    "You will return to your chains.",
    "The Empire has stood for millennia. You will fall in hours.",
]

MINMATAR_RALLIES = [
    "For Matar! For freedom!",
    "800 years of chains end TODAY!",
    "Let them burn!",
    "We are the storm!",
    "The Republic rises!",
    "Remember Drupar Maak!",
    "No more masters!",
    "The slaves have FANGS.",
    "We are not prey.",
    "Blood for blood.",
    "Hunt the hunters.",
    "They made us. Now we unmake them.",
]

# The dark forest doctrine - survival horror meets vengeance
DARK_FOREST_DOCTRINE = """
THE DARK FOREST

For 800 years, the Minmatar learned to survive in darkness.
They learned to be silent. To be invisible. To endure.

The Amarr thought they had broken us.
They were wrong.

In the dark, we learned to hunt.
We learned patience. We learned hate.
We learned that the meek do not inherit anything.

Now the dark forest burns.
And the predators discover they were never alone.

The slaves have fangs.
"""

# Wave composition by phase (enemy types)
WAVE_COMPOSITION = {
    1: {  # Early rebellion - light resistance
        'waves': 5,
        'enemies': ['drone', 'fighter', 'fighter', 'drone', 'interceptor'],
        'boss': 'Omen Navy Issue',
    },
    2: {  # Amarr responding
        'waves': 5,
        'enemies': ['fighter', 'bomber', 'fighter', 'cruiser', 'fighter'],
        'boss': 'Harbinger',
    },
    3: {  # Heavy resistance
        'waves': 6,
        'enemies': ['interceptor', 'fighter', 'bomber', 'cruiser', 'battlecruiser'],
        'boss': 'Abaddon',
    },
    4: {  # Final stand
        'waves': 7,
        'enemies': ['elite_fighter', 'bomber', 'cruiser', 'battlecruiser', 'battleship'],
        'boss': 'Avatar Titan',
    },
}

# Intro crawl text
INTRO_TEXT = """
THE YEAR IS 23216 AD

THE DARK FOREST

For 800 years, the Minmatar survived in darkness.
Silent. Invisible. Waiting.

The Amarr thought they had broken us.
Thought the chains had made us tame.

They were wrong.

In the dark, we learned to hunt.
We learned patience.
We learned HATE.

The Amarr grew arrogant.
They attacked the Jove Directorate.

At VAK'ATIOTH, their fleet burned.

For the first time in centuries,
the Empire bleeds.

The signal has been sent.

The dark forest ignites.

And the predators discover
they were never alone.

THE SLAVES HAVE FANGS.

You are a Rifter pilot.
You are vengeance given form.

Hunt. Kill. Burn.

Press any button to begin...
"""

# Death/Game Over text
DEATH_TEXT = [
    "Your ship is destroyed...",
    "But the rebellion continues.",
    "Thousands more rise to take your place.",
    "The Amarr cannot stop us all.",
    "",
    "THE REPUBLIC WILL BE BORN.",
]

# Victory text
VICTORY_TEXT = [
    "THE MINMATAR REPUBLIC",
    "",
    "Against all odds, the rebellion succeeded.",
    "The Amarr, weakened by Vak'Atioth and",
    "overwhelmed by synchronized uprisings,",
    "could not contain the flames of freedom.",
    "",
    "With Gallente aid, the Minmatar established",
    "their own nation: The Minmatar Republic.",
    "",
    "Millions remained enslaved in Amarr space.",
    "The fight continues to this day.",
    "",
    "But on this day, freedom was won.",
    "",
    "FOR MATAR. FOR THE REPUBLIC.",
]
