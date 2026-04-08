import random

def calculate_catch_rate(hp_max: int, hp_current: int, base_rate: int, ball_type: str) -> bool:
    """Returns True if caught, False if broke free."""
    ball_multipliers = {
        "pokeball": 1.0,
        "great_ball": 1.5,
        "ultra_ball": 2.0,
        "master_ball": 999.0 # Guaranteed
    }
    
    multiplier = ball_multipliers.get(ball_type, 1.0)
    
    # Bypass formula for Master Ball
    if ball_type == "master_ball":
        return True
        
    # Simplified Gen 1-4 Catch Formula
    catch_value = ((3 * hp_max - 2 * hp_current) * base_rate * multiplier) / (3 * hp_max)
    
    # Random roll between 0 and 255
    roll = random.randint(0, 255)
    
    return catch_value >= roll

def calculate_damage(attacker_level: int, power: int, attack_stat: int, defense_stat: int, type_advantage: float) -> int:
    """Calculates battle damage."""
    # Simplified Pokemon damage formula
    base_damage = (((2 * attacker_level / 5) + 2) * power * (attack_stat / defense_stat)) / 50
    total_damage = (base_damage + 2) * type_advantage * random.uniform(0.85, 1.0)
    return int(total_damage)
