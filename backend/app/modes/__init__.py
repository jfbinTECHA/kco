from .architect import ArchitectMode
from .coder import CoderMode
from .debugger import DebuggerMode
from .ask import AskMode

MODE_MAP = {
  "architect": ArchitectMode(),
  "coder": CoderMode(),
  "debugger": DebuggerMode(),
  "ask": AskMode(),
}