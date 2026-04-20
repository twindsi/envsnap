"""Scheduled snapshot capture: define and persist auto-capture schedules."""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional


def _schedule_path(snapshot_dir: str) -> str:
    return os.path.join(snapshot_dir, ".schedules.json")


def _load_schedules(snapshot_dir: str) -> dict:
    path = _schedule_path(snapshot_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_schedules(snapshot_dir: str, data: dict) -> None:
    path = _schedule_path(snapshot_dir)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


@dataclass
class Schedule:
    name: str
    interval: str  # e.g. "daily", "hourly", "weekly"
    prefix: Optional[str] = None
    enabled: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Schedule":
        return Schedule(**d)


VALID_INTERVALS = {"hourly", "daily", "weekly"}


def add_schedule(snapshot_dir: str, schedule: Schedule) -> None:
    if schedule.interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval '{schedule.interval}'. Choose from {VALID_INTERVALS}.")
    data = _load_schedules(snapshot_dir)
    data[schedule.name] = schedule.to_dict()
    _save_schedules(snapshot_dir, data)


def remove_schedule(snapshot_dir: str, name: str) -> bool:
    data = _load_schedules(snapshot_dir)
    if name not in data:
        return False
    del data[name]
    _save_schedules(snapshot_dir, data)
    return True


def get_schedule(snapshot_dir: str, name: str) -> Optional[Schedule]:
    data = _load_schedules(snapshot_dir)
    if name not in data:
        return None
    return Schedule.from_dict(data[name])


def list_schedules(snapshot_dir: str) -> List[Schedule]:
    data = _load_schedules(snapshot_dir)
    return [Schedule.from_dict(v) for v in data.values()]


def toggle_schedule(snapshot_dir: str, name: str, enabled: bool) -> bool:
    data = _load_schedules(snapshot_dir)
    if name not in data:
        return False
    data[name]["enabled"] = enabled
    _save_schedules(snapshot_dir, data)
    return True
