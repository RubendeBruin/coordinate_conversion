# coordinate_conversion

Desktop tool (Python + PySide6) to convert WGS84 coordinates to local relative X/Y positions.

## Run

```bash
python app.py
```

## Input format

Paste multi-line free-format text where each line starts with a name, followed by coordinates.
A line named `Origin` defines the reference point.

Example (decimal degrees):

```text
Origin: 3.8163243, 52.7022056
P1 3.826240, 52.704478
P2 3.818058, 52.695705
```

The UI lets you choose:
- decimal degrees or degrees+minutes input
- whether longitude values are East-positive or West-positive
- whether latitude values are North-positive or South-positive

Output is tab-separated (`Name`, `X`, `Y`) so it can be copied directly.
