"""Stats bar widget showing summary metrics."""

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


class StatsBar(Widget):
  """Bottom stats bar showing key metrics."""

  DEFAULT_CSS = """
  StatsBar {
    height: 1;
    width: 100%;
    background: $surface;
    padding: 0 2;
  }
  """

  total_logs: reactive[int] = reactive(0)
  streak_days: reactive[int] = reactive(0)
  weekly_score: reactive[int] = reactive(0)
  goals_on_track: reactive[int] = reactive(0)
  total_goals: reactive[int] = reactive(0)

  def render(self) -> RenderableType:
    """Render the stats bar."""
    parts = []

    # Logs this week
    parts.append(f"[dim]Logs:[/] [cyan]{self.total_logs}[/]")

    # Streak
    if self.streak_days > 0:
      parts.append(f"[dim]Streak:[/] [yellow]󰈸 {self.streak_days}d[/]")
    else:
      parts.append(f"[dim]Streak:[/] [dim]0d[/]")

    # Goals on track
    if self.total_goals > 0:
      parts.append(f"[dim]On Track:[/] [green]{self.goals_on_track}/{self.total_goals}[/]")

    # Weekly score
    score_color = "green" if self.weekly_score >= 80 else "yellow" if self.weekly_score >= 60 else "red"
    parts.append(f"[dim]Score:[/] [{score_color}]{self.weekly_score}%[/]")

    return Text.from_markup("  │  ".join(parts))
