"""Main Textual application for the Resolution Tracker TUI.

Inspired by Charm's bubbletea/lipgloss aesthetic:
- Generous whitespace
- Gradient accents
- Muted, cohesive color palette
- Clear visual hierarchy
"""

from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.widgets import Static, Header, Footer, Input, Button, Label
from textual.containers import Horizontal, Vertical, ScrollableContainer, Container
from textual.binding import Binding
from textual.screen import ModalScreen
from textual import on, work
from textual.reactive import reactive
from rich.text import Text
from rich.style import Style
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich import box

from . import storage, ai
from .models import Goal


# Color palette inspired by Charm/Catppuccin
COLORS = {
    "bg": "#1e1e2e",
    "surface": "#313244",
    "overlay": "#45475a",
    "text": "#cdd6f4",
    "subtext": "#a6adc8",
    "lavender": "#b4befe",
    "blue": "#89b4fa",
    "sapphire": "#74c7ec",
    "sky": "#89dceb",
    "teal": "#94e2d5",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "peach": "#fab387",
    "maroon": "#eba0ac",
    "red": "#f38ba8",
    "mauve": "#cba6f7",
    "pink": "#f5c2e7",
}

# Lucide-style Nerd Font glyphs
ICONS = {
    "target": "󰓾",      # nf-md-target
    "robot": "󰚩",       # nf-md-robot
    "flame": "󰈸",       # nf-md-fire
    "zap": "󱐋",         # nf-md-lightning-bolt
    "rocket": "󰀻",      # nf-md-rocket-launch
    "compass": "󰆋",     # nf-md-compass
    "flask": "󰂖",       # nf-md-flask/beaker
    "chart": "󰄧",       # nf-md-chart-bar
    "eye": "󰈈",         # nf-md-eye
    "sync": "󰕍",        # nf-md-sync
    "send": "󰕓",        # nf-md-send
    "tune": "󰒓",        # nf-md-tune/settings
    "check": "󰄬",       # nf-md-check-circle
    "thumbup": "󰔓",     # nf-md-thumb-up
    "sparkle": "󰛨",     # nf-md-star-shooting
    "note": "󰏫",        # nf-md-note-text
    "keyboard": "󰌌",    # nf-md-keyboard
    "diamond": "󰣏",     # nf-md-diamond-stone
    "checkmark": "󰄵",   # nf-md-check-bold
    "trophy": "󰆴",      # nf-md-trophy
    "arrow": "󰁔",       # nf-md-arrow-right
}

# AI Daily Brief 10-Week Challenge Mission Data
MISSIONS_DATA = {
    1: {
        "title": "Resolution Tracker",
        "subtitle": "Vibe code an AI-powered system to track your goals and keep you accountable.",
        "briefing": "Create a personal resolution tracker using AI. Design a system that helps you set, monitor, and achieve your goals throughout the year. Use natural language processing to log updates and get intelligent feedback on your progress.",
        "tips": [
            "Start with 3-5 specific, measurable resolutions",
            "Use AI to categorize and prioritize goals",
            "Set up automated check-in prompts",
            "Include sentiment analysis on your progress updates",
        ],
        "resources": ["ChatGPT or Claude for natural language interaction", "Notion AI for structured tracking", "Zapier for automation workflows"],
    },
    2: {
        "title": "Model Mapping",
        "subtitle": "Create your personal AI model guide - know which tools work best for what.",
        "briefing": "Develop a comprehensive map of AI models and their optimal use cases. Test different models with the same prompts, document their strengths and weaknesses, and create a personal reference guide for when to use each tool.",
        "tips": [
            "Test at least 5 different AI models",
            "Use consistent prompts across all models",
            "Document response time, accuracy, and style",
            "Create a decision tree for model selection",
        ],
        "resources": ["OpenAI GPT-4, Claude, Gemini, Llama", "Comparison frameworks and benchmarks", "Prompt libraries for testing"],
    },
    3: {
        "title": "Deep Research",
        "subtitle": "Master the art of AI-assisted deep research on any topic.",
        "briefing": "Pick a topic you're curious about and conduct thorough research using AI tools. Learn to verify sources, cross-reference information, and synthesize findings into a comprehensive report or presentation.",
        "tips": [
            "Choose a topic with multiple perspectives",
            "Use AI to find primary sources",
            "Cross-reference AI outputs with authoritative sources",
            "Create a structured research methodology",
        ],
        "resources": ["Perplexity AI for research", "Consensus for academic papers", "Elicit for literature reviews"],
    },
    4: {
        "title": "Data Analyst",
        "subtitle": "Transform raw data into insights using AI-powered analysis.",
        "briefing": "Find or create a dataset relevant to your interests and use AI tools to analyze it. Generate visualizations, identify patterns, and create a data story that communicates your findings effectively.",
        "tips": [
            "Start with a question you want to answer",
            "Clean your data before analysis",
            "Use multiple visualization types",
            "Document your analytical process",
        ],
        "resources": ["ChatGPT Code Interpreter", "Julius AI for data analysis", "Tableau or Observable for visualization"],
    },
    5: {
        "title": "Visual Reasoning",
        "subtitle": "Explore multimodal AI - analyze and create with images.",
        "briefing": "Work with AI vision capabilities to analyze images, extract information, and create visual content. Build a project that combines text and image understanding.",
        "tips": [
            "Test image analysis with different types of visuals",
            "Combine vision AI with text generation",
            "Explore image generation and editing",
            "Document accuracy and limitations",
        ],
        "resources": ["GPT-4 Vision, Claude Vision", "DALL-E, Midjourney, Stable Diffusion", "Google Lens for comparison"],
    },
    6: {
        "title": "Information Pipelines",
        "subtitle": "Build automated flows to gather, process, and deliver information.",
        "briefing": "Design and implement an information pipeline that automatically collects data from multiple sources, processes it with AI, and delivers insights in a useful format. Think of it as your personal AI news/research assistant.",
        "tips": [
            "Identify your information sources",
            "Define filtering and prioritization rules",
            "Set up summarization workflows",
            "Create a delivery schedule that works for you",
        ],
        "resources": ["Make.com or Zapier for automation", "RSS feeds and web scrapers", "AI summarization APIs"],
    },
    7: {
        "title": "Automation: Distribution",
        "subtitle": "Automate content creation and distribution across platforms.",
        "briefing": "Create an automated system that helps you create, adapt, and distribute content across multiple platforms. Learn to repurpose content efficiently while maintaining quality and authenticity.",
        "tips": [
            "Map your content distribution channels",
            "Create templates for different platforms",
            "Maintain your authentic voice",
            "Set up scheduling and cross-posting",
        ],
        "resources": ["Buffer, Hootsuite for scheduling", "Repurpose.io for content adaptation", "Canva AI for visual content"],
    },
    8: {
        "title": "Automation: Productivity",
        "subtitle": "Supercharge your daily workflow with AI automation.",
        "briefing": "Identify repetitive tasks in your work or personal life and create AI-powered automations to handle them. Focus on workflows that save significant time and reduce cognitive load.",
        "tips": [
            "Audit your tasks for automation potential",
            "Start with high-frequency, low-complexity tasks",
            "Build error handling into your automations",
            "Measure time saved",
        ],
        "resources": ["Notion AI, Coda AI", "Mac Shortcuts, Windows Power Automate", "Custom GPTs and Claude Projects"],
    },
    9: {
        "title": "Context Engineering",
        "subtitle": "Master the art of prompting and context design for better AI outputs.",
        "briefing": "Deep dive into advanced prompting techniques. Learn to structure context, create system prompts, use few-shot examples, and design prompts that consistently produce excellent results.",
        "tips": [
            "Study prompt engineering frameworks",
            "Create a personal prompt library",
            "Test systematic variations",
            "Document what works and why",
        ],
        "resources": ["OpenAI Prompt Engineering Guide", "Anthropic's Claude documentation", "DAIR.AI Prompt Engineering Guide"],
    },
    10: {
        "title": "Build an AI App",
        "subtitle": "Bring it all together - build a complete AI-powered application.",
        "briefing": "Apply everything you've learned to build a functional AI-powered application. This could be a tool for yourself, your community, or the world. Focus on solving a real problem.",
        "tips": [
            "Start with a specific problem to solve",
            "Keep the MVP scope small",
            "Use no-code/low-code tools if needed",
            "Get feedback from real users",
        ],
        "resources": ["Lovable for web apps", "Streamlit for data apps", "FlutterFlow for mobile"],
    },
}

# Suggested prompts for AI Coach (label, prompt, type)
COACH_PROMPTS = [
    ("󰊠 Progress", "analyze", "How am I doing on my goals?"),
    ("󰛨 Motivate", "remind", "Give me encouragement and a check-in"),
    ("󰆋 Focus", "analyze", "What should I focus on today?"),
    ("󰂖 Tips", "analyze", "Tips for my current mission"),
    ("󰈸 Streak", "analyze", "How's my streak looking?"),
    ("󱐋 Quick Win", "remind", "Suggest a quick win I can do right now"),
]


def make_gradient_bar(progress: float, width: int = 20) -> Text:
    """Create a gradient progress bar like lipgloss style."""
    filled = int(progress * width)
    empty = width - filled

    # Gradient from teal to green to yellow based on progress
    if progress >= 0.8:
        fill_color = COLORS["green"]
    elif progress >= 0.5:
        fill_color = COLORS["teal"]
    elif progress >= 0.3:
        fill_color = COLORS["yellow"]
    else:
        fill_color = COLORS["peach"]

    bar = Text()
    bar.append("█" * filled, style=fill_color)
    bar.append("░" * empty, style=COLORS["overlay"])
    return bar


def make_sparkline(values: list[float]) -> Text:
    """Create a sparkline with gradient coloring."""
    if not values:
        return Text("▁" * 7, style=COLORS["overlay"])

    chars = "▁▂▃▄▅▆▇█"
    min_v, max_v = min(values), max(values)
    rng = max_v - min_v if max_v != min_v else 1

    spark = Text()
    for i, v in enumerate(values[-7:]):
        idx = int((v - min_v) / rng * 7)
        idx = max(0, min(7, idx))
        # Color gradient based on position
        colors = [COLORS["blue"], COLORS["sapphire"], COLORS["sky"],
                  COLORS["teal"], COLORS["green"], COLORS["yellow"], COLORS["peach"]]
        color = colors[i % len(colors)]
        spark.append(chars[idx], style=color)

    return spark


class GoalWidget(Static, can_focus=True):
    """A beautifully styled goal card - click to see details."""

    def __init__(self, goal: Goal, progress: float, logs: int, streak: int,
                 sparkline_data: list[float], **kwargs):
        super().__init__(**kwargs)
        self.goal = goal
        self.progress = progress
        self.logs = logs
        self.streak = streak
        self.sparkline_data = sparkline_data
        # Cache the rendered content since it won't change
        self._cached_render: Text | None = None

    def on_click(self) -> None:
        """Open mission detail modal when clicked."""
        self.app.push_screen(MissionDetailModal(self.goal))

    def render(self) -> Text:
        """Render the goal with lipgloss-inspired styling (cached)."""
        if self._cached_render is not None:
            return self._cached_render

        g = self.goal

        # Build the card content
        lines = Text()

        # Title line with emoji
        lines.append(f" {g.emoji} ", style=f"bold")
        lines.append(f"{g.title}\n", style=f"bold {COLORS['text']}")

        # Progress bar with percentage
        pct = int(self.progress * 100)
        lines.append("    ")
        lines.append_text(make_gradient_bar(self.progress, 16))

        # Percentage with color
        pct_color = COLORS["green"] if pct >= 80 else COLORS["yellow"] if pct >= 50 else COLORS["peach"]
        lines.append(f" {pct:>3}%", style=pct_color)
        lines.append("\n")

        # Details line: sparkline + target + streak
        lines.append("    ")
        lines.append_text(make_sparkline(self.sparkline_data))
        lines.append(f"  ", style=COLORS["subtext"])

        if g.target:
            lines.append(f"{g.target}", style=COLORS["subtext"])
        else:
            lines.append(f"{self.logs} logs", style=COLORS["subtext"])

        if self.streak > 0:
            lines.append(f"  {ICONS['flame']}{self.streak}", style=COLORS["yellow"])

        self._cached_render = lines
        return lines


class StatsWidget(Static):
    """Bottom stats bar with clean styling."""

    def __init__(self, total_logs: int = 0, streak: int = 0,
                 on_track: int = 0, total: int = 0, **kwargs):
        super().__init__(**kwargs)
        self._total_logs = total_logs
        self._streak = streak
        self._on_track = on_track
        self._total = total

    def render(self) -> Text:
        t = Text()
        t.append("  ")

        # Logs
        t.append(f"{ICONS['diamond']} ", style=COLORS["blue"])
        t.append(f"{self._total_logs}", style=f"bold {COLORS['text']}")
        t.append(" logs  ", style=COLORS["subtext"])

        # Streak
        if self._streak > 0:
            t.append(f"{ICONS['flame']} ", style=COLORS["yellow"])
            t.append(f"{self._streak}d", style=f"bold {COLORS['text']}")
            t.append(" streak  ", style=COLORS["subtext"])

        # On track
        t.append(f"{ICONS['checkmark']} ", style=COLORS["green"])
        t.append(f"{self._on_track}/{self._total}", style=f"bold {COLORS['text']}")
        t.append(" on track", style=COLORS["subtext"])

        return t


class ChatMessage(Static):
    """A single chat message with nice styling."""

    def __init__(self, role: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.content = content

    def render(self) -> Text:
        t = Text()
        if self.role == "user":
            t.append("You › ", style=f"bold {COLORS['lavender']}")
        else:
            t.append("Coach › ", style=f"bold {COLORS['teal']}")
        t.append(self.content, style=COLORS["text"])
        return t


class AddModal(ModalScreen[str | None]):
    """Clean modal for adding goals."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Static(f"{ICONS['sparkle']} New Resolution", id="modal-title")
            yield Input(placeholder="What do you want to achieve?", id="goal-input")
            yield Static("[dim]Press Enter to add, Escape to cancel[/]", id="modal-hint")

    @on(Input.Submitted)
    def on_submit(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.dismiss(event.value.strip())

    def action_cancel(self) -> None:
        self.dismiss(None)


class LogModal(ModalScreen[str | None]):
    """Clean modal for quick logging."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Static(f"{ICONS['note']} Log Progress", id="modal-title")
            yield Input(placeholder="What did you do today?", id="log-input")
            yield Static("[dim]Press Enter to log, Escape to cancel[/]", id="modal-hint")

    @on(Input.Submitted)
    def on_submit(self, event: Input.Submitted) -> None:
        if event.value.strip():
            self.dismiss(event.value.strip())

    def action_cancel(self) -> None:
        self.dismiss(None)


class MissionDetailModal(ModalScreen[None]):
    """Modal showing full mission details when a goal is clicked."""

    BINDINGS = [Binding("escape", "close", "Close")]

    def __init__(self, goal: Goal, **kwargs):
        super().__init__(**kwargs)
        self.goal = goal

    def compose(self) -> ComposeResult:
        with Container(id="mission-modal"):
            yield ScrollableContainer(Static(self._render_mission()), id="mission-content")

    def _render_mission(self) -> Text:
        """Render the full mission details."""
        t = Text()
        g = self.goal

        # Extract week number from title (e.g., "Week 1: Resolution Tracker" -> 1)
        week_num = g.priority  # Priority matches week number in demo data

        mission = MISSIONS_DATA.get(week_num, {})

        # Header with emoji and title
        t.append(f"\n  {g.emoji}  ", style=f"bold")
        t.append(f"{g.title}\n", style=f"bold {COLORS['lavender']}")

        if mission:
            # Subtitle
            t.append(f"\n  {mission.get('subtitle', '')}\n", style=f"italic {COLORS['subtext']}")

            # Briefing section
            t.append(f"\n  {ICONS['target']} MISSION BRIEFING\n", style=f"bold {COLORS['teal']}")
            t.append(f"  ─────────────────────────\n", style=COLORS['overlay'])
            briefing = mission.get('briefing', '')
            # Wrap text for better display
            for line in self._wrap_text(briefing, 50):
                t.append(f"  {line}\n", style=COLORS['text'])

            # Tips section
            tips = mission.get('tips', [])
            if tips:
                t.append(f"\n  {ICONS['zap']} TIPS\n", style=f"bold {COLORS['yellow']}")
                t.append(f"  ─────────────────────────\n", style=COLORS['overlay'])
                for tip in tips:
                    t.append(f"  {ICONS['arrow']} ", style=COLORS['teal'])
                    t.append(f"{tip}\n", style=COLORS['text'])

            # Resources section
            resources = mission.get('resources', [])
            if resources:
                t.append(f"\n  {ICONS['flask']} RESOURCES\n", style=f"bold {COLORS['mauve']}")
                t.append(f"  ─────────────────────────\n", style=COLORS['overlay'])
                for res in resources:
                    t.append(f"  {ICONS['diamond']} ", style=COLORS['blue'])
                    t.append(f"{res}\n", style=COLORS['text'])
        else:
            # Fallback for custom goals
            t.append(f"\n  Target: {g.target or 'Not set'}\n", style=COLORS['subtext'])
            t.append(f"  Category: {g.category}\n", style=COLORS['subtext'])

        t.append(f"\n  [dim]Press Esc to close[/]\n")
        return t

    def _wrap_text(self, text: str, width: int) -> list[str]:
        """Simple text wrapping."""
        words = text.split()
        lines = []
        current = []
        length = 0
        for word in words:
            if length + len(word) + 1 > width:
                lines.append(' '.join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + 1
        if current:
            lines.append(' '.join(current))
        return lines

    def action_close(self) -> None:
        self.dismiss(None)


class HelpModal(ModalScreen[None]):
    """Help overlay with keyboard shortcuts."""

    BINDINGS = [Binding("escape", "close", "Close"), Binding("?", "close", "Close")]

    def compose(self) -> ComposeResult:
        with Container(id="help-container"):
            yield Static(self._render_help())

    def _render_help(self) -> Text:
        t = Text()
        t.append(f"\n  {ICONS['keyboard']}  Keyboard Shortcuts\n\n", style=f"bold {COLORS['lavender']}")

        shortcuts = [
            ("a", "Add new resolution"),
            ("l", "Log progress"),
            ("j/↓", "Next goal"),
            ("k/↑", "Previous goal"),
            ("Tab", "Switch to chat"),
            ("?", "This help"),
            ("q", "Quit"),
        ]

        for key, desc in shortcuts:
            t.append(f"  {key:<8}", style=f"bold {COLORS['teal']}")
            t.append(f"{desc}\n", style=COLORS["text"])

        t.append("\n  [dim]Press ? or Esc to close[/]\n")
        return t

    def action_close(self) -> None:
        self.dismiss(None)


class ResolutionApp(App):
    """Resolution Tracker with Charm-inspired aesthetics."""

    CSS = """
    Screen {
        background: #1e1e2e;
    }

    #main {
        layout: horizontal;
        height: 1fr;
        margin: 1 2;
    }

    #goals-panel {
        width: 1fr;
        height: 100%;
        border: round #45475a;
        padding: 1 2;
        margin-right: 1;
    }

    #goals-panel > Static:first-child {
        margin-bottom: 1;
    }

    #goals-list {
        height: 1fr;
    }

    GoalWidget {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: #313244;
        border: round #45475a;
    }

    GoalWidget:hover {
        background: #45475a;
        border: round #74c7ec;
    }

    GoalWidget:focus {
        background: #45475a;
        border: round #b4befe;
    }

    #chat-panel {
        width: 1fr;
        height: 100%;
        border: round #45475a;
        padding: 1 2;
    }

    #chat-title {
        margin-bottom: 1;
    }

    #chat-messages {
        height: 1fr;
        margin-bottom: 1;
    }

    ChatMessage {
        margin-bottom: 1;
    }

    #chat-input {
        dock: bottom;
        margin-top: 1;
    }

    #stats-bar {
        dock: bottom;
        height: 3;
        background: #313244;
        border-top: solid #45475a;
        padding: 1;
    }

    #modal-container {
        align: center middle;
        width: 50;
        height: auto;
        background: #313244;
        border: round #b4befe;
        padding: 2;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #modal-hint {
        text-align: center;
        margin-top: 1;
    }

    #help-container {
        align: center middle;
        width: 40;
        height: auto;
        background: #313244;
        border: round #b4befe;
        padding: 1;
    }

    #mission-modal {
        align: center middle;
        width: 70;
        height: auto;
        max-height: 80%;
        background: #313244;
        border: round #94e2d5;
        padding: 1 2;
    }

    #mission-content {
        height: auto;
        max-height: 100%;
    }

    #suggested-prompts {
        height: auto;
        margin-bottom: 1;
        padding: 0;
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1;
    }

    .prompt-btn {
        width: 100%;
        min-width: 12;
        height: 3;
        background: #45475a;
        border: round #585b70;
        color: #cdd6f4;
        text-align: center;
    }

    .prompt-btn:hover {
        background: #585b70;
        border: round #74c7ec;
    }

    .prompt-btn:focus {
        background: #74c7ec;
        color: #1e1e2e;
        border: round #89dceb;
    }

    Input {
        border: round #45475a;
        background: #1e1e2e;
        padding: 0 1;
    }

    Input:focus {
        border: round #b4befe;
    }

    Header {
        background: #313244;
    }

    Footer {
        background: #313244;
    }
    """

    TITLE = f"{ICONS['target']} AI Daily Brief - 10 Week Challenge"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("a", "add", "Add"),
        Binding("l", "log", "Log"),
        Binding("j", "next", "Next", show=False),
        Binding("k", "prev", "Prev", show=False),
        Binding("down", "next", show=False),
        Binding("up", "prev", show=False),
        Binding("tab", "focus_chat", "Chat"),
    ]

    def __init__(self, demo: bool = False):
        super().__init__()
        self.demo = demo
        self._chat_messages: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main"):
            # Goals panel
            with Vertical(id="goals-panel"):
                yield Static(Text(f"{ICONS['target']} AI MISSIONS", style=f"bold {COLORS['lavender']}"))
                yield ScrollableContainer(id="goals-list")

            # Chat panel
            with Vertical(id="chat-panel"):
                yield Static(Text(f"{ICONS['robot']} AI COACH", style=f"bold {COLORS['teal']}"), id="chat-title")
                yield ScrollableContainer(id="chat-messages")
                # Suggested prompts (grid layout)
                with Container(id="suggested-prompts"):
                    for i, (label, _, _) in enumerate(COACH_PROMPTS):
                        yield Button(label, id=f"prompt-{i}", classes="prompt-btn")
                yield Input(placeholder="Chat with your coach...", id="chat-input")

        yield StatsWidget(id="stats-bar")
        yield Footer()

    def on_mount(self) -> None:
        if self.demo:
            self._setup_demo()
        self._refresh_display()
        self._add_chat("assistant", f"Welcome to the 10-Week AI Challenge! {ICONS['target']} You're on Week 1: Resolution Tracker. Let's build something awesome!")

    def _setup_demo(self) -> None:
        """Load demo data with AI Daily Brief 10-Week Challenge."""
        import os
        data_file = storage.get_data_file()
        if data_file.exists():
            os.remove(data_file)

        # AI Daily Brief 10-Week AI Missions
        # https://aidbnewyear.com/program
        missions = [
            ("Week 1: Resolution Tracker", "ai-tools", "Build a tracker", 1, ICONS["target"]),
            ("Week 2: Model Mapping", "ai-tools", "Map AI models", 2, ICONS["compass"]),
            ("Week 3: Deep Research", "ai-tools", "Research project", 3, ICONS["flask"]),
            ("Week 4: Data Analyst", "ai-tools", "Analyze data", 4, ICONS["chart"]),
            ("Week 5: Visual Reasoning", "ai-tools", "Image analysis", 5, ICONS["eye"]),
            ("Week 6: Information Pipelines", "ai-tools", "Build pipeline", 6, ICONS["sync"]),
            ("Week 7: Automation: Distribution", "ai-tools", "Automate sharing", 7, ICONS["send"]),
            ("Week 8: Automation: Productivity", "ai-tools", "Boost productivity", 8, ICONS["zap"]),
            ("Week 9: Context Engineering", "ai-tools", "Master context", 9, ICONS["tune"]),
            ("Week 10: Build an AI App", "ai-tools", "Ship an app", 10, ICONS["rocket"]),
        ]

        for title, cat, target, pri, emoji in missions:
            storage.add_goal(title, cat, target, pri, emoji)

        # Add progress for Week 1 (we're doing it now!)
        logs = [
            (1, "Set up Python project with Textual", 1, "positive"),
            (1, "Built CLI with Typer", 1, "positive"),
            (1, "Added AI integration with Claude", 1, "positive"),
            (1, "Created TUI dashboard", 1, "positive"),
        ]
        for gid, update, val, sent in logs:
            storage.add_log(gid, update, update, val, "", sent)

    def _refresh_display(self) -> None:
        """Refresh goals and stats - loads data once."""
        goals_list = self.query_one("#goals-list", ScrollableContainer)
        goals_list.remove_children()

        # Load all data once
        goals = storage.get_goals()
        all_logs = storage.get_logs()

        # Pre-index logs by goal_id for O(1) lookup
        logs_by_goal: dict[int, list] = {}
        for log in all_logs:
            logs_by_goal.setdefault(log.goal_id, []).append(log)

        if not goals:
            goals_list.mount(Static(
                Text("\n  No resolutions yet!\n\n  Press [a] to add one.", style=COLORS["subtext"])
            ))
        else:
            for goal in sorted(goals, key=lambda g: g.priority):
                goal_logs = logs_by_goal.get(goal.id, [])
                log_count = len(goal_logs)
                progress = min(log_count / 10, 1.0)
                streak = self._calc_streak(goal_logs)
                sparkline = self._get_sparkline(goal_logs)

                widget = GoalWidget(
                    goal=goal,
                    progress=progress,
                    logs=log_count,
                    streak=streak,
                    sparkline_data=sparkline,
                )
                goals_list.mount(widget)

        # Update stats with already-loaded data
        self._update_stats(goals, all_logs)

    def _calc_streak(self, logs) -> int:
        if not logs:
            return 0
        dates = sorted(set(l.timestamp.date() for l in logs), reverse=True)
        if not dates:
            return 0
        today = datetime.now().date()
        if dates[0] < today - timedelta(days=1):
            return 0
        streak = 1
        for i in range(1, len(dates)):
            if dates[i] == dates[i-1] - timedelta(days=1):
                streak += 1
            else:
                break
        return streak

    def _get_sparkline(self, logs) -> list[float]:
        today = datetime.now().date()
        values = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_logs = [l for l in logs if l.timestamp.date() == day]
            values.append(sum(l.value or 1 for l in day_logs))
        return values

    def _update_stats(self, goals: list, logs: list) -> None:
        """Update stats bar with pre-loaded data."""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        weekly = [l for l in logs if l.timestamp > week_ago]

        three_days = now - timedelta(days=3)
        # Build set of goal_ids with recent activity for O(1) lookup
        recent_goal_ids = {l.goal_id for l in logs if l.timestamp > three_days}
        on_track = sum(1 for g in goals if g.id in recent_goal_ids)

        # Update stats widget
        stats = self.query_one("#stats-bar", StatsWidget)
        stats._total_logs = len(weekly)
        stats._on_track = on_track
        stats._total = len(goals)
        stats._streak = self._calc_streak(logs)
        stats.refresh()

    def _add_chat(self, role: str, content: str) -> None:
        self._chat_messages.append((role, content))
        container = self.query_one("#chat-messages", ScrollableContainer)
        container.mount(ChatMessage(role, content))
        container.scroll_end()

    def action_help(self) -> None:
        self.push_screen(HelpModal())

    def action_add(self) -> None:
        def on_add(result: str | None) -> None:
            if result:
                self._do_add(result)
        self.push_screen(AddModal(), on_add)

    @work(thread=True)
    def _do_add(self, title: str) -> None:
        try:
            analysis = ai.analyze_goal(title)
            goal = storage.add_goal(
                title, analysis.category, analysis.target,
                analysis.priority, analysis.emoji
            )
            self.call_from_thread(self._refresh_display)
            self.call_from_thread(
                self._add_chat, "assistant",
                f"Added {goal.emoji} **{goal.title}**! Target: {goal.target}"
            )
        except Exception:
            goal = storage.add_goal(title)
            self.call_from_thread(self._refresh_display)
            self.call_from_thread(self._add_chat, "assistant", f"Added: {title}")

    def action_log(self) -> None:
        def on_log(result: str | None) -> None:
            if result:
                self._do_log(result)
        self.push_screen(LogModal(), on_log)

    @work(thread=True)
    def _do_log(self, text: str) -> None:
        goals = storage.get_goals()
        if not goals:
            self.call_from_thread(
                self._add_chat, "assistant",
                "Add a goal first with [a]!"
            )
            return

        try:
            analysis = ai.analyze_log(text, goals)
            goal = storage.get_goal(analysis.goal_id) or goals[0]
            storage.add_log(
                goal.id, text, analysis.parsed_update,
                analysis.value, analysis.unit, analysis.sentiment
            )
            self.call_from_thread(self._refresh_display)
            icon = ICONS["check"] if analysis.sentiment == "positive" else ICONS["thumbup"]
            self.call_from_thread(
                self._add_chat, "assistant",
                f"{icon} Logged to {goal.emoji} {goal.title}!"
            )
        except Exception:
            goal = goals[0]
            storage.add_log(goal.id, text, text)
            self.call_from_thread(self._refresh_display)
            self.call_from_thread(self._add_chat, "assistant", f"Logged to {goal.title}")

    @on(Button.Pressed, ".prompt-btn")
    def on_prompt_btn(self, event: Button.Pressed) -> None:
        """Handle suggested prompt button clicks."""
        btn_id = event.button.id
        if btn_id and btn_id.startswith("prompt-"):
            idx = int(btn_id.split("-")[1])
            if 0 <= idx < len(COACH_PROMPTS):
                _, prompt_type, prompt_text = COACH_PROMPTS[idx]
                self._add_chat("user", prompt_text)
                self._handle_coach_prompt(prompt_type, prompt_text)

    @on(Input.Submitted, "#chat-input")
    def on_chat(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.clear()
        self._add_chat("user", text)
        self._handle_chat(text)

    @work(thread=True)
    def _handle_coach_prompt(self, prompt_type: str, text: str) -> None:
        """Handle coach prompts with proper AI function selection."""
        goals = storage.get_goals()
        logs = storage.get_logs()

        try:
            if prompt_type == "remind":
                response = ai.generate_reminder(goals, logs)
            else:  # "analyze" or default
                response = ai.generate_analysis(goals, logs)
            self.call_from_thread(self._add_chat, "assistant", response)
        except ValueError as e:
            self.call_from_thread(
                self._add_chat, "assistant",
                f"API key issue: {e}"
            )
        except Exception as e:
            self.call_from_thread(
                self._add_chat, "assistant",
                f"Connection error: {type(e).__name__}. Check your API key is set."
            )

    @work(thread=True)
    def _handle_chat(self, text: str) -> None:
        goals = storage.get_goals()
        logs = storage.get_logs()

        # Check if it's a log
        log_words = ["did", "finished", "completed", "ran", "read", "went"]
        if goals and any(w in text.lower() for w in log_words):
            self._do_log(text)
            return

        try:
            response = ai.generate_analysis(goals, logs)
            self.call_from_thread(self._add_chat, "assistant", response)
        except ValueError as e:
            self.call_from_thread(
                self._add_chat, "assistant",
                f"API key issue: {e}"
            )
        except Exception as e:
            self.call_from_thread(
                self._add_chat, "assistant",
                f"Connection error: {type(e).__name__}. Check your API key."
            )

    def action_next(self) -> None:
        pass  # TODO: goal navigation

    def action_prev(self) -> None:
        pass  # TODO: goal navigation

    def action_focus_chat(self) -> None:
        self.query_one("#chat-input", Input).focus()


def run_app(demo: bool = False) -> None:
    """Run the Resolution Tracker TUI."""
    app = ResolutionApp(demo=demo)
    app.run()
