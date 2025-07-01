# GLOBAL_SCRIPTS – easy access to world-wide scripts

`evennia.GLOBAL_SCRIPTS` is a convenience container that lets you fetch or create *global* Script instances via attribute access – no searches, no IDs to remember.

A *global* Script is one that is **not attached to an object or account** (both `db_obj` and `db_account` are `None`).  Typical uses include weather daemons, timekeepers, resource spawners, or any long-running piece of game logic.

## 1. Declaring scripts via settings
Add to your game's `settings.py` (usually `mygame/server/conf/settings.py`):
```python
GLOBAL_SCRIPTS = {
    "weather": {
        "typeclass": "world.weather.WeatherScript",
        "interval": 60,          # custom attributes passed to .create()
        "start_delay": True,
    },
    "time": {
        "typeclass": "world.time.GameClock",
    },
}
```
Evennia will (re)create those scripts on startup and expose them as attributes on the container.

## 2. Access patterns
```python
from evennia import GLOBAL_SCRIPTS

# get script by attribute (preferred)
weather = GLOBAL_SCRIPTS.weather
weather.db.current_weather = "Stormy"

# fetch dynamically (e.g. variable key)
script = GLOBAL_SCRIPTS.get("time")

# iterate
for scr in GLOBAL_SCRIPTS.all():
    caller.msg(f"Found global script: {scr.key}")
```

Access is lazy; if the script does not yet exist but *is* listed in `settings.GLOBAL_SCRIPTS`, it will be auto-created on first access.

## 3. Creating at runtime
You may spawn a global script on the fly:
```python
from evennia import create_script, GLOBAL_SCRIPTS

scr = create_script("typeclasses.my.FestivalDaemon", key="festival")
GLOBAL_SCRIPTS.get("festival")  # now available
```
Or, more succinctly, rely on the settings entry so Evennia recreates it automatically after reloads.

## 4. Deleting / restarting
```python
GLOBAL_SCRIPTS.weather.stop()
GLOBAL_SCRIPTS.weather.delete()
# Next access GLOBAL_SCRIPTS.weather will auto-recreate it from settings dict.
```

## 5. When to use GLOBAL_SCRIPTS vs search_script()
* Use the container for *singleton* scripts you need often. It provides dot-access and auto-recovery.
* Use `search_script()` for ad-hoc lookups or when many instances share the same key.

## 6. Reference
See code and API docs: [`evennia.utils.containers.GlobalScriptContainer`](evennia.utils.containers.GlobalScriptContainer).