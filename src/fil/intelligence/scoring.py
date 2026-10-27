"""Extracted source-order scoring primitives; no acquisition or research imports."""

from dataclasses import dataclass


class ScoreError(ValueError):
    """Unresolved score semantics or failed official reconciliation; do not publish."""


@dataclass(frozen=True)
class OfficialScore:
    match_id: int
    home_team_id: int
    away_team_id: int
    home_score: int
    away_score: int

    def __post_init__(self) -> None:
        for name in ("match_id", "home_team_id", "away_team_id", "home_score", "away_score"):
            value = getattr(self, name)
            if type(value) is not int or value < (0 if name.endswith("score") else 1):
                raise ScoreError(f"Invalid official {name}")
        if self.home_team_id == self.away_team_id:
            raise ScoreError("Official teams must be distinct")


@dataclass(frozen=True)
class ScoringSignal:
    event_id: str
    kind: str  # shot, own_for, own_against
    team_id: int
    player_id: int | None
    scored: bool
    penalty: bool
    related_event_ids: tuple[str, ...] = ()


_SHOT_OUTCOMES = {
    "Goal",
    "Blocked",
    "Off T",
    "Post",
    "Saved",
    "Wayward",
    "Saved Off Target",
    "Saved to Post",
}


def official_score(matches: list[dict], match_id: int) -> OfficialScore:
    """Read official team identity/final score from exactly one original metadata record."""
    try:
        rows = [m for m in matches if m["match_id"] == match_id]
        if len(rows) != 1:
            raise ScoreError("Expected one official match record")
        m = rows[0]
        return OfficialScore(
            m["match_id"],
            m["home_team"]["home_team_id"],
            m["away_team"]["away_team_id"],
            m["home_score"],
            m["away_score"],
        )
    except (KeyError, TypeError) as exc:
        raise ScoreError("Malformed official score metadata") from exc


def scoring_signals(events: list[dict]) -> tuple[ScoringSignal, ...]:
    """Shots (including misses) and own goals only; goalkeeper echoes never award goals."""
    result = []
    try:
        for e in events:
            name = e["type"]["name"]
            if name not in {"Shot", "Own Goal For", "Own Goal Against"}:
                continue
            if name == "Shot":
                shot = e["shot"]
                outcome = shot["outcome"]["name"]
                shot_type = shot["type"]["name"]
                if outcome not in _SHOT_OUTCOMES or shot_type not in {
                    "Open Play",
                    "Free Kick",
                    "Corner",
                    "Kick Off",
                    "Penalty",
                    "Other",
                }:
                    raise ScoreError("Unsupported shot outcome/type: score semantics unresolved")
                kind, scored, penalty = "shot", outcome == "Goal", shot_type == "Penalty"
            else:
                kind = "own_for" if name == "Own Goal For" else "own_against"
                scored, penalty = True, False
            links = e.get("related_events", [])
            if not isinstance(links, list) or any(not isinstance(i, str) for i in links):
                raise ScoreError("Malformed related event IDs")
            player = e.get("player")
            result.append(
                ScoringSignal(
                    e["id"],
                    kind,
                    e["team"]["id"],
                    player["id"] if player is not None else None,
                    scored,
                    penalty,
                    tuple(links),
                )
            )
    except (KeyError, TypeError) as exc:
        raise ScoreError("Malformed provider scoring fields; never infer missing outcomes") from exc
    return tuple(result)


def ordered_score(raw: list[dict], metadata: dict) -> dict:
    """Reconcile native order without creating a clock or assuming physical endpoints.

    Own-goal perspectives require explicit source links and matching native times.
    Shootout success is separate and is not certified against match-play metadata.
    """
    official = official_score([metadata], metadata["match_id"])
    teams = (official.home_team_id, official.away_team_id)
    by = {e["id"]: e for e in raw}
    signals = {s.event_id: s for s in scoring_signals(raw)}
    adjacency = {i: set() for i in signals}
    for i, signal in signals.items():
        if signal.team_id not in teams or i in signal.related_event_ids:
            raise ValueError("Invalid scoring identity/link")
        for j in signal.related_event_ids:
            if j not in by:
                raise ValueError("Unavailable scoring link")
            if j in signals:
                adjacency[i].add(j)
                adjacency[j].add(i)
    visited, own_instants, decisions = set(), set(), []
    for i in signals:
        if i in visited:
            continue
        component, pending = {i}, [i]
        while pending:
            for j in adjacency[pending.pop()] - component:
                component.add(j)
                pending.append(j)
        visited.update(component)
        ids = sorted(component, key=lambda j: by[j]["index"])
        members = [signals[j] for j in ids]
        first = by[ids[0]]
        if len(ids) > 1 and (
            len(ids) != 2
            or {s.kind for s in members} != {"own_for", "own_against"}
            or len({(by[j]["period"], by[j]["timestamp"]) for j in ids}) != 1
            or len({s.team_id for s in members}) != 2
        ):
            raise ValueError("Ambiguous scoring representations")
        own = members[0].kind != "shot"
        if own:
            instant = (first["period"], first["timestamp"])
            if instant in own_instants or first["period"] == 5:
                raise ValueError("Unlinked own-goal representations or invalid shootout")
            own_instants.add(instant)
            beneficiary = next(
                (s.team_id for s in members if s.kind == "own_for"),
                teams[1 - teams.index(members[0].team_id)],
            )
        else:
            beneficiary = members[0].team_id
            if first["period"] == 5 and not members[0].penalty:
                raise ValueError("Non-penalty shootout record")
        decisions.append(
            dict(
                source_event_ids=ids,
                provider_index=first["index"],
                period=first["period"],
                beneficiary_team_id=beneficiary,
                scored=members[0].scored,
                domain="shootout" if first["period"] == 5 else "match_play",
            )
        )
    totals = {"match_play": [0, 0], "shootout": [0, 0]}
    for d in decisions:
        if d["scored"]:
            totals[d["domain"]][teams.index(d["beneficiary_team_id"])] += 1
    if totals["match_play"] != [official.home_score, official.away_score]:
        raise ValueError("Native-order score disagrees with official metadata")
    return dict(
        **totals,
        decisions=decisions,
        shootout_official_reconciliation="unavailable",
        physical_timing_certified=False,
    )
