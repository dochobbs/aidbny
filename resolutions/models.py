"""Pydantic data models for the resolution tracker."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Goal(BaseModel):
  """A personal resolution or goal to track."""
  id: int
  title: str
  category: str = "general"  # fitness, learning, health, finance, etc.
  target: str = ""  # "3x per week", "daily", "12 books by Dec 31"
  created_at: datetime = Field(default_factory=datetime.now)
  priority: int = Field(default=3, ge=1, le=10)  # 1=highest, 10=lowest
  emoji: str = ""  # Visual indicator for the goal


class LogEntry(BaseModel):
  """A progress update for a goal."""
  id: int
  goal_id: int
  raw_input: str  # Original user text
  parsed_update: str = ""  # AI-extracted action
  value: Optional[float] = None  # Numeric value if applicable
  unit: str = ""  # "miles", "pages", "sessions", etc.
  timestamp: datetime = Field(default_factory=datetime.now)
  sentiment: str = "neutral"  # positive, neutral, struggling


class Config(BaseModel):
  """User configuration settings."""
  reminder_frequency: str = "daily"  # daily, weekly, adaptive
  preferred_time: str = "09:00"  # 24-hour format
  ai_personality: str = "balanced"  # encouraging, analytical, balanced


class GoalAnalysis(BaseModel):
  """AI-generated analysis for a goal."""
  goal_id: int
  category: str
  target: str
  priority: int
  emoji: str
  reasoning: str = ""


class LogAnalysis(BaseModel):
  """AI-generated analysis for a log entry."""
  goal_id: int
  parsed_update: str
  value: Optional[float] = None
  unit: str = ""
  sentiment: str


class DataStore(BaseModel):
  """Root data structure for JSON storage."""
  goals: list[Goal] = []
  logs: list[LogEntry] = []
  config: Config = Field(default_factory=Config)
  next_goal_id: int = 1
  next_log_id: int = 1
