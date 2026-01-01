"""AI Chat panel widget for conversational coaching."""

from textual.widget import Widget
from textual.widgets import Static, Input, RichLog
from textual.containers import Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.message import Message
from textual import on, work
from textual.worker import Worker, get_current_worker
from rich.text import Text
from rich.markdown import Markdown
from datetime import datetime


class AIChat(Widget):
  """AI coaching chat panel with conversation history."""

  DEFAULT_CSS = """
  AIChat {
    height: 100%;
    width: 100%;
    layout: vertical;
    padding: 0;
  }

  AIChat #chat-header {
    height: 2;
    padding: 0 1;
    background: $accent 20%;
    border-bottom: solid $accent;
  }

  AIChat #chat-messages {
    height: 1fr;
    padding: 1;
    scrollbar-gutter: stable;
  }

  AIChat #chat-input-container {
    height: auto;
    padding: 1;
    background: $surface;
    border-top: solid $primary-background;
  }

  AIChat #chat-input {
    width: 100%;
  }

  AIChat .message {
    margin-bottom: 1;
    padding: 1;
  }

  AIChat .message-user {
    background: $primary 20%;
    border-left: thick $primary;
  }

  AIChat .message-ai {
    background: $surface;
    border-left: thick $accent;
  }

  AIChat .message-header {
    text-style: bold;
    margin-bottom: 1;
  }

  AIChat .typing-indicator {
    color: $accent;
  }
  """

  is_typing: reactive[bool] = reactive(False)

  class MessageSent(Message):
    """Posted when user sends a message."""
    def __init__(self, text: str) -> None:
      self.text = text
      super().__init__()

  class ResponseReceived(Message):
    """Posted when AI response is received."""
    def __init__(self, text: str) -> None:
      self.text = text
      super().__init__()

  def __init__(
    self,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
  ) -> None:
    super().__init__(name=name, id=id, classes=classes)
    self._messages: list[dict] = []

  def compose(self):
    """Compose the chat layout."""
    yield Static("🤖 AI Coach", id="chat-header")

    with ScrollableContainer(id="chat-messages"):
      yield RichLog(id="chat-log", highlight=True, markup=True, wrap=True)

    with Vertical(id="chat-input-container"):
      yield Input(placeholder="Type a message... (Enter to send)", id="chat-input")

  def on_mount(self) -> None:
    """Initialize with welcome message."""
    self._add_ai_message(
      "Hey! I'm your AI coach. Tell me about your progress today, "
      "or ask me anything about your goals. 💪"
    )

  def _add_user_message(self, text: str) -> None:
    """Add a user message to the chat."""
    log = self.query_one("#chat-log", RichLog)
    log.write(Text.from_markup(f"[bold cyan]You:[/] {text}"))
    log.write("")
    self._messages.append({"role": "user", "content": text})

  def _add_ai_message(self, text: str) -> None:
    """Add an AI message to the chat."""
    log = self.query_one("#chat-log", RichLog)
    log.write(Text.from_markup(f"[bold magenta]Coach:[/] {text}"))
    log.write("")
    self._messages.append({"role": "assistant", "content": text})

  def _show_typing(self) -> None:
    """Show typing indicator."""
    log = self.query_one("#chat-log", RichLog)
    log.write(Text.from_markup("[dim italic]Coach is typing...[/]"))
    self.is_typing = True

  def _hide_typing(self) -> None:
    """Hide typing indicator by clearing last line."""
    self.is_typing = False

  @on(Input.Submitted, "#chat-input")
  def on_input_submitted(self, event: Input.Submitted) -> None:
    """Handle user input submission."""
    text = event.value.strip()
    if not text:
      return

    # Clear input
    event.input.clear()

    # Add user message
    self._add_user_message(text)

    # Post message for app to handle
    self.post_message(self.MessageSent(text))

  def add_response(self, text: str) -> None:
    """Add an AI response to the chat."""
    self._hide_typing()
    self._add_ai_message(text)

  def show_typing(self) -> None:
    """Show typing indicator."""
    self._show_typing()

  def get_conversation_history(self) -> list[dict]:
    """Get the conversation history for context."""
    return self._messages.copy()

  def clear_history(self) -> None:
    """Clear conversation history."""
    self._messages.clear()
    log = self.query_one("#chat-log", RichLog)
    log.clear()
    self._add_ai_message("Chat cleared. How can I help you today?")
