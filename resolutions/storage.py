"""JSON file storage operations for the resolution tracker."""

import json
from pathlib import Path
from typing import Optional

from .models import DataStore, Goal, LogEntry, Config


# Simple in-memory cache to avoid repeated disk reads
_cache: DataStore | None = None
_cache_mtime: float = 0


def get_data_dir() -> Path:
  """Get the data directory path, creating it if needed."""
  data_dir = Path.home() / ".resolutions"
  data_dir.mkdir(exist_ok=True)
  return data_dir


def get_data_file() -> Path:
  """Get the main data file path."""
  return get_data_dir() / "data.json"


def _invalidate_cache() -> None:
  """Invalidate the cache after writes."""
  global _cache, _cache_mtime
  _cache = None
  _cache_mtime = 0


def load_data() -> DataStore:
  """Load data from JSON file, using cache if valid."""
  global _cache, _cache_mtime
  data_file = get_data_file()

  # Check if cache is still valid
  if _cache is not None:
    if data_file.exists():
      mtime = data_file.stat().st_mtime
      if mtime == _cache_mtime:
        return _cache

  # Load from disk
  if data_file.exists():
    with open(data_file, "r") as f:
      data = json.load(f)
    _cache = DataStore.model_validate(data)
    _cache_mtime = data_file.stat().st_mtime
    return _cache

  _cache = DataStore()
  _cache_mtime = 0
  return _cache


def save_data(store: DataStore) -> None:
  """Save data to JSON file and update cache."""
  global _cache, _cache_mtime
  data_file = get_data_file()
  with open(data_file, "w") as f:
    json.dump(store.model_dump(mode="json"), f, indent=2, default=str)
  # Update cache with new data
  _cache = store
  _cache_mtime = data_file.stat().st_mtime


def add_goal(title: str, category: str = "general", target: str = "",
             priority: int = 3, emoji: str = "") -> Goal:
  """Add a new goal and return it."""
  store = load_data()
  goal = Goal(
    id=store.next_goal_id,
    title=title,
    category=category,
    target=target,
    priority=priority,
    emoji=emoji,
  )
  store.goals.append(goal)
  store.next_goal_id += 1
  save_data(store)
  return goal


def get_goals() -> list[Goal]:
  """Get all goals."""
  store = load_data()
  return store.goals


def get_goal(goal_id: int) -> Optional[Goal]:
  """Get a specific goal by ID."""
  store = load_data()
  for goal in store.goals:
    if goal.id == goal_id:
      return goal
  return None


def update_goal(goal_id: int, **kwargs) -> Optional[Goal]:
  """Update a goal's fields."""
  store = load_data()
  for i, goal in enumerate(store.goals):
    if goal.id == goal_id:
      updated = goal.model_copy(update=kwargs)
      store.goals[i] = updated
      save_data(store)
      return updated
  return None


def remove_goal(goal_id: int) -> bool:
  """Remove a goal and its logs. Returns True if found and removed."""
  store = load_data()
  original_count = len(store.goals)
  store.goals = [g for g in store.goals if g.id != goal_id]
  store.logs = [l for l in store.logs if l.goal_id != goal_id]
  if len(store.goals) < original_count:
    save_data(store)
    return True
  return False


def add_log(goal_id: int, raw_input: str, parsed_update: str = "",
            value: Optional[float] = None, unit: str = "",
            sentiment: str = "neutral") -> Optional[LogEntry]:
  """Add a log entry for a goal."""
  store = load_data()
  # Verify goal exists
  if not any(g.id == goal_id for g in store.goals):
    return None
  log = LogEntry(
    id=store.next_log_id,
    goal_id=goal_id,
    raw_input=raw_input,
    parsed_update=parsed_update,
    value=value,
    unit=unit,
    sentiment=sentiment,
  )
  store.logs.append(log)
  store.next_log_id += 1
  save_data(store)
  return log


def get_logs(goal_id: Optional[int] = None) -> list[LogEntry]:
  """Get logs, optionally filtered by goal ID."""
  store = load_data()
  if goal_id is not None:
    return [l for l in store.logs if l.goal_id == goal_id]
  return store.logs


def get_config() -> Config:
  """Get user configuration."""
  store = load_data()
  return store.config


def update_config(**kwargs) -> Config:
  """Update configuration settings."""
  store = load_data()
  store.config = store.config.model_copy(update=kwargs)
  save_data(store)
  return store.config


def get_goal_progress(goal_id: int) -> dict:
  """Calculate progress stats for a goal."""
  logs = get_logs(goal_id)
  if not logs:
    return {"count": 0, "total_value": 0, "last_log": None}

  total_value = sum(l.value or 0 for l in logs)
  sentiments = [l.sentiment for l in logs]

  return {
    "count": len(logs),
    "total_value": total_value,
    "last_log": logs[-1].timestamp,
    "positive_count": sentiments.count("positive"),
    "neutral_count": sentiments.count("neutral"),
    "struggling_count": sentiments.count("struggling"),
  }
