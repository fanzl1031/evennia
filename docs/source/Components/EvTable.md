# EvTable – Pretty, ANSI-aware ASCII tables

`EvTable` lives in `evennia.utils.evtable` and lets you build *beautiful*, fully-ANSI-compatible tables for use in the terminal and webclient.  It understands wrapping, alignment, arbitrary borders, and will auto-balance incomplete rows/columns so you never end up with jagged output.

```python title="minimal"
from evennia.utils import evtable

table = evtable.EvTable("Name", "HP", "MP")
table.add_row("Goblin", 35, 4)
table.add_row("Dark Wizard", 200, 350)
cave_entrance.msg(table)  # send nicely formatted table to a room/character
```

Result (with default border):

```
+-----------+-----+-----+
| Name      | HP  | MP  |
+===========+=====+=====+
| Goblin    |  35 |   4 |
| Dark Wiza | 200 | 350 |
+-----------+-----+-----+
```

## Feature highlights

* **Auto-sizing & auto-balancing** – supply as little or as much data as you want; EvTable will fill gaps so the table remains rectangular.
* **Per-column formatting** – width, alignment (`l`, `r`, `c`, `f`…), and padding can be set individually.
* **ANSI‐aware wrapping** – long texts wrap perfectly while preserving colour codes (`|rRed|n` won't bleed).
* **Unicode & custom borders** – change corners and edges or go borderless (`border=None`).

## Common recipes

### 1. Fixed width table
```python
table = evtable.EvTable("Key", "Description", table=[])
table.reformat(width=60)
```

### 2. Mixed fixed & auto columns
```python
table = evtable.EvTable("Slot", "Item", "Value", border="cells")
# Keep column 0 narrow, others auto-adjust
table.reformat_column(0, width=6, align="c")
```

### 3. Inline ANSI colours
```python
from evennia.utils.ansi import ANSIString as A

table = evtable.EvTable("Enemy", "Status")
table.add_row("|rOrc|n", A("|gAsleep|n"))
```

### 4. No borders (telnet-friendly)
```python
table = evtable.EvTable(border=None)
```

### 5. Multiline cells & wrapping
```python
lore = (
    "Here lies a very long piece of lore that should wrap across multiple lines "
    "but still be inside a single table cell."
)
table = evtable.EvTable("Lore")
table.add_row(lore)
table.reformat(width=50)
```

## API reference

The *complete* API, including `EvCell`, `EvColumn`, helper functions, and all keyword arguments is available in the autodoc page: [`evennia.utils.evtable`](evennia.utils.evtable).

---

*Tip:* For advanced layouts (nested tables, side-by-side stats blocks, etc.) you can override `EvTable`'s rendering methods or build small helper functions that return `EvTable` instances ready to print. Experiment!