# Evennia API Quick-Start & Practical Guide

> **Audience**  Developers who already have Evennia running and want a concise, copy-paste-ready reference to the public API and common workflows.

---

## 1  Project overview
Evennia is a full-featured text-MUD engine built on Django 5 & Twisted.  
It exposes a rich Python API for creating online multiplayer games, from high-level helpers such as `evennia.spawn()` to low-level session hooks.

```bash
# Install
pip install evennia           # or clone and install in editable mode
# Create and run a new game in the current directory
evennia --init mygame && cd mygame
evennia migrate
evennia start                 # Portal + Server start on default ports
```

---

## 2  Flat API (import-once convenience layer)
All names below become available after server start-up:

```python
from evennia import (
    # Creation helpers
    create_object, create_script, create_account,
    # Core typeclasses
    DefaultCharacter, DefaultRoom,
    # Handlers
    TICKER_HANDLER, SESSION_HANDLER,
    # Utilities
    ansi, spawn, logger, EvMenu,
)

room = create_object(DefaultRoom, key="Blue Room")
hero = create_object(DefaultCharacter, key="Diana", location=room)
```

| Category  | Public names (non-exhaustive)               | Quick note                                           |
|-----------|---------------------------------------------|------------------------------------------------------|
| Creation  | `create_object`, `create_script`, …         | Return fully-saved DB objects                        |
| Search    | `search_object`, `search_tag`, …            | Return querysets or lists                            |
| Typeclasses | `DefaultObject`, `DefaultCharacter`, …    | Sub-class for game logic                             |
| Handlers  | `TICKER_HANDLER`, `TASK_HANDLER`, …         | Global singletons                                    |
| Utilities | `ansi`, `spawn`, `logger`, `gametime`, …    | Coloring, prototyping, logging, timing              |

Full list: `help(evennia)` inside an `evennia shell`.

---

## 3  Typical workflows & examples

### 3.1  Object creation
```python
from evennia import create_object, DefaultCharacter, DefaultRoom

room = create_object(DefaultRoom, key="The Parthenon")
hero = create_object(DefaultCharacter, key="Diana", location=room)
hero.db.level = 1
```

### 3.2  Custom Command
```python
# mygame/commands/mycmds.py
from evennia import Command

class CmdWave(Command):
    """Wave to everyone in the same room."""
    key = "wave"

    def func(self):
        self.caller.location.msg_contents(f"{self.caller.key} waves.")
```
Attach it via a `CmdSet`:
```python
from evennia import CmdSet, DefaultCharacter

class CharacterCmdSet(CmdSet):
    key = "CharacterCmdSet"
    def at_cmdset_creation(self):
        self.add(CmdWave())

DefaultCharacter.cmdset.add_default(CharacterCmdSet, permanent=True)
```

### 3.3  Components system
```python
from evennia.contrib.base_systems.components import Component

class Health(Component):
    """Simple HP component."""
    health = 100
    def at_damage(self, amount):
        self.health -= amount
```
Attach: `goblin.components.add(Health)`.

### 3.4  Scheduler & ticker
```python
from evennia import TICKER_HANDLER

def tick(caller):
    caller.msg("⏰ Tick.")

TICKER_HANDLER.add(interval=60, callback=tick, idstring="status_tick", persistent=True)
```

---

## 4  REST & WebSocket endpoints
* REST root: `/api/` (OpenAPI schema at `/api/schema`).
* Webclient live at `/webclient/` and speaks WebSocket (`/ws`) with fallback to telnet.

---

## 5  Testing pattern
```bash
pip install '.[tests]'
pytest evennia/contrib/utils/random_string_generator/tests.py::TestRandomString
```

---

## 6  Building the documentation
The repository ships with Sphinx + MyST.

```bash
cd docs
pip install -r requirements.txt   # only once
make html                         # outputs to docs/build/html
open build/html/index.html
```

Autodoc stubs live under `docs/source/api/` and will be populated from docstrings at build time.

---

## 7  Release checklist
1. Bump version in `pyproject.toml` and `evennia/VERSION.txt`.  
2. Update `CHANGELOG.md`.  
3. Ensure `tox -e py311,docs` passes.  
4. Run `make release` to tag, push and publish to PyPI.

---

*Happy hacking & have fun with Evennia!*