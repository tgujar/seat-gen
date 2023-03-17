# seat-gen

A seat randomizer for test taking.

## Features:

- Config file(`config.yaml`) to specify seat naming in shorthand.
- Match students based on if they are left or right handed.
- Regex matching for seats to assign spacing between them with priority.

## Spacing priority

Seats are sorted first according to the `spacing_priority` specified in the config. Seats matching a regex expression at an earlier index in the `spacing_priority` array appear earlier in the sorted array.

Spacing is then assigned to seats, starting with seats which appear earlier in the sorted array.

**Note: config fields are explained in the config file**

## How to run

From repository root run:

```
pip install -r requirements.txt
python3 assign.py
```
