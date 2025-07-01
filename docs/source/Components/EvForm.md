# EvForm – Text form templates

`EvForm` (evennia.utils.evform) lets you design rich, fixed-layout text UIs—character sheets, login banners, score screens—using a **template string** with tagged substitution fields.  Think of it as printf for multi-line ANSI art.

## 1. The idea

1. Draw your layout with ASCII / box-drawing characters.
2. Put `|`-delimited *tags* where dynamic data should appear.
3. Feed the template to `EvForm` along with a mapping of tag → value.

The resulting object behaves like a string (`str(evform)`), ready to `msg` to a Character or display in the webclient.

## 2. Minimal example
```python
from evennia.utils.evform import EvForm

_template = r"""
.————————————————————.
| Name : |name              |
| Class: |cls               |
| HP    |hp      / |hp_max  |
| MANA  |mp      / |mp_max  |
'————————————————————'
"""

form = EvForm(_template)
form.map({
    "name": "Diana",
    "cls": "Amazon",
    "hp": "35",
    "hp_max": "42",
    "mp": "12",
    "mp_max": "18",
})
caller.msg(form)
```

Would display:
```
.————————————————————.
| Name : Diana             |
| Class: Amazon            |
| HP    35      / 42       |
| MANA  12      / 18       |
'————————————————————'
```

## 3. Tags & modifiers

Tags take the form `|key[align][:format]` where

* **key** – lookup in the mapping you pass to `EvForm.map()`.
* **align** – one of `<`, `>`, `^` to left, right or center align inside the original field width.
* **format** – optional callable name available in `EvForm`'s formatter dict to post-process the value (e.g. colourising numbers).

Example with alignment:
```python
"|name^|"  # center name in the original placeholder width
```

Custom formatters:
```python
from evennia.utils.evform import EvForm

def hp_color(val):
    val = int(val)
    if val < 20:
        return "|r" + str(val) + "|n"
    return "|g" + str(val) + "|n"

form = EvForm(_template, funcs={"hpclr": hp_color})
form.map({"hp": "15"})  # tag |hpclr will apply colour function
```

## 4. Working with EvForm objects
```python
form = EvForm(template)
form.map(mapping)        # assign/update tags
form.unmap("hp")         # remove a tag so the placeholder shows again
print(form)              # => rendered form string
```

## 5. Use cases
* Character sheets & inspection windows
* Colorful login/info screens
* RPG battle HUDs
* Wizard/admin dashboards

## 6. Limitations & tips
1. Keep each line *exactly* the same length in the template—EvForm uses absolute positioning.
2. Use monospace fonts (the Evennia webclient and most terminals do).
3. For complex screens combine multiple `EvForm` instances side-by-side using `EvTable`.

## API reference
See the full autodoc for every attribute and helper: [`evennia.utils.evform`](evennia.utils.evform).