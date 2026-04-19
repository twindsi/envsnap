"""Compare multiple snapshots side-by-side."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envsnap.snapshot import load


@dataclass
class CompareResult:
    names: List[str]
    keys: List[str]
    table: Dict[str, Dict[str, Optional[str]]]  # key -> {snapshot_name -> value}

    def common_keys(self) -> List[str]:
        return [k for k in self.keys if all(self.table[k].get(n) is not None for n in self.names)]

    def divergent_keys(self) -> List[str]:
        return [
            k for k in self.keys
            if len({self.table[k].get(n) for n in self.names}) > 1
        ]


def compare_snapshots(snapshot_dir: str, names: List[str]) -> CompareResult:
    snapshots = {}
    for name in names:
        data = load(snapshot_dir, name)
        snapshots[name] = data.get("vars", {})

    all_keys = sorted({k for env in snapshots.values() for k in env})
    table: Dict[str, Dict[str, Optional[str]]] = {}
    for key in all_keys:
        table[key] = {name: snapshots[name].get(key) for name in names}

    return CompareResult(names=names, keys=all_keys, table=table)


def format_compare_table(result: CompareResult) -> str:
    col_width = max((len(n) for n in result.names), default=10)
    key_width = max((len(k) for k in result.keys), default=10)
    header = f"{'KEY':<{key_width}}  " + "  ".join(f"{n:<{col_width}}" for n in result.names)
    sep = "-" * len(header)
    rows = [header, sep]
    for key in result.keys:
        vals = "  ".join(f"{str(result.table[key].get(n, '')):<{col_width}}" for n in result.names)
        rows.append(f"{key:<{key_width}}  {vals}")
    return "\n".join(rows)
