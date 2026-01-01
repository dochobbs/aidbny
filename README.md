# Resolution Tracker

An AI-powered terminal dashboard for tracking your New Year's resolutions. Built for the [AI Daily Brief 10-Week Challenge](https://aidbnewyear.com).

```
╭──────────────────────────────────────────────────────────────────────────────╮
│  󰓾 AI MISSIONS                      │  󰚩 AI COACH                          │
│                                      │                                       │
│  󰓾 Week 1: Resolution Tracker       │  Welcome to the 10-Week AI Challenge! │
│     ████████████████ 100%            │  You're on Week 1. Let's build        │
│     ▁▂▃▅▇█▇  Build a tracker  󰈸4    │  something awesome!                   │
│                                      │                                       │
│  󰆋 Week 2: Model Mapping            │  ┌─────────────────────────────────┐  │
│     ░░░░░░░░░░░░░░░░   0%            │  │ 󰊠 Progress │ 󰛨 Motivate │ ...  │  │
│     ▁▁▁▁▁▁▁  Map AI models           │  └─────────────────────────────────┘  │
│                                      │                                       │
│  󰂖 Week 3: Deep Research            │  > Chat with your coach...            │
│     ░░░░░░░░░░░░░░░░   0%            │                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Features

- **Beautiful TUI** - Catppuccin color palette with Charm-inspired aesthetics
- **AI Coach** - Claude-powered coaching with smart suggestions
- **Mission Details** - Click any goal to see full briefing, tips, and resources
- **Progress Tracking** - Sparklines, progress bars, and streak counters
- **Natural Language Logging** - Just type what you did, AI matches it to goals
- **Lucide Glyphs** - Consistent Nerd Font icons throughout

## Quick Start

```bash
# Clone and install
git clone https://github.com/dochobbs/aidbny.git
cd aidbny
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Launch with demo data
res --demo
```

## Requirements

- Python 3.10+
- [Anthropic API key](https://console.anthropic.com/)
- Terminal with [Nerd Font](https://www.nerdfonts.com/) for icons (recommended)

## Usage

### Launch the Dashboard

```bash
res              # Interactive TUI
res --demo       # Load with 10-Week Challenge demo data
```

### CLI Commands

```bash
res add "Read 24 books this year"     # Add a goal (AI categorizes it)
res log "Finished chapter 5"          # Log progress (AI matches to goal)
res list                              # Show all goals
res status                            # Quick progress overview
res analyze                           # Get AI insights
res remind                            # Get a check-in prompt
```

### Keyboard Shortcuts (TUI)

| Key | Action |
|-----|--------|
| `a` | Add new goal |
| `l` | Log progress |
| `j/k` or `↑/↓` | Navigate goals |
| `Enter` or click | View mission details |
| `Tab` | Switch to chat |
| `?` | Help |
| `q` | Quit |

## The 10-Week AI Challenge

This tracker comes pre-loaded with the AI Daily Brief's 10-Week Challenge:

| Week | Mission | Goal |
|------|---------|------|
| 1 | Resolution Tracker | Build an AI-powered goal tracker |
| 2 | Model Mapping | Create your personal AI model guide |
| 3 | Deep Research | Master AI-assisted research |
| 4 | Data Analyst | Transform data into insights |
| 5 | Visual Reasoning | Explore multimodal AI |
| 6 | Information Pipelines | Build automated info flows |
| 7 | Automation: Distribution | Automate content distribution |
| 8 | Automation: Productivity | Supercharge your workflow |
| 9 | Context Engineering | Master prompting techniques |
| 10 | Build an AI App | Ship a complete AI application |

## Tech Stack

- **[Textual](https://textual.textualize.io/)** - Modern Python TUI framework
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal rendering
- **[Anthropic Claude](https://anthropic.com/)** - AI coaching (Haiku 3.5)
- **[Typer](https://typer.tiangolo.com/)** - CLI interface
- **[Pydantic](https://pydantic.dev/)** - Data validation

## Project Structure

```
resolutions/
├── app.py          # Main Textual application
├── ai.py           # Claude API integration
├── cli.py          # Typer CLI commands
├── models.py       # Pydantic data models
├── storage.py      # JSON persistence
└── widgets/        # Custom TUI components
    ├── goal_card.py
    ├── sparkline.py
    └── stats_bar.py
```

## Configuration

Data is stored in `~/.resolutions/data.json`. To reset:

```bash
rm ~/.resolutions/data.json
```

## License

MIT

---

Built with Claude Code for the AI Daily Brief 10-Week Challenge.
