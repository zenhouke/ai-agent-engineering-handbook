"""Versioned checkpoint repository. Caller supplies an initialized connection."""

import json
import sqlite3
from pathlib import Path


def initialize(connection: sqlite3.Connection) -> None:
    connection.executescript(Path(__file__).with_suffix(".sql").read_text())


def save(
    connection: sqlite3.Connection,
    tenant: str,
    task: str,
    expected_version: int,
    payload: dict,
) -> int:
    encoded = json.dumps(payload, sort_keys=True)
    with connection:
        if expected_version == 0:
            connection.execute(
                "INSERT INTO checkpoints VALUES (?, ?, 1, ?)", (tenant, task, encoded)
            )
        else:
            changed = connection.execute(
                "UPDATE checkpoints SET version=version+1,payload=? WHERE tenant=? AND task=? AND version=?",
                (encoded, tenant, task, expected_version),
            ).rowcount
            if changed != 1:
                raise RuntimeError("Checkpoint version conflict")
    return expected_version + 1


# Saving state does not prove an external operation did or did not execute.
