"""Sparkline widget for mini trend visualization."""

from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text


class Sparkline(Widget):
  """A mini sparkline chart widget."""

  DEFAULT_CSS = """
  Sparkline {
    height: 1;
    width: auto;
    min-width: 8;
  }
  """

  values: reactive[list[float]] = reactive(list)

  SPARK_CHARS = "▁▂▃▄▅▆▇█"

  def __init__(
    self,
    values: list[float] | None = None,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
  ) -> None:
    super().__init__(name=name, id=id, classes=classes)
    if values:
      self.values = values

  def render(self) -> Text:
    """Render the sparkline."""
    if not self.values:
      return Text("▁" * 7, style="dim")

    # Normalize values to 0-7 range (8 spark chars)
    min_val = min(self.values)
    max_val = max(self.values)
    value_range = max_val - min_val if max_val != min_val else 1

    spark = ""
    for v in self.values[-7:]:  # Last 7 values
      normalized = int((v - min_val) / value_range * 7)
      normalized = max(0, min(7, normalized))
      spark += self.SPARK_CHARS[normalized]

    # Pad to 7 chars if needed
    while len(spark) < 7:
      spark = "▁" + spark

    return Text(spark, style="cyan")
