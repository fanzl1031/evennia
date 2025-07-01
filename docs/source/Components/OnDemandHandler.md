# OnDemandHandler – Efficient, event-driven timers

`ON_DEMAND_HANDLER` is a singleton located in `evennia.scripts.ondemandhandler`.  It lets you model time-based progressions (growth, cooldowns, aging, crafting, hunger …) **without** running real-time Scripts/tickers.  Work is only done the moment you *check* a task, so your server idles at 0 % CPU when nothing happens.

## 1. When to use it
* Entities that evolve over hours/days (plants, crops, brewing, construction)
* Cooldowns on abilities/items
* Long crafting jobs
* Environmental cycles (weather turning from drizzle → rain → storm) that matter only when someone looks

Not suitable when players must be notified *spontaneously* (e.g. heartbeat ‘you are starving!’ messages); use Scripts or tickers for that.

## 2. Creating a task
```python
from evennia import ON_DEMAND_HANDLER  # available after Evennia boot
from evennia.utils import gametime

stages = {
    0: "seedling",
    120: "sprouting",   # 2 min
    300: "blooming",    # 5 min
    600: "wilted",
    900: "dead",
}

plant = create_object(key="Rose Bush")
# key can be any str; using obj.dbref keeps it unique
ON_DEMAND_HANDLER.add(
    key=plant.dbref,
    category="plants",
    stages=stages,
)
```

`add()` returns the `OnDemandTask` instance; you can keep it or fetch it later with `get()`.

## 3. Checking progress
```python
stage = ON_DEMAND_HANDLER.get_stage(plant.dbref, category="plants")
if stage == "blooming":
    caller.msg("The rose bush is in full bloom – lovely scent!")
```

`get_dt()` returns seconds elapsed in current iteration – handy for progress bars.

## 4. Manipulating time
```python
# cheat 5 minutes forward (testing, spells, etc.)
ON_DEMAND_HANDLER.set_dt(plant.dbref, "plants", dt=300)

# or jump directly to a stage
ON_DEMAND_HANDLER.set_stage(plant.dbref, "plants", stage="blooming")
```

## 5. Looping or bouncing stages
Stage functions allow dynamic behaviour:
```python
from evennia.scripts.ondemandhandler import OnDemandTask

stages = {
    0: "red",
    5: ("green", OnDemandTask.stagefunc_bounce),  # bounce back & forth every 5 s
}
```
The handler now oscillates between 'red' and 'green' indefinitely.

## 6. Persistence & server restarts
`ON_DEMAND_HANDLER` automatically saves tasks into `ServerConfig` on shutdown and restores them on startup, including any looping counters.

## 7. Reference
Autodoc details all methods, kwargs and helper stage-functions: [`evennia.scripts.ondemandhandler`](evennia.scripts.ondemandhandler).
