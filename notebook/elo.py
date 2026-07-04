"""F1 asymmetric Elo system.

Python port of the R/tidyverse implementation in F1_DriverPeformance.qmd
(the `elo-prep` and `elo-compute` chunks) and elo_design.md — see f1_PLAN/
for the redesign this module belongs to. The rules are ported exactly as
implemented in the qmd (not the design doc's prose where the two differ,
e.g. Category 1 is not zeroed for DQ drivers who set a real qualifying time
in the source code, even though the design doc's summary suggests it is).

Structure is iterative and explicit rather than a vectorised translation of
the R tibble folds — race fields are ~20-30 drivers, so plain loops over
sorted lists are both fast enough and far easier to follow than the
cross-join-then-filter approach the R version needed to express "compare
each driver to a range of opponents" in dplyr.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

K1 = K3 = 32
K2 = 16
SPRINT_K2 = K2  # scaled per-event by sprint_weight(), see process_sprint
SPRINT_K3 = K3
FLOOR = 100
START = 1000

DQ_CODES = {"D", "E"}
RETIRED_CODES = {"R", "N", "W", "F"}


def classify_result(position_text: object) -> str:
    text = str(position_text)
    if text in DQ_CODES:
        return "DQ"
    if text in RETIRED_CODES:
        return "Retired"
    return "Classified"


def elo_expected(ra: float, rb: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rb - ra) / 400))


@dataclass
class RaceEntry:
    driver_id: int
    quali_pos: float | None
    grid: int
    position_order: float | None
    result_type: str
    laps: int | None
    race_name: str
    date: str


# ---------------------------------------------------------------------------
# Data loading & prep — mirrors qmd's `elo-prep` chunk
# ---------------------------------------------------------------------------

def load_dataset(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (race_data, sprint_data): both normalised, one row per
    driver per event, ready to feed into run_full / run_incremental."""
    data_dir = Path(data_dir)
    races = pd.read_csv(data_dir / "races.csv", na_values="\\N")
    results = pd.read_csv(data_dir / "results.csv", na_values="\\N")
    qualifying = pd.read_csv(data_dir / "qualifying.csv", na_values="\\N")
    sprint_results = pd.read_csv(data_dir / "sprint_results.csv", na_values="\\N")

    races_modern = (
        races.loc[races["year"] >= 1970, ["raceId", "year", "round", "name", "date"]]
        .rename(columns={"name": "race_name"})
        .sort_values(["year", "round"])
    )

    quali = qualifying.drop_duplicates(subset=["raceId", "driverId"])[
        ["raceId", "driverId", "position"]
    ].rename(columns={"position": "quali_pos"})
    quali["quali_pos"] = pd.to_numeric(quali["quali_pos"], errors="coerce")

    race_data = _prep_results(races_modern, results, quali)
    sprint_data = _prep_results(races_modern, sprint_results, quali=None)
    return race_data, sprint_data


def _prep_results(
    races_modern: pd.DataFrame, results: pd.DataFrame, quali: pd.DataFrame | None
) -> pd.DataFrame:
    results = results.copy()
    results["result_type"] = results["positionText"].apply(classify_result)

    merged = races_modern.merge(
        results[["raceId", "driverId", "grid", "positionOrder", "result_type", "laps"]],
        on="raceId",
        how="inner",
    )
    if quali is not None:
        merged = merged.merge(quali, on=["raceId", "driverId"], how="left")
    else:
        merged["quali_pos"] = pd.NA

    return _normalise_grid_and_position(merged)


def _normalise_grid_and_position(df: pd.DataFrame) -> pd.DataFrame:
    """Pit-lane starts (grid 0/NA) go to the back of the grid; DQ drivers
    with no recorded finish are placed after the last classified finisher.
    Both are computed per-race, so this loops over race groups explicitly
    rather than leaning on a single global vectorised pass."""
    fixed_groups = []
    for _, group in df.groupby("raceId", sort=False):
        group = group.copy()

        pit_lane = group["grid"].isna() | (group["grid"] == 0)
        group.loc[pit_lane, "grid"] = len(group) + 1
        group["grid"] = group["grid"].astype(int)

        classified = group[group["result_type"] == "Classified"]
        max_classified = classified["positionOrder"].max() if not classified.empty else 0
        needs_fix = (group["result_type"] == "DQ") & group["positionOrder"].isna()
        if needs_fix.any():
            group.loc[needs_fix, "positionOrder"] = max_classified + needs_fix[needs_fix].cumsum()

        fixed_groups.append(group)

    return pd.concat(fixed_groups, ignore_index=True)


def _entries_from_group(group: pd.DataFrame) -> list[RaceEntry]:
    race_name = group["race_name"].iat[0]
    date = group["date"].iat[0]
    entries = []
    for row in group.itertuples(index=False):
        entries.append(
            RaceEntry(
                driver_id=row.driverId,
                quali_pos=None if pd.isna(row.quali_pos) else float(row.quali_pos),
                grid=int(row.grid),
                position_order=None if pd.isna(row.positionOrder) else float(row.positionOrder),
                result_type=row.result_type,
                laps=None if pd.isna(row.laps) else int(row.laps),
                race_name=race_name,
                date=date,
            )
        )
    return entries


# ---------------------------------------------------------------------------
# Category deltas — plain loops over drivers sorted by position, comparing
# each to its neighbour(s). No lead/lag or cross-join needed.
# ---------------------------------------------------------------------------

def quali_deltas(entries: list[RaceEntry], elo_before: dict[int, float], k: float) -> dict[int, float]:
    ranked = sorted((e for e in entries if e.quali_pos is not None), key=lambda e: e.quali_pos)
    deltas: dict[int, float] = {}
    for i, e in enumerate(ranked):
        delta = 0.0
        if i + 1 < len(ranked):
            below = ranked[i + 1]
            delta += k * (1 - elo_expected(elo_before[e.driver_id], elo_before[below.driver_id]))
        if i > 0:
            above = ranked[i - 1]
            delta += k * (0 - elo_expected(elo_before[e.driver_id], elo_before[above.driver_id]))
        deltas[e.driver_id] = delta
    return deltas


def finish_deltas(entries: list[RaceEntry], elo_before: dict[int, float], k: float) -> dict[int, float]:
    classified = sorted(
        (e for e in entries if e.result_type == "Classified"), key=lambda e: e.position_order
    )
    deltas: dict[int, float] = {}
    for i, e in enumerate(classified):
        delta = 0.0
        if i + 1 < len(classified):
            below = classified[i + 1]
            delta += k * (1 - elo_expected(elo_before[e.driver_id], elo_before[below.driver_id]))
        if i > 0:
            above = classified[i - 1]
            delta += k * (0 - elo_expected(elo_before[e.driver_id], elo_before[above.driver_id]))
        deltas[e.driver_id] = delta

    if classified:
        last_elo = elo_before[classified[-1].driver_id]
        for e in entries:
            if e.result_type == "DQ":
                deltas[e.driver_id] = k * (0 - elo_expected(elo_before[e.driver_id], last_elo))
    return deltas


def grid_vs_finish_deltas(entries: list[RaceEntry], elo_before: dict[int, float], k: float) -> dict[int, float]:
    pool = [e for e in entries if e.result_type == "Classified"]
    deltas: dict[int, float] = {}
    for e in entries:
        if e.result_type == "Retired":
            continue
        fp, gp = e.position_order, e.grid
        total = 0.0
        if fp < gp and e.result_type != "DQ":  # improved, DQ can't "win" per the asymmetry rule
            for opp in pool:
                if fp < opp.position_order <= gp:
                    total += k * (1 - elo_expected(elo_before[e.driver_id], elo_before[opp.driver_id]))
        elif fp > gp:  # worsened — DQ still loses here
            for opp in pool:
                if gp <= opp.position_order < fp:
                    total += k * (0 - elo_expected(elo_before[e.driver_id], elo_before[opp.driver_id]))
        deltas[e.driver_id] = total
    return deltas


SPRINT_WEIGHT = 1 / 3


def sprint_weight(sprint_entries: list[RaceEntry], race_entries: list[RaceEntry]) -> float:
    """Fixed at 1/3 rather than computed per-weekend from lap counts — the
    real ratio clusters tightly around 0.32-0.34 across every sprint weekend
    in the dataset (one outlier at 0.25, a red-flag-shortened case), so a
    constant is simpler and close enough. Kept as a function (not just the
    constant inline) in case per-weekend weighting is worth revisiting later."""
    return SPRINT_WEIGHT


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class EloEngine:
    def __init__(self, ratings: dict[int, float] | None = None):
        self.ratings: dict[int, float] = dict(ratings or {})

    def rating(self, driver_id: int) -> float:
        return self.ratings.get(driver_id, START)

    def process_race(self, entries: list[RaceEntry]) -> list[dict]:
        elo_before = {e.driver_id: self.rating(e.driver_id) for e in entries}
        cat1 = quali_deltas(entries, elo_before, K1)
        cat2 = grid_vs_finish_deltas(entries, elo_before, K2)
        cat3 = finish_deltas(entries, elo_before, K3)
        return self._apply(entries, elo_before, cat1, cat2, cat3, race_name_suffix="")

    def process_sprint(self, entries: list[RaceEntry], weight: float) -> list[dict]:
        """No Category 1 — this dataset has no separate sprint qualifying,
        the weekend's one qualifying session already feeds the main race's
        Category 1. Categories 2 & 3 apply, scaled down by `weight`."""
        elo_before = {e.driver_id: self.rating(e.driver_id) for e in entries}
        cat2 = grid_vs_finish_deltas(entries, elo_before, SPRINT_K2 * weight)
        cat3 = finish_deltas(entries, elo_before, SPRINT_K3 * weight)
        return self._apply(entries, elo_before, {}, cat2, cat3, race_name_suffix=" (Sprint)")

    def _apply(
        self,
        entries: list[RaceEntry],
        elo_before: dict[int, float],
        cat1: dict[int, float],
        cat2: dict[int, float],
        cat3: dict[int, float],
        race_name_suffix: str,
    ) -> list[dict]:
        rows = []
        for e in entries:
            c1 = round(cat1.get(e.driver_id, 0.0))
            c2 = round(cat2.get(e.driver_id, 0.0))
            c3 = round(cat3.get(e.driver_id, 0.0))
            after = max(elo_before[e.driver_id] + c1 + c2 + c3, FLOOR)
            self.ratings[e.driver_id] = after
            rows.append(
                {
                    "driver_id": e.driver_id,
                    "date": e.date,
                    "race_name": e.race_name + race_name_suffix,
                    "quali_pos": e.quali_pos,
                    "finish_pos": e.position_order if e.result_type == "Classified" else None,
                    "cat1_delta": c1,
                    "cat2_delta": c2,
                    "cat3_delta": c3,
                    "elo_after": after,
                }
            )
        return rows


# ---------------------------------------------------------------------------
# Orchestration — full run vs incremental (see f1_PLAN/03 Python Elo Port.md)
# ---------------------------------------------------------------------------

def run_all_events(race_data: pd.DataFrame, sprint_data: pd.DataFrame, engine: EloEngine) -> list[dict]:
    rows: list[dict] = []
    sprint_groups = dict(tuple(sprint_data.groupby("raceId", sort=False)))
    race_order = (
        race_data[["raceId", "year", "round"]].drop_duplicates().sort_values(["year", "round"])["raceId"]
    )
    for race_id in race_order:
        race_entries = _entries_from_group(race_data[race_data["raceId"] == race_id])

        sprint_group = sprint_groups.get(race_id)
        if sprint_group is not None and not sprint_group.empty:
            sprint_entries = _entries_from_group(sprint_group)
            weight = sprint_weight(sprint_entries, race_entries)
            rows.extend(engine.process_sprint(sprint_entries, weight))  # Saturday, before the race

        rows.extend(engine.process_race(race_entries))  # Sunday

    return rows


def run_full(race_data: pd.DataFrame, sprint_data: pd.DataFrame) -> list[dict]:
    return run_all_events(race_data, sprint_data, EloEngine())


def run_incremental(
    race_data: pd.DataFrame, sprint_data: pd.DataFrame, existing_history: pd.DataFrame
) -> list[dict]:
    last_date = existing_history["date"].max()
    new_race_data = race_data[race_data["date"] > last_date]
    if new_race_data.empty:
        return []

    new_race_ids = set(new_race_data["raceId"])
    new_sprint_data = sprint_data[sprint_data["raceId"].isin(new_race_ids)]

    seed = existing_history.sort_values("date").groupby("driver_id")["elo_after"].last().to_dict()
    return run_all_events(new_race_data, new_sprint_data, EloEngine(seed))


# ---------------------------------------------------------------------------
# Output — see f1_PLAN/02 Architecture.md for the column rationale
# ---------------------------------------------------------------------------

HISTORY_COLUMNS = [
    "driver_id",
    "date",
    "race_name",
    "quali_pos",
    "finish_pos",
    "cat1_delta",
    "cat2_delta",
    "cat3_delta",
    "elo_after",
]


def history_to_dataframe(rows: list[dict]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=HISTORY_COLUMNS)
    return pd.DataFrame(rows)[HISTORY_COLUMNS]


def build_drivers_table(data_dir: Path, driver_ids: set[int]) -> pd.DataFrame:
    drivers = pd.read_csv(Path(data_dir) / "drivers.csv", na_values="\\N")
    drivers = drivers[drivers["driverId"].isin(driver_ids)].copy()
    drivers["name"] = drivers["forename"] + " " + drivers["surname"]
    return drivers[["driverId", "name", "driverRef"]].rename(
        columns={"driverId": "driver_id", "driverRef": "driver_ref"}
    )


# ---------------------------------------------------------------------------
# Local sanity check — run directly against a folder with the source CSVs
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run the Elo engine locally and print peak-Elo sanity-check values."
    )
    parser.add_argument(
        "data_dir",
        type=Path,
        help="Folder containing races.csv, results.csv, qualifying.csv, sprint_results.csv, drivers.csv",
    )
    parser.add_argument(
        "--no-sprints",
        action="store_true",
        help="Races only, no sprint weighting — use this first to validate the port before adding sprints.",
    )
    args = parser.parse_args()

    race_data, sprint_data = load_dataset(args.data_dir)
    if args.no_sprints:
        sprint_data = sprint_data.iloc[0:0]

    history = history_to_dataframe(run_full(race_data, sprint_data))

    driver_ref_by_id = pd.read_csv(args.data_dir / "drivers.csv", na_values="\\N").set_index("driverId")[
        "driverRef"
    ]
    history["driver_ref"] = history["driver_id"].map(driver_ref_by_id)

    peak_rows = history.loc[history.groupby("driver_id")["elo_after"].idxmax()]

    print(f"{'driver':<20}{'peak_elo':>10}   race / date")
    for ref in ["max_verstappen", "hamilton", "scheckter"]:
        match = peak_rows[peak_rows["driver_ref"] == ref]
        if match.empty:
            print(f"{ref:<20}{'not found':>10}")
            continue
        row = match.iloc[0]
        print(f"{ref:<20}{row['elo_after']:>10.0f}   {row['race_name']} ({row['date']})")
