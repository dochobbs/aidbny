"""Goal card widget displaying a single resolution."""

from textual.widget import Widget
from textual.widgets import Static, ProgressBar
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text

from ..models import Goal
from .sparkline import Sparkline


class GoalCard(Widget, can_focus=True):
  """A card displaying a goal with progress and sparkline."""

  DEFAULT_CSS = """
  GoalCard {
    height: auto;
    padding: 1;
    margin-bottom: 1;
    background: $surface;
    border: solid $primary-background;
    layout: vertical;
  }

  GoalCard:hover {
    background: $primary-background-darken-1;
  }

  GoalCard:focus {
    border: double $accent;
    background: $primary-background;
  }

  GoalCard .goal-header {
    layout: horizontal;
    height: 1;
    width: 100%;
  }

  GoalCard .goal-title {
    width: 1fr;
  }

  GoalCard .goal-percent {
    width: auto;
    text-align: right;
  }

  GoalCard .goal-details {
    layout: horizontal;
    height: 1;
    margin-top: 1;
  }

  GoalCard .goal-sparkline {
    width: auto;
    margin-right: 2;
  }

  GoalCard .goal-stats {
    width: 1fr;
  }

  GoalCard .goal-streak {
    width: auto;
    text-align: right;
  }

  GoalCard ProgressBar {
    margin-top: 1;
    padding: 0;
  }

  GoalCard Bar > .bar--bar {
    color: $success;
  }
  """

  class Selected(Message):
    """Posted when a goal card is selected."""
    def __init__(self, goal: Goal) -> None:
      self.goal = goal
      super().__init__()

  goal: reactive[Goal | None] = reactive(None)
  progress: reactive[float] = reactive(0.0)
  log_count: reactive[int] = reactive(0)
  streak: reactive[int] = reactive(0)
  sparkline_values: reactive[list[float]] = reactive(list)
  status: reactive[str] = reactive("on_track")  # on_track, behind, ahead

  def __init__(
    self,
    goal: Goal | None = None,
    progress: float = 0.0,
    log_count: int = 0,
    streak: int = 0,
    sparkline_values: list[float] | None = None,
    status: str = "on_track",
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
  ) -> None:
    super().__init__(name=name, id=id, classes=classes)
    self.goal = goal
    self.progress = progress
    self.log_count = log_count
    self.streak = streak
    self.sparkline_values = sparkline_values or []
    self.status = status

  def compose(self):
    """Compose the card layout."""
    if not self.goal:
      yield Static("No goal", classes="goal-title")
      return

    # Header row: emoji + title + percentage
    with Horizontal(classes="goal-header"):
      title = f"{self.goal.emoji} {self.goal.title}"
      yield Static(title, classes="goal-title")
      percent = f"[{'green' if self.progress >= 0.8 else 'yellow' if self.progress >= 0.5 else 'red'}]{int(self.progress * 100)}%[/]"
      yield Static(Text.from_markup(percent), classes="goal-percent")

    # Progress bar
    yield ProgressBar(total=100, show_eta=False, show_percentage=False)

    # Details row: sparkline + stats + streak
    with Horizontal(classes="goal-details"):
      yield Sparkline(values=self.sparkline_values, classes="goal-sparkline")

      # Stats (target or log count)
      stats_text = self.goal.target if self.goal.target else f"{self.log_count} logs"
      yield Static(f"[dim]{stats_text}[/]", classes="goal-stats", markup=True)

      # Streak
      if self.streak > 0:
        yield Static(f"[yellow]󰈸 {self.streak}d[/]", classes="goal-streak", markup=True)
      else:
        status_text = self._get_status_text()
        yield Static(status_text, classes="goal-streak", markup=True)

  def _get_status_text(self) -> str:
    """Get status indicator text."""
    if self.status == "ahead":
      return "[cyan]↑ Ahead[/]"
    elif self.status == "behind":
      return "[red]↓ Behind[/]"
    else:
      return "[green]✓ On track[/]"

  def on_mount(self) -> None:
    """Update progress bar on mount."""
    progress_bar = self.query_one(ProgressBar)
    progress_bar.update(progress=int(self.progress * 100))

  def watch_progress(self, new_progress: float) -> None:
    """Update progress bar when progress changes."""
    try:
      progress_bar = self.query_one(ProgressBar)
      progress_bar.update(progress=int(new_progress * 100))
    except Exception:
      pass

  def action_select(self) -> None:
    """Select this goal card."""
    if self.goal:
      self.post_message(self.Selected(self.goal))
