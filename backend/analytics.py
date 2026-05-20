import time

DENSITY_THRESHOLDS = {'low': 5, 'medium': 15, 'high': 30}

def compute_density(counts: dict) -> dict:
    total = counts.get('person', 0)
    if   total < DENSITY_THRESHOLDS['low']:    level = 'LOW'
    elif total < DENSITY_THRESHOLDS['medium']: level = 'MEDIUM'
    elif total < DENSITY_THRESHOLDS['high']:   level = 'HIGH'
    else:                                       level = 'CRITICAL'
    return {
        'total_people':    total,
        'total_vehicles':  counts.get('car', 0) + counts.get('truck', 0),
        'total_bikes':     counts.get('bicycle', 0) + counts.get('motorcycle', 0),
        'density_level':   level,
        'density_score':   min(100, int(total * 3.3)),
        'timestamp':       time.time(),
    }
