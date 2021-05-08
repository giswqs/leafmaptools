"""
Some leafmaptools utilities.
"""

import json
from typing import Tuple

import geojson


def bounds(geojson_obj: dict) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Calculate the bounds of the GeoJSON object as [[south, west], [north, east]].
    """
    # Is there really no simpler/faster way to do this (without NumPy)?
    coords = list(geojson.utils.coords(geojson_obj))
    south = min(lat for lon, lat in coords)
    north = max(lat for lon, lat in coords)
    west = min(lon for lon, lat in coords)
    east = max(lon for lon, lat in coords)
    bounds = [[south, west], [north, east]]
    return bounds


def is_valid_json(text: str) -> bool:
    """Is this text valid JSON?
    """
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False
