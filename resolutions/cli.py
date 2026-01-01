"""CLI interface for the resolution tracker."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

from . import storage, ai

app = typer.Typer(
  name="res",
  help="AI-powered personal resolution tracker",
  no_args_is_help=False,
  invoke_without_command=True,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(
  ctx: typer.Context,
  demo: bool = typer.Option(False, "--demo", help="Launch with demo data"),
  tui: bool = typer.Option(False, "--tui", "-t", help="Launch interactive TUI dashboard"),
):
  """AI-powered personal resolution tracker.

  Run without arguments to launch the interactive dashboard.
  """
  if ctx.invoked_subcommand is None:
    # Default behavior: launch TUI
    from .app import run_app
    run_app(demo=demo)


@app.command()
def dashboard(
  demo: bool = typer.Option(False, "--demo", help="Load demo data for showcase"),
):
  """Launch the interactive TUI dashboard."""
  from .app import run_app
  run_app(demo=demo)


@app.command()
def add(
  title: str = typer.Argument(..., help="Your resolution or goal"),
  skip_ai: bool = typer.Option(False, "--no-ai", help="Skip AI categorization"),
):
  """Add a new resolution with AI categorization."""
  with console.status("[bold green]Analyzing your goal...") as status:
    if skip_ai:
      goal = storage.add_goal(title)
    else:
      try:
        analysis = ai.analyze_goal(title)
        goal = storage.add_goal(
          title=title,
          category=analysis.category,
          target=analysis.target,
          priority=analysis.priority,
          emoji=analysis.emoji,
        )
        status.stop()
        console.print(f"\n[green]Added:[/green] {goal.emoji} {goal.title}")
        console.print(f"  Category: [cyan]{goal.category}[/cyan] | Target: [cyan]{goal.target or 'not set'}[/cyan] | Priority: [cyan]{goal.priority}[/cyan]")
        if analysis.reasoning:
          console.print(f"  [dim]{analysis.reasoning}[/dim]")
        return
      except ValueError as e:
        status.stop()
        console.print(f"[yellow]AI unavailable:[/yellow] {e}")
        goal = storage.add_goal(title)

  console.print(f"\n[green]Added:[/green] {goal.title}")


@app.command(name="list")
def list_goals():
  """Show all resolutions with progress."""
  goals = storage.get_goals()
  if not goals:
    console.print("[yellow]No resolutions yet![/yellow] Add one with: res add \"Your goal here\"")
    return

  table = Table(title="Your Resolutions", box=box.ROUNDED)
  table.add_column("ID", style="dim", width=4)
  table.add_column("Goal", style="bold")
  table.add_column("Category", style="cyan")
  table.add_column("Target", style="green")
  table.add_column("Logs", justify="right")
  table.add_column("Priority", justify="center")

  for goal in sorted(goals, key=lambda g: g.priority):
    progress = storage.get_goal_progress(goal.id)
    priority_stars = "" * (6 - goal.priority)
    table.add_row(
      str(goal.id),
      f"{goal.emoji} {goal.title}",
      goal.category,
      goal.target or "-",
      str(progress["count"]),
      priority_stars,
    )

  console.print(table)


@app.command()
def log(
  update: str = typer.Argument(..., help="Your progress update in natural language"),
  goal_id: Optional[int] = typer.Option(None, "--goal", "-g", help="Specify goal ID (AI matches automatically if not provided)"),
):
  """Log progress with natural language."""
  goals = storage.get_goals()
  if not goals:
    console.print("[red]No resolutions to log against![/red] Add one first with: res add \"Your goal\"")
    raise typer.Exit(1)

  with console.status("[bold green]Parsing your update..."):
    if goal_id:
      # Manual goal specification
      goal = storage.get_goal(goal_id)
      if not goal:
        console.print(f"[red]Goal {goal_id} not found![/red]")
        raise typer.Exit(1)
      log_entry = storage.add_log(
        goal_id=goal_id,
        raw_input=update,
        parsed_update=update,
        sentiment="neutral",
      )
      matched_goal = goal
    else:
      # AI matching
      try:
        analysis = ai.analyze_log(update, goals)
        matched_goal = storage.get_goal(analysis.goal_id)
        if not matched_goal:
          matched_goal = goals[0]
        log_entry = storage.add_log(
          goal_id=matched_goal.id,
          raw_input=update,
          parsed_update=analysis.parsed_update,
          value=analysis.value,
          unit=analysis.unit,
          sentiment=analysis.sentiment,
        )
      except ValueError:
        # AI unavailable, use first goal
        matched_goal = goals[0]
        log_entry = storage.add_log(
          goal_id=matched_goal.id,
          raw_input=update,
          parsed_update=update,
          sentiment="neutral",
        )

  if log_entry:
    sentiment_icons = {"positive": "󰄬", "neutral": "󰏫", "struggling": "󱐋"}  # Lucide glyphs
    icon = sentiment_icons.get(log_entry.sentiment, "")
    console.print(f"\n[green]Logged to:[/green] {matched_goal.emoji} {matched_goal.title}")
    console.print(f"  {log_entry.parsed_update} {icon}")
    if log_entry.value:
      console.print(f"  Value: [cyan]{log_entry.value} {log_entry.unit}[/cyan]")
  else:
    console.print("[red]Failed to log entry![/red]")


@app.command()
def status():
  """Quick progress overview."""
  goals = storage.get_goals()
  if not goals:
    console.print("[yellow]No resolutions yet![/yellow] Add one with: res add \"Your goal here\"")
    return

  console.print()
  for goal in sorted(goals, key=lambda g: g.priority):
    progress = storage.get_goal_progress(goal.id)
    count = progress["count"]

    # Build a simple progress indicator
    filled = min(count, 10)
    bar = "" * filled + "" * (10 - filled)

    # Sentiment summary
    pos = progress.get("positive_count", 0)
    strug = progress.get("struggling_count", 0)
    sentiment_str = ""
    if pos > 0:
      sentiment_str = f" [green]+{pos}[/green]"
    if strug > 0:
      sentiment_str += f" [red]-{strug}[/red]"

    console.print(f"  {goal.emoji} [bold]{goal.title}[/bold]")
    console.print(f"     {bar} {count} logs{sentiment_str}")

  console.print()


@app.command()
def analyze(
  goal_id: Optional[int] = typer.Option(None, "--goal", "-g", help="Analyze specific goal"),
):
  """Get AI-powered analysis and insights."""
  goals = storage.get_goals()
  logs = storage.get_logs()

  with console.status("[bold green]Generating insights..."):
    try:
      analysis = ai.generate_analysis(goals, logs, goal_id)
    except ValueError as e:
      console.print(f"[red]AI unavailable:[/red] {e}")
      raise typer.Exit(1)

  console.print()
  console.print(Panel(analysis, title=" Progress Analysis", border_style="green"))
  console.print()


@app.command()
def remind():
  """Get a smart check-in reminder."""
  goals = storage.get_goals()
  logs = storage.get_logs()

  with console.status("[bold green]Crafting your check-in..."):
    try:
      reminder = ai.generate_reminder(goals, logs)
    except ValueError as e:
      console.print(f"[red]AI unavailable:[/red] {e}")
      raise typer.Exit(1)

  console.print()
  console.print(Panel(reminder, title=" Daily Check-in", border_style="blue"))
  console.print()


@app.command()
def edit(
  goal_id: int = typer.Argument(..., help="Goal ID to edit"),
  title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
  category: Optional[str] = typer.Option(None, "--category", "-c", help="New category"),
  target: Optional[str] = typer.Option(None, "--target", help="New target"),
  priority: Optional[int] = typer.Option(None, "--priority", "-p", help="New priority (1-5)"),
):
  """Edit an existing resolution."""
  goal = storage.get_goal(goal_id)
  if not goal:
    console.print(f"[red]Goal {goal_id} not found![/red]")
    raise typer.Exit(1)

  updates = {}
  if title:
    updates["title"] = title
  if category:
    updates["category"] = category
  if target:
    updates["target"] = target
  if priority:
    updates["priority"] = priority

  if not updates:
    console.print("[yellow]No changes specified.[/yellow] Use --title, --category, --target, or --priority")
    return

  updated = storage.update_goal(goal_id, **updates)
  if updated:
    console.print(f"[green]Updated:[/green] {updated.emoji} {updated.title}")
  else:
    console.print("[red]Update failed![/red]")


@app.command()
def remove(
  goal_id: int = typer.Argument(..., help="Goal ID to remove"),
  force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
  """Remove a resolution and its logs."""
  goal = storage.get_goal(goal_id)
  if not goal:
    console.print(f"[red]Goal {goal_id} not found![/red]")
    raise typer.Exit(1)

  if not force:
    confirm = typer.confirm(f"Remove '{goal.title}' and all its logs?")
    if not confirm:
      console.print("Cancelled.")
      return

  if storage.remove_goal(goal_id):
    console.print(f"[green]Removed:[/green] {goal.title}")
  else:
    console.print("[red]Remove failed![/red]")


@app.command()
def logs(
  goal_id: Optional[int] = typer.Option(None, "--goal", "-g", help="Filter by goal ID"),
  limit: int = typer.Option(10, "--limit", "-n", help="Number of logs to show"),
):
  """View recent log entries."""
  all_logs = storage.get_logs(goal_id)
  if not all_logs:
    console.print("[yellow]No logs yet![/yellow] Add one with: res log \"Your update\"")
    return

  # Sort by timestamp, most recent first
  sorted_logs = sorted(all_logs, key=lambda l: l.timestamp, reverse=True)[:limit]

  table = Table(title="Recent Logs", box=box.ROUNDED)
  table.add_column("Date", style="dim")
  table.add_column("Goal", style="cyan")
  table.add_column("Update")
  table.add_column("Mood", justify="center")

  goals = {g.id: g for g in storage.get_goals()}

  for log_entry in sorted_logs:
    goal = goals.get(log_entry.goal_id)
    goal_name = f"{goal.emoji} {goal.title[:20]}" if goal else f"Goal {log_entry.goal_id}"
    sentiment_icons = {"positive": "󰄬", "neutral": "󰏫", "struggling": "󱐋"}  # Lucide glyphs
    mood = sentiment_icons.get(log_entry.sentiment, "")

    table.add_row(
      log_entry.timestamp.strftime("%m/%d %H:%M"),
      goal_name,
      log_entry.parsed_update or log_entry.raw_input,
      mood,
    )

  console.print(table)


if __name__ == "__main__":
  app()
