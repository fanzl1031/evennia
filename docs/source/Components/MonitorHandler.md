# MonitorHandler – Reacting to model & Attribute changes

`MONITOR_HANDLER` from `evennia.scripts.monitorhandler` lets you attach callbacks that trigger **only when a specific DB field or Attribute value actually *changes***.  Use it to keep caches in sync, fire achievements, emit notifications, or enforce invariants—without polling.

## 1. Quick anatomy
A monitor is defined by:
* **obj** – the object or Attribute instance to watch.
* **fieldname** – either a model field (`db_key`, `db_location_id`, …) *or* an Attribute key.
* **idstring** – optional unique label so you can set multiple monitors on the same field.
* **callback** – callable `func(obj, fieldname, **kwargs)` executed post-save if value changed.
* **persistent** – if `True`, survives shutdowns (restored on reboot); otherwise survives reloads only.

## 2. Field monitor example
```python
from evennia import MONITOR_HANDLER

# 1. Define the reaction

def on_room_rename(obj, fieldname, **kwargs):
    old_name = kwargs.get("old")
    new_name = obj.key
    obj.msg_contents(f"|gThe room name changes from {old_name} to {new_name}.|n")

# 2. Attach monitor (e.g. in a Command after rename)
old = caller.location.key
MONITOR_HANDLER.add(
    obj=caller.location,
    fieldname="db_key",
    idstring="room_rename_broadcast",
    callback=on_room_rename,
    persistent=False,
    old=old,  # extra kwargs forwarded to callback
)
```
Whenever the room's `key` field is saved to a different value, everyone in the room sees the message.

## 3. Attribute monitor example
```python
from evennia import MONITOR_HANDLER

# Suppose every Character has an Attribute `hp`.

def low_hp_warning(obj, fieldname, **kwargs):
    if obj.db.hp < 10:
        obj.msg("|rYour health is critically low!|n")

MONITOR_HANDLER.add(
    obj=caller,
    fieldname="hp",        # Attribute name (no db_ prefix)
    category=None,          # set if Attribute categories used
    callback=low_hp_warning,
    idstring="warn_low_hp",
    persistent=True,
)
```

## 4. Listing & removing monitors
```python
# list all on an object
tasks = MONITOR_HANDLER.all(caller)

# remove a specific one
MONITOR_HANDLER.remove(caller, "hp", idstring="warn_low_hp")

# clear every monitor everywhere (rare!)
MONITOR_HANDLER.clear()
```

## 5. Persistence rules
Monitors with `persistent=True` survive *cold* restarts; non-persistent ones survive only soft reloads.  Sessions passed in `kwargs` are checked—if the session disappeared between restarts, its monitor is silently dropped.

## 6. Tips & gotchas
* **Do not** mutate the database inside the callback in a way that would immediately trigger the same monitor again—this could create recursion.
* For Attribute categories, pass `category="mycat"` when adding/removing.
* Callbacks must be *pickleable* (stand-alone or `@staticmethod`) so Evennia can serialize them.

## 7. Reference
See full API docs: [`evennia.scripts.monitorhandler`](evennia.scripts.monitorhandler).