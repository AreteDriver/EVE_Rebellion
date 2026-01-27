#!/usr/bin/env python3
"""
Quick test script for Berserk System
Run this to verify the system works before integrating
"""

from berserk_system import BerserkSystem
from devil_blade_effects import EffectManager


def test_berserk_system():
    print("🎮 Testing Devil Blade Berserk System\n")

    # Create system
    berserk = BerserkSystem()
    print("✅ Berserk System created")

    # Test distance calculations
    player_pos = (400, 300)  # Center of 800x600 screen

    test_cases = [
        ((440, 310), "EXTREME CLOSE (40px)"),
        ((480, 300), "CLOSE (80px)"),
        ((550, 300), "MEDIUM (150px)"),
        ((700, 300), "FAR (300px)"),
        ((900, 300), "VERY FAR (500px)"),
    ]

    print("\n📏 Distance Multiplier Tests:")
    print("-" * 60)

    total_score = 0
    for enemy_pos, description in test_cases:
        base_score = 100
        final_score = berserk.register_kill(base_score, player_pos, enemy_pos)
        multiplier = final_score / base_score

        print(f"{description:25} → {multiplier:.1f}x → {final_score} points")
        total_score += final_score

    print("-" * 60)
    print(f"Total score: {total_score}")

    # Test stats
    print("\n📊 Statistics:")
    stats = berserk.get_stats()
    print(f"  Total kills: {stats['total_kills']}")
    print(f"  Average multiplier: {stats['avg_multiplier']:.2f}x")
    print(f"  Extreme kills: {stats['extreme_kills']}")
    print("  Kills by range:")
    for range_name, count in stats["kills_by_range"].items():
        if count > 0:
            print(f"    {range_name}: {count}")

    print("\n✅ Berserk System test complete!")
    return True


def test_effects():
    print("\n🎨 Testing Visual Effects System\n")

    effects = EffectManager()
    print("✅ Effect Manager created")

    # Add some effects
    effects.add_explosion((100, 100), (255, 150, 50), particle_count=30)
    effects.add_shake(intensity=5, duration=10)
    effects.add_flash((255, 255, 255), duration=8)

    print("✅ Created test effects:")
    print(f"  - {len(effects.explosions)} explosions")
    print(f"  - {len(effects.shakes)} screen shakes")
    print(f"  - {len(effects.flashes)} screen flashes")

    # Update for a few frames
    for i in range(5):
        effects.update()

    print("\n✅ After 5 frames of updates:")
    print(f"  - {len(effects.explosions)} explosions remaining")
    print(f"  - {len(effects.shakes)} shakes remaining")
    print(f"  - {len(effects.flashes)} flashes remaining")

    print("\n✅ Effect system test complete!")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("DEVIL BLADE BERSERK SYSTEM - STANDALONE TEST")
    print("=" * 60)

    try:
        test_berserk_system()
        test_effects()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe Berserk System is ready for integration!")
        print("See DEVIL_BLADE_INTEGRATION.md for next steps.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
