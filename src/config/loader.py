"""Load and expose the business configuration from business.yaml.

Phase 2: reads from the local YAML file.
Phase 3: this module will be updated to read from the "Config" tab in Google
Sheets, making categories / vehicles / workers editable by the owner without
touching any code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).parent / "business.yaml"


@dataclass(frozen=True)
class BusinessConfig:
    categories: list[str]
    vehicles: list[str]
    workers: list[str]


def load_business_config() -> BusinessConfig:
    data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
    return BusinessConfig(
        categories=data["categories"],
        vehicles=data["vehicles"],
        workers=data["workers"],
    )


# Module-level singleton — loaded once at import time.
business = load_business_config()
