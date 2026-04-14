"""
Eco-Score & Carbon Footprint Analyzer
Calculates the estimated energy consumption (Joules) and Carbon Footprint (gCO2e)
based on the time complexity, space complexity, and specific programming language efficiency.

Data based on standard Green Software Engineering benchmarks (e.g., C is 1.0, Python is ~75x).
"""

import math

# Language Energy Efficiency Multipliers (Baseline C = 1.0)
LANGUAGE_ENERGY_MULTIPLIERS = {
    "c": 1.0,
    "cpp": 1.34,
    "cpp_unsupported": 1.34,
    "java": 1.98,
    "javascript": 4.45,
    "python": 75.88,
    "unknown": 20.0
}

# Base energy in Joules for a simple O(1) operation x 1 Million runs
BASE_ENERGY_JOULES_1M = 0.05 

# Average Global Carbon Intensity: ~475 grams of CO2 per kWh
CO2_PER_JOULE = 475 / 3_600_000 

def calculate_eco_score(time_complexity: str, space_complexity: str, language: str):
    """
    Returns the estimated energy (Joules) and Carbon Footprint (gCO2e)
    for 1 Million executions of the given code.
    """
    lang_multiplier = LANGUAGE_ENERGY_MULTIPLIERS.get(language, 20.0)
    
    # Estimate operation scaling factor based on Time Complexity
    # (Assuming an average input size N = 100 for visualization purposes)
    N = 100
    
    time_factor = 1.0
    if "O(n)" in time_complexity:
        time_factor = N
    elif "n log n" in time_complexity.lower():
        time_factor = N * 6.64  # log2(100)
    elif "n^2" in time_complexity:
        time_factor = N ** 2
    elif "n^3" in time_complexity:
        time_factor = N ** 3
    elif "2^n" in time_complexity:
        # Cap to 1,000,000 to avoid infinity. Note: For large N, 2^n easily exceeds this cap,
        # ensuring worst-case time complexity always results in an 'F' eco rating,
        # effectively making the language multiplier irrelevant for astronomically slow algorithms.
        time_factor = min(1_000_000, 2 ** N)
        
    # Space factor (memory allocations cost energy)
    space_factor = 1.0
    if "O(n)" in space_complexity:
        space_factor = 2.0
    elif "n^2" in space_complexity:
        space_factor = 5.0
        
    # Total Energy for 1 Million Runs
    energy_joules = BASE_ENERGY_JOULES_1M * lang_multiplier * time_factor * space_factor
    
    # Convert to Carbon Footprint (gCO2e)
    carbon_footprint = energy_joules * CO2_PER_JOULE
    
    # Calculate an Eco-Score out of 100
    # A perfectly optimized C program is 100.
    # A Python O(N^2) program will be ~0.
    max_perfect_energy = BASE_ENERGY_JOULES_1M * 1.0 * 1.0 * 1.0
    score_ratio = max_perfect_energy / max(energy_joules, max_perfect_energy)
    
    # Scale logarithmically for better visual variance
    eco_score = max(0, min(100, 100 + (math.log10(score_ratio) * 15)))
    
    # Eco Rating Label
    if eco_score > 80:
        eco_rating = "A+ (Excellent)"
    elif eco_score > 60:
        eco_rating = "B (Good)"
    elif eco_score > 40:
        eco_rating = "C (Average)"
    elif eco_score > 20:
        eco_rating = "D (Poor)"
    else:
        eco_rating = "F (High Carbon Impact)"

    return {
        "energy_joules_1m": round(energy_joules, 4),
        "carbon_gco2e_1m": round(carbon_footprint, 6),
        "eco_score_100": round(eco_score),
        "eco_rating": eco_rating
    }
