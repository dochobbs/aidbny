"""AI integration with Claude for intelligent resolution tracking."""

import json
import os
import re
from typing import Optional

from anthropic import Anthropic

from .models import Goal, LogEntry, GoalAnalysis, LogAnalysis


def _extract_json(text: str) -> dict:
  """Extract JSON from text, handling markdown code blocks."""
  # Try direct parse first
  text = text.strip()
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    pass

  # Try to extract from markdown code block
  patterns = [
    r'```json\s*(.*?)\s*```',
    r'```\s*(.*?)\s*```',
    r'\{[^{}]*\}',
  ]

  for pattern in patterns:
    match = re.search(pattern, text, re.DOTALL)
    if match:
      try:
        return json.loads(match.group(1) if '```' in pattern else match.group(0))
      except json.JSONDecodeError:
        continue

  raise json.JSONDecodeError("No valid JSON found", text, 0)


def get_client() -> Anthropic:
  """Get Anthropic client, raising error if API key not set."""
  api_key = os.environ.get("ANTHROPIC_API_KEY")
  if not api_key:
    raise ValueError(
      "ANTHROPIC_API_KEY environment variable not set. "
      "Add it to your ~/.zshrc or export it in your shell."
    )
  return Anthropic(api_key=api_key)


def _call_claude(prompt: str, system: str = "") -> str:
  """Make a call to Claude and return the response text."""
  client = get_client()
  message = client.messages.create(
    model="claude-3-5-haiku-20241022",
    max_tokens=1024,
    system=system if system else "You are a helpful assistant for tracking personal resolutions and goals.",
    messages=[{"role": "user", "content": prompt}],
  )
  return message.content[0].text


# Lucide-style Nerd Font glyphs for categories
CATEGORY_ICONS = {
  "fitness": "󰖽",      # nf-md-run
  "health": "󰺕",       # nf-md-heart-pulse
  "learning": "󰌢",     # nf-md-lightbulb
  "reading": "󰂺",      # nf-md-book-open
  "finance": "󰆩",      # nf-md-currency-usd
  "career": "󰊢",       # nf-md-briefcase
  "relationships": "󰙍", # nf-md-account-multiple
  "creativity": "󰏘",    # nf-md-palette
  "mindfulness": "󰒲",   # nf-md-meditation
  "productivity": "󱐋",  # nf-md-lightning-bolt
  "general": "󰓾",       # nf-md-target
  "ai-tools": "󰚩",      # nf-md-robot
}


def analyze_goal(title: str) -> GoalAnalysis:
  """Analyze a goal to extract category, target, and priority."""
  prompt = f"""Analyze this personal resolution/goal and extract structured information.

Goal: "{title}"

Return a JSON object with these fields:
- category: one of [fitness, health, learning, reading, finance, career, relationships, creativity, mindfulness, productivity, general]
- target: a measurable target extracted or inferred (e.g., "3x per week", "12 books", "daily")
- priority: 1-5 where 1 is highest priority (infer from urgency/importance)
- reasoning: brief explanation of your categorization

Return ONLY the JSON object, no other text."""

  try:
    response = _call_claude(prompt)
    data = _extract_json(response)
    category = data.get("category", "general")
    icon = CATEGORY_ICONS.get(category, CATEGORY_ICONS["general"])
    return GoalAnalysis(
      goal_id=0,  # Will be set by caller
      category=category,
      target=data.get("target", ""),
      priority=data.get("priority", 3),
      emoji=icon,
      reasoning=data.get("reasoning", ""),
    )
  except (json.JSONDecodeError, KeyError) as e:
    # Fallback to defaults
    return GoalAnalysis(
      goal_id=0,
      category="general",
      target="",
      priority=3,
      emoji=CATEGORY_ICONS["general"],
      reasoning=f"Could not analyze goal: {e}",
    )


def analyze_log(raw_input: str, goals: list[Goal]) -> LogAnalysis:
  """Parse a natural language log entry and match it to a goal."""
  if not goals:
    return LogAnalysis(
      goal_id=0,
      parsed_update=raw_input,
      sentiment="neutral",
    )

  goals_list = "\n".join([f"- ID {g.id}: {g.title} (category: {g.category})" for g in goals])

  prompt = f"""Parse this progress update and match it to the most relevant goal.

Update: "{raw_input}"

Available goals:
{goals_list}

Return a JSON object with:
- goal_id: the ID of the matching goal (integer)
- parsed_update: a clean summary of what was accomplished
- value: numeric value if mentioned (e.g., 3 for "ran 3 miles"), or null
- unit: unit of measurement if applicable (e.g., "miles", "pages", "minutes")
- sentiment: one of [positive, neutral, struggling] based on tone

Return ONLY the JSON object, no other text."""

  try:
    response = _call_claude(prompt)
    data = _extract_json(response)
    return LogAnalysis(
      goal_id=data.get("goal_id", goals[0].id),
      parsed_update=data.get("parsed_update", raw_input),
      value=data.get("value"),
      unit=data.get("unit", ""),
      sentiment=data.get("sentiment", "neutral"),
    )
  except (json.JSONDecodeError, KeyError):
    # Fallback: match to first goal
    return LogAnalysis(
      goal_id=goals[0].id if goals else 0,
      parsed_update=raw_input,
      sentiment="neutral",
    )


def generate_analysis(goals: list[Goal], logs: list[LogEntry],
                      specific_goal_id: Optional[int] = None) -> str:
  """Generate AI analysis of progress."""
  if not goals:
    return "No resolutions yet! Add some with `res add \"Your goal here\"`"

  # Build context
  if specific_goal_id:
    goals = [g for g in goals if g.id == specific_goal_id]
    logs = [l for l in logs if l.goal_id == specific_goal_id]

  goals_context = "\n".join([
    f"- {g.emoji} {g.title} (target: {g.target or 'not set'}, priority: {g.priority})"
    for g in goals
  ])

  logs_context = ""
  if logs:
    recent_logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:20]
    logs_context = "\n".join([
      f"- [{l.timestamp.strftime('%Y-%m-%d')}] Goal {l.goal_id}: {l.parsed_update or l.raw_input} ({l.sentiment})"
      for l in recent_logs
    ])
  else:
    logs_context = "No progress logged yet."

  prompt = f"""Analyze this user's resolution progress and provide helpful, encouraging insights.

Goals:
{goals_context}

Recent Activity:
{logs_context}

Provide:
1. Brief progress summary for each goal
2. Patterns you notice (good habits, areas needing attention)
3. Specific, actionable suggestions
4. Encouragement and motivation

Keep the tone warm but not overly effusive. Be specific and practical.
Format with clear sections. Keep it concise (under 300 words).
Do NOT use emojis - use plain text only."""

  system = """You are a supportive personal coach helping someone track their New Year's resolutions.
Be encouraging but honest. Focus on actionable insights. Do NOT use emojis - keep responses clean and text-only."""

  return _call_claude(prompt, system)


def generate_reminder(goals: list[Goal], logs: list[LogEntry]) -> str:
  """Generate a smart check-in reminder based on patterns."""
  if not goals:
    return "You haven't set any resolutions yet. Start with `res add \"Your goal\"`!"

  goals_context = "\n".join([
    f"- {g.emoji} {g.title} (priority: {g.priority})"
    for g in goals
  ])

  # Analyze recent activity
  recent_logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)[:10] if logs else []
  if recent_logs:
    logs_context = "\n".join([
      f"- [{l.timestamp.strftime('%Y-%m-%d')}] {l.parsed_update or l.raw_input}"
      for l in recent_logs
    ])
  else:
    logs_context = "No recent activity logged."

  prompt = f"""Generate a brief, personalized check-in prompt for this user.

Their goals:
{goals_context}

Recent activity:
{logs_context}

Create a friendly 2-3 sentence check-in that:
1. References their specific goals
2. Acknowledges recent progress (if any)
3. Asks a specific question about today's plans

Keep it conversational and motivating. Don't be preachy.
Do NOT use emojis - use plain text only."""

  system = "You are a friendly accountability partner. Be warm, specific, and brief. Do NOT use emojis."

  return _call_claude(prompt, system)
