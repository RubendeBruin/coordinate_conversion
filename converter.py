import math
import re
from dataclasses import dataclass

EARTH_RADIUS_M = 6_378_137.0
NUMBER_PATTERN = re.compile(r"[-+]?\d+(?:[\.,]\d+)?")
LINE_PATTERN = re.compile(r"^([^:;\t\s]+)\s*[:;]?\s+(.*)$")


@dataclass(frozen=True)
class ParsedPoint:
    name: str
    lon: float
    lat: float


def _extract_numbers(text: str) -> list[float]:
    return [float(match.group(0).replace(",", ".")) for match in NUMBER_PATTERN.finditer(text)]


def _apply_positive_direction(value: float, positive_direction: str) -> float:
    direction_factor = -1.0 if positive_direction in {"W", "S"} else 1.0
    return value * direction_factor


def _combine_degrees_minutes(degrees: float, minutes: float) -> float:
    minute_component = abs(minutes) / 60.0
    if degrees < 0:
        return degrees - minute_component
    if degrees > 0:
        return degrees + minute_component
    return minutes / 60.0


def parse_coordinate_pair(payload: str, coord_format: str, lon_positive: str, lat_positive: str) -> tuple[float, float]:
    numbers = _extract_numbers(payload)

    if coord_format == "decimal":
        if len(numbers) < 2:
            raise ValueError("Expected at least two decimal values (longitude, latitude).")
        lon_raw, lat_raw = numbers[0], numbers[1]
    elif coord_format == "dm":
        if len(numbers) < 4:
            raise ValueError("Expected degrees+minutes for longitude and latitude (4 values).")
        lon_deg, lon_min, lat_deg, lat_min = numbers[0], numbers[1], numbers[2], numbers[3]
        lon_raw = _combine_degrees_minutes(lon_deg, lon_min)
        lat_raw = _combine_degrees_minutes(lat_deg, lat_min)
    else:
        raise ValueError(f"Unsupported coordinate format: {coord_format}")

    lon = _apply_positive_direction(lon_raw, lon_positive)
    lat = _apply_positive_direction(lat_raw, lat_positive)
    return lon, lat


def parse_points(raw_text: str, coord_format: str, lon_positive: str, lat_positive: str) -> tuple[ParsedPoint, list[ParsedPoint]]:
    origin = None
    points: list[ParsedPoint] = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        match = LINE_PATTERN.match(stripped)
        if not match:
            raise ValueError(f"Could not parse line: {line}")

        name, payload = match.group(1).strip(), match.group(2).strip()
        lon, lat = parse_coordinate_pair(payload, coord_format, lon_positive, lat_positive)
        parsed = ParsedPoint(name=name, lon=lon, lat=lat)

        if name.lower() == "origin":
            origin = parsed
        else:
            points.append(parsed)

    if origin is None:
        raise ValueError("No origin found. Add a line starting with 'Origin'.")
    if not points:
        raise ValueError("No points found.")

    return origin, points


def to_relative_xy(origin: ParsedPoint, points: list[ParsedPoint]) -> list[tuple[str, float, float]]:
    lat0_rad = math.radians(origin.lat)
    m_per_deg_lon = EARTH_RADIUS_M * math.cos(lat0_rad) * math.pi / 180.0
    m_per_deg_lat = EARTH_RADIUS_M * math.pi / 180.0

    results: list[tuple[str, float, float]] = []
    for point in points:
        x = (point.lon - origin.lon) * m_per_deg_lon
        y = (point.lat - origin.lat) * m_per_deg_lat
        results.append((point.name, x, y))

    return results


def convert_text(raw_text: str, coord_format: str, lon_positive: str, lat_positive: str) -> str:
    origin, points = parse_points(raw_text, coord_format, lon_positive, lat_positive)
    results = to_relative_xy(origin, points)
    lines = ["Name\tX\tY"]
    for name, x, y in results:
        lines.append(f"{name}\t{x:.3f}\t{y:.3f}")
    return "\n".join(lines)
