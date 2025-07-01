# Evennia MUD Framework - API Documentation

This is comprehensive documentation for the Evennia MUD/MUX/MU* creation framework. Evennia is a modern, full-featured toolkit for creating text-based multiplayer games.

## Table of Contents

1. [Core Components](#core-components)
2. [Object System](#object-system)
3. [Command System](#command-system)
4. [Search Functions](#search-functions)
5. [Creation Functions](#creation-functions)
6. [Utility Components](#utility-components)
7. [Script System](#script-system)
8. [Account System](#account-system)
9. [Communication System](#communication-system)
10. [Examples and Usage](#examples-and-usage)

---

## Core Components

### Main Entry Point

```python
import evennia
```

The main `evennia` module provides access to all core components through a flat API structure.

#### Key Properties Available

- **DefaultObject** - Base object class for in-game entities
- **DefaultCharacter** - Base class for player characters  
- **DefaultRoom** - Base class for rooms/locations
- **DefaultExit** - Base class for exits between rooms
- **DefaultAccount** - Base class for player accounts
- **DefaultScript** - Base class for scripts/timers
- **DefaultChannel** - Base class for communication channels

#### Database Models

- **ObjectDB** - Database model for objects
- **AccountDB** - Database model for accounts
- **ScriptDB** - Database model for scripts
- **ChannelDB** - Database model for channels
- **Msg** - Database model for messages

#### Handlers

- **SESSION_HANDLER** - Manages client sessions
- **TASK_HANDLER** - Manages delayed/repeated tasks
- **TICKER_HANDLER** - Manages periodic tickers
- **GLOBAL_SCRIPTS** - Container for global scripts

---

## Object System

### DefaultObject Class

The base class for all in-game entities with physical presence.

```python
from evennia import DefaultObject

class MyObject(DefaultObject):
    """Custom object implementation"""
    pass
```

#### Core Properties

- `key` (str) - Object name/identifier
- `dbref` (int) - Unique database ID
- `location` (Object) - Current location
- `home` (Object) - Home/safety location  
- `contents` (list) - Objects inside this object
- `exits` (list) - Exit objects from this location
- `destination` (Object) - For exits, where they lead

#### Key Methods

##### Movement and Location

```python
# Move object to new location
obj.move_to(destination, quiet=False, emit_to_obj=None)

# Clear all contents
obj.clear_contents()

# Get contents with filtering
obj.contents_get(exclude=None, content_type=None)
```

##### Search and Access

```python
# Search for objects from this object's perspective
results = obj.search(searchdata, 
                    global_search=False,
                    use_nicks=True, 
                    typeclass=None,
                    location=None,
                    quiet=False,
                    exact=False)

# Check access permissions
has_access = obj.access(accessing_obj, access_type='read', default=False)
```

##### Messaging

```python
# Send message to object
obj.msg(text="Hello", from_obj=None, session=None)

# Send message to all contents
obj.msg_contents(text="Everyone sees this", 
                exclude=None, 
                from_obj=None,
                mapping=None)

# Execute command as this object
obj.execute_cmd("look", session=None)
```

##### Display and Appearance

```python
# Get display name for a looker
name = obj.get_display_name(looker=None)

# Get full appearance description
appearance = obj.return_appearance(looker)

# Format appearance with custom template
formatted = obj.format_appearance(appearance, looker)
```

#### Hooks (Override These)

```python
def at_object_creation(self):
    """Called once when object is first created"""
    pass

def at_object_delete(self):
    """Called before object deletion. Return False to abort."""
    return True

def at_init(self):
    """Called when object loads from database"""
    pass

def at_pre_move(self, destination):
    """Called before moving. Return False to abort."""
    return True

def at_post_move(self, source_location):
    """Called after successful move"""
    pass

def at_object_receive(self, obj, source_location):
    """Called when this object receives another object"""
    pass

def at_object_leave(self, obj, target_location):
    """Called when object leaves this location"""
    pass

def at_look(self, target):
    """Called when this object looks at something"""
    return target.return_appearance(self)

def at_get(self, getter):
    """Called when object is picked up"""
    pass

def at_drop(self, dropper):
    """Called when object is dropped"""
    pass
```

### DefaultCharacter Class

Extends DefaultObject for player-controlled characters.

```python
from evennia import DefaultCharacter

class Character(DefaultCharacter):
    """Custom character class"""
    
    def at_post_puppet(self):
        """Called when account connects to character"""
        self.msg("Welcome back!")
        
    def at_pre_unpuppet(self):
        """Called before account disconnects"""
        self.msg("Goodbye!")
```

#### Additional Character Properties

- `is_connected` (bool) - True if account is connected
- `has_account` (bool) - True if has associated account
- `is_superuser` (bool) - True if account is superuser
- `idle_time` (int) - Seconds since last command
- `connection_time` (int) - Seconds since connection

### DefaultRoom Class

Extends DefaultObject for locations/rooms.

```python
from evennia import DefaultRoom

class Room(DefaultRoom):
    """Custom room class"""
    
    def at_object_receive(self, obj, source_location):
        """Announce arrivals"""
        if obj.has_account:
            self.msg_contents(f"{obj.name} arrives.", exclude=[obj])
```

### DefaultExit Class  

Extends DefaultObject for connections between rooms.

```python
from evennia import DefaultExit

class Exit(DefaultExit):
    """Custom exit class"""
    
    def at_traverse(self, traversing_object, target_location):
        """Handle traversal with custom logic"""
        if not traversing_object.access(self, 'traverse'):
            traversing_object.msg("You cannot go that way.")
            return False
        return traversing_object.move_to(target_location)
```

---

## Command System

### Command Class

Base class for all commands in Evennia.

```python
from evennia import Command

class CmdLook(Command):
    """
    Look at something
    
    Usage:
        look [target]
        
    Look at your location or a specific target.
    """
    
    key = "look"
    aliases = ["l", "examine"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        """Main command logic"""
        if not self.args:
            # Look at location
            self.caller.msg(self.caller.location.return_appearance(self.caller))
        else:
            # Look at target
            target = self.caller.search(self.args)
            if target:
                self.caller.msg(self.caller.at_look(target))
```

#### Command Properties

- `key` (str) - Primary command name
- `aliases` (list) - Alternative command names
- `locks` (str) - Permission requirements
- `help_category` (str) - Help system category
- `auto_help` (bool) - Auto-generate help text

#### Available in Commands

- `self.caller` - Object executing command
- `self.args` - Arguments after command name
- `self.cmdstring` - Exact command name used
- `self.raw_string` - Full input string
- `self.session` - Session that sent command

#### Command Methods

```python
def parse(self):
    """Parse arguments before func()"""
    pass

def func(self):
    """Main command logic - override this"""
    pass

def at_pre_cmd(self):
    """Called before parse(). Return False to abort."""
    pass

def at_post_cmd(self):
    """Called after func()"""
    pass
```

#### Utility Methods

```python
# Send message (shortcut for caller.msg)
self.msg("Message text")

# Execute another command
self.execute_cmd("look north")

# Access styled table helper
table = self.styled_table("Header1", "Header2")
table.add_row("data1", "data2")
self.msg(table)

# Get client width for formatting
width = self.client_width()
```

### CmdSet Class

Groups related commands together.

```python
from evennia import CmdSet

class MyCmdSet(CmdSet):
    """Custom command set"""
    
    key = "mycmdset"
    
    def at_cmdset_creation(self):
        """Add commands to set"""
        self.add(CmdLook())
        self.add(CmdSay())
        self.add(CmdInventory())
```

---

## Search Functions

### Object Search

```python
from evennia.utils import search

# Search for objects
results = search.search_object(
    key="sword",                    # Search term
    location=room,                  # Limit to location
    typeclass="weapons.Sword",      # Filter by typeclass
    tags=["weapon", "metal"],       # Filter by tags
    exact=False,                    # Partial matching
    candidates=None                 # Pre-filtered candidates
)

# Search by attributes
results = search.search_object_attribute(
    key="material",
    value="steel"
)

# Search by tags
results = search.search_object_by_tag(
    key="weapon",
    category="item_type"
)

# Search by typeclass
results = search.search_objects_by_typeclass(
    typeclass="typeclasses.objects.Weapon",
    include_children=True
)
```

### Account Search

```python
# Search for accounts
accounts = search.search_account("PlayerName")

# Search by account attributes
accounts = search.search_account_attribute(
    key="email",
    value="player@example.com"
)
```

### Script Search  

```python
# Search for scripts
scripts = search.search_script(
    key="heartbeat",
    obj=character,                  # Scripts on specific object
    typeclass="scripts.Heartbeat"
)
```

### Communication Search

```python
# Search channels
channels = search.search_channel("general")

# Search messages
messages = search.search_message(
    sender=account,
    channel=channel,
    date=datetime.now()
)
```

### Help Search

```python
# Search help entries
help_entries = search.search_help(
    key="combat",
    category="Tutorial"
)
```

---

## Creation Functions

### Object Creation

```python
from evennia.utils import create

# Create basic object
obj = create.create_object(
    typeclass="typeclasses.objects.Object",
    key="Sword",
    location=room,
    home=room,
    attributes=[("weight", 5), ("material", "steel")],
    tags=[("weapon", "item_type"), ("sharp", "properties")],
    locks="get:all();drop:all()",
    aliases=["blade", "weapon"]
)

# Create character
char = create.create_object(
    typeclass="typeclasses.characters.Character", 
    key="Hero",
    location=start_room,
    permissions=["Builder"]
)

# Create room
room = create.create_object(
    typeclass="typeclasses.rooms.Room",
    key="Forest Clearing",
    attributes=[("desc", "A peaceful clearing in the woods.")]
)

# Create exit
exit = create.create_object(
    typeclass="typeclasses.exits.Exit",
    key="north",
    aliases=["n"],
    location=room1,
    destination=room2
)
```

### Account Creation

```python
# Create account
account = create.create_account(
    key="PlayerName",
    email="player@example.com", 
    password="secret123",
    permissions=["Player"],
    typeclass="typeclasses.accounts.Account"
)
```

### Script Creation

```python
# Create script
script = create.create_script(
    typeclass="scripts.Heartbeat",
    key="character_heartbeat",
    obj=character,
    interval=60,                    # Run every 60 seconds
    repeats=0,                      # Infinite repeats
    start_delay=False,              # Start immediately
    persistent=True,                # Survive restarts
    autostart=True,                 # Start when created
    attributes=[("rate", "normal")]
)
```

### Channel Creation

```python
# Create communication channel
channel = create.create_channel(
    key="newbie",
    aliases=["n"],
    desc="Channel for new players",
    locks="listen:all();send:all()",
    keep_log=True
)
```

### Help Entry Creation

```python
# Create help entry
help_entry = create.create_help_entry(
    key="combat",
    entrytext="Combat in this game involves...",
    category="Tutorial", 
    aliases=["fighting", "battle"],
    locks="view:all()"
)
```

### Message Creation

```python
# Create message
msg = create.create_message(
    senderobj=sender,
    message="Hello there!",
    receivers=[receiver1, receiver2],
    header="chat"
)
```

---

## Utility Components

### EvMenu - Interactive Menu System

Create complex menu-driven interfaces.

```python
from evennia.utils.evmenu import EvMenu

# Simple menu definition (in separate module)
def start_node(caller):
    """Main menu node"""
    text = "Welcome to the character creator!"
    options = (
        {"desc": "Create new character", "goto": "create_char"},
        {"desc": "Load existing character", "goto": "load_char"},
        {"desc": "Exit", "goto": "quit_menu"}
    )
    return text, options

def create_char(caller, raw_string):
    """Character creation node"""
    text = "Enter character name:"
    options = {"key": "_default", "goto": ("save_name", {"input": raw_string})}
    return text, options

# Start menu
EvMenu(caller, "path.to.menu_module", startnode="start_node")

# Template-based menu
menu_template = """
## node start
Welcome! Choose an option:

## options
1: First Choice -> node1
2: Second Choice -> node2
quit: Exit Menu -> quit

## node node1
You chose option 1!

## options
back: Go Back -> start
"""

from evennia.utils.evmenu import template2menu
template2menu(caller, menu_template)
```

### EvTable - Advanced Table Creation

Create formatted tables with borders, colors, and alignment.

```python
from evennia.utils.evtable import EvTable

# Basic table
table = EvTable("Name", "Level", "Class")
table.add_row("Alice", "5", "Warrior")
table.add_row("Bob", "3", "Mage")
table.add_row("Charlie", "7", "Rogue")

# Table with options
table = EvTable("Header1", "Header2", 
                border="cells",           # Border style
                width=50,                 # Table width
                align="c")                # Center alignment

# Add data
table.add_column("Col3", "Col4")
table.add_row("Data", "More Data", "Even More", "Final")

# Reformat specific column
table.reformat_column(1, width=20, align="r")

print(table)  # Display table
```

### EvMore - Paginated Output

Display long text with automatic pagination.

```python
from evennia.utils.evmore import EvMore

long_text = "Very long text that needs pagination..."

# Simple pagination  
EvMore(caller, long_text)

# With options
EvMore(caller, long_text, 
       session=session,
       justify_kwargs={"width": 70, "align": "c"})
```

### EvEditor - Text Editor

Provide in-game text editing capabilities.

```python
from evennia.utils.eveditor import EvEditor

def save_callback(caller, buffer):
    """Called when editor saves"""
    caller.db.story = buffer
    caller.msg("Story saved!")

# Start editor
EvEditor(caller, 
         loadfunc=lambda caller: caller.db.story or "",
         savefunc=save_callback,
         quitfunc=lambda caller: caller.msg("Editor closed."),
         key="story")
```

### EvForm - Form Creation

Create structured input forms.

```python
from evennia.utils.evform import EvForm

# Form template
form_template = """
.------------------------------------------------.
|                Character Sheet                 |
|                                                |
| Name: [XXXXXXXXXXXXXXXXXXXXXXX]                |
| Race: [XXXXXXXXXXX]                            |
| Class: [XXXXXXXXXXX]                           |
|                                                |
| STR: [XXX]  DEX: [XXX]  CON: [XXX]            |
| INT: [XXX]  WIS: [XXX]  CHA: [XXX]            |
|                                                |
'------------------------------------------------'
"""

# Create form
form = EvForm("path.to.form_template")

# Add cells
form.map_cell("A", "name", width=23)
form.map_cell("B", "race", width=11) 
form.map_cell("C", "class", width=11)
form.map_cell("D", "str", width=3)

# Display
caller.msg(form)
```

### Input Helpers

Get single-line input or yes/no confirmation.

```python
from evennia.utils.evmenu import get_input, ask_yes_no

# Get text input
def handle_input(caller, prompt, input_text):
    caller.msg(f"You entered: {input_text}")

get_input(caller, "Enter your name: ", handle_input)

# Yes/No question
def handle_response(caller, response):
    if response:
        caller.msg("You said yes!")
    else:
        caller.msg("You said no!")

ask_yes_no(caller, "Do you want to continue?", 
           yes_action=lambda c: handle_response(c, True),
           no_action=lambda c: handle_response(c, False))
```

---

## Script System

### DefaultScript Class

Scripts are objects that can run code at timed intervals.

```python
from evennia import DefaultScript

class HeartbeatScript(DefaultScript):
    """
    A script that runs every few seconds
    """
    
    def at_script_creation(self):
        """Configure script at creation"""
        self.key = "heartbeat"
        self.desc = "Character heartbeat"
        self.interval = 60  # 60 seconds
        self.repeats = 0    # Infinite
        self.persistent = True  # Survive restarts
        
    def at_repeat(self):
        """Called every interval"""
        if self.obj:  # Script attached to an object
            self.obj.msg("*thump*")
            
    def is_valid(self):
        """Return False to stop script"""
        return self.obj and self.obj.location
        
    def at_start(self):
        """Called when script starts"""
        self.obj.msg("Heart starts beating.")
        
    def at_stop(self):
        """Called when script stops"""
        self.obj.msg("Heart stops beating.")

# Create and start script
script = create.create_script(HeartbeatScript, obj=character)
```

#### Script Properties

- `key` (str) - Script identifier
- `interval` (int) - Seconds between calls
- `repeats` (int) - Number of repeats (0 = infinite)
- `persistent` (bool) - Survive server restarts
- `obj` (Object) - Object script is attached to
- `account` (Account) - Account script is attached to

#### Script Control

```python
# Start/restart script
script.start(interval=30, repeats=10)

# Pause script
script.pause()

# Unpause script
script.unpause()

# Stop script
script.stop()

# Force immediate execution
script.force_repeat()

# Check status
is_running = script.ndb._task and script.ndb._task.running

# Time until next run
time_left = script.time_until_next_repeat()

# Remaining repeats
remaining = script.remaining_repeats()
```

### Global Scripts

Scripts not attached to any specific object.

```python
class ServerMaintenance(DefaultScript):
    """Global server maintenance script"""
    
    def at_script_creation(self):
        self.key = "server_maintenance"
        self.interval = 3600  # Every hour
        self.persistent = True
        
    def at_repeat(self):
        # Perform maintenance tasks
        from evennia import GLOBAL_SCRIPTS
        total_objects = len(GLOBAL_SCRIPTS.objects.all())
        print(f"Server has {total_objects} objects")

# Create global script  
script = create.create_script(ServerMaintenance)
```

---

## Account System

### DefaultAccount Class

Represents a player account that can control characters.

```python
from evennia import DefaultAccount

class Account(DefaultAccount):
    """Custom account class"""
    
    def at_account_creation(self):
        """Called when account is first created"""
        self.msg("Welcome to the game!")
        
    def at_pre_login(self):
        """Called before login"""
        pass
        
    def at_post_login(self, session=None):
        """Called after successful login"""
        self.msg("Login successful!")
        
    def at_disconnect(self, reason=None):
        """Called when disconnecting"""
        self.msg("Goodbye!")
```

#### Account Properties

- `key` (str) - Account name
- `email` (str) - Email address
- `is_superuser` (bool) - Superuser status
- `characters` (list) - Characters owned by account
- `sessions` (QuerySet) - Active sessions
- `last_login` (datetime) - Last login time

#### Account Methods

```python
# Create new character
char = account.create_character(
    key="NewCharacter",
    typeclass="typeclasses.characters.Character"
)

# Get characters
chars = account.db._playable_characters

# Puppet character
account.puppet_object(session, character)

# Check available character slots
available = account.check_available_slots()

# Search for objects as account
results = account.search("target")

# Send message to account
account.msg("Account message")
```

### Session Management

```python
# Get sessions
sessions = account.sessions.all()

# Session properties
for session in sessions:
    print(f"Session {session.sessid}")
    print(f"Address: {session.address}")
    print(f"Protocol: {session.protocol}")
    print(f"Idle: {session.idle_time}")
    print(f"Connected: {session.connection_time}")

# Send to specific session
account.msg("Message", session=session)
```

---

## Communication System

### Channels

Persistent communication channels for groups.

```python
from evennia import DefaultChannel

class CustomChannel(DefaultChannel):
    """Custom channel with additional features"""
    
    def at_channel_creation(self):
        """Configure channel at creation"""
        self.locks.add("listen:all();send:all()")
        
    def at_pre_send_message(self, message):
        """Filter messages before sending"""
        # Block messages with certain words
        if "badword" in message.lower():
            return False
        return True
        
    def at_post_send_message(self, message):
        """Called after message sent"""
        # Log all messages
        print(f"Channel {self.key}: {message}")

# Create channel
channel = create.create_channel(
    key="general",
    desc="General discussion channel",
    aliases=["gen", "g"]
)

# Subscribe account to channel
channel.connect(account)

# Send message to channel
channel.msg("Hello everyone!", senders=[account])

# Unsubscribe
channel.disconnect(account)
```

### Messages

Persistent messages between entities.

```python
# Send message
msg = create.create_message(
    senderobj=sender_account,
    message="Hello there!",
    receivers=[receiver_account],
    header="tell"
)

# Message properties
print(msg.message)      # Message text
print(msg.date_sent)    # When sent
print(msg.senders)      # Who sent it
print(msg.receivers)    # Who received it

# Search messages
messages = search.search_message(
    sender=account,
    receiver=account,
    freetext="hello"
)
```

---

## Examples and Usage

### Basic Object Creation and Interaction

```python
# Create a weapon object
sword = create.create_object(
    typeclass="typeclasses.objects.Weapon",
    key="Iron Sword",
    location=character,
    attributes=[
        ("damage", 10),
        ("weight", 5),
        ("durability", 100)
    ],
    tags=[("weapon", "type"), ("metal", "material")]
)

# Move it to a room
sword.move_to(room)

# Character picks it up
if sword.access(character, "get"):
    sword.move_to(character)
    character.msg(f"You pick up {sword.get_display_name(character)}.")
```

### Command with Complex Parsing

```python
class CmdGive(Command):
    """
    Give an item to someone
    
    Usage:
        give <item> to <target>
        give <item> = <target>
    """
    
    key = "give"
    locks = "cmd:all()"
    
    def parse(self):
        """Parse 'item to target' or 'item = target'"""
        self.item = None
        self.target = None
        
        if " to " in self.args:
            self.item, self.target = self.args.split(" to ", 1)
        elif " = " in self.args:
            self.item, self.target = self.args.split(" = ", 1)
        else:
            self.caller.msg("Usage: give <item> to <target>")
            return
            
        self.item = self.item.strip()
        self.target = self.target.strip()
    
    def func(self):
        if not self.item or not self.target:
            self.caller.msg("Give what to whom?")
            return
            
        # Find item in inventory
        item = self.caller.search(self.item, 
                                 location=self.caller,
                                 nofound_string="You don't have that.")
        if not item:
            return
            
        # Find target
        target = self.caller.search(self.target)
        if not target:
            return
            
        # Check if target can receive items
        if not target.access(self.caller, "give"):
            self.caller.msg("You cannot give items to that.")
            return
            
        # Perform the give
        if item.move_to(target):
            self.caller.msg(f"You give {item.name} to {target.name}.")
            target.msg(f"{self.caller.name} gives you {item.name}.")
        else:
            self.caller.msg("You cannot give that away.")
```

### Room with Special Features

```python
class MagicRoom(DefaultRoom):
    """A room with magical properties"""
    
    def at_object_receive(self, obj, source_location):
        """Welcome message for characters"""
        if obj.has_account:
            self.msg_contents(
                f"A shimmering portal deposits {obj.name} into the room.",
                exclude=[obj]
            )
            obj.msg("You emerge from a swirling magical portal!")
            
    def at_object_leave(self, obj, target_location):
        """Farewell message"""
        if obj.has_account:
            self.msg_contents(
                f"{obj.name} fades away in a burst of magical energy.",
                exclude=[obj]
            )
            
    def return_appearance(self, looker, **kwargs):
        """Custom room description with magical effects"""
        appearance = super().return_appearance(looker, **kwargs)
        
        # Add magical ambiance
        effects = [
            "Motes of light drift lazily through the air.",
            "The walls shimmer with arcane energy.",
            "A faint humming fills the air."
        ]
        
        import random
        effect = random.choice(effects)
        appearance += f"\n\n|c{effect}|n"
        
        return appearance
```

### Interactive NPC with Script

```python
class Merchant(DefaultCharacter):
    """An NPC merchant"""
    
    def at_object_creation(self):
        """Set up merchant"""
        self.db.shop_inventory = {
            "sword": {"price": 100, "stock": 5},
            "shield": {"price": 50, "stock": 3},
            "potion": {"price": 25, "stock": 10}
        }
        
        # Create wandering script
        create.create_script(
            "scripts.MerchantWander",
            obj=self,
            interval=300,  # Move every 5 minutes
            repeats=0
        )
        
    def announce_wares(self):
        """Announce items for sale"""
        items = ", ".join(self.db.shop_inventory.keys())
        self.location.msg_contents(
            f"{self.name} calls out: 'Fresh {items} for sale!'"
        )

class MerchantWander(DefaultScript):
    """Script to make merchant wander"""
    
    def at_repeat(self):
        """Move to random connected room"""
        if not self.obj.location:
            return
            
        exits = self.obj.location.exits
        if exits:
            import random
            exit = random.choice(exits)
            if exit.destination:
                self.obj.move_to(exit.destination)
                self.obj.announce_wares()
```

### Advanced Menu System

```python
def char_creation_menu(caller):
    """Character creation main menu"""
    
    # Get current character data
    char_data = caller.ndb._char_creation or {}
    
    text = f"""
    |cCharacter Creation|n
    
    Name: |w{char_data.get('name', 'Not Set')}|n
    Race: |w{char_data.get('race', 'Not Set')}|n
    Class: |w{char_data.get('class', 'Not Set')}|n
    
    Stats:
    STR: {char_data.get('str', 10)}  DEX: {char_data.get('dex', 10)}  CON: {char_data.get('con', 10)}
    INT: {char_data.get('int', 10)}  WIS: {char_data.get('wis', 10)}  CHA: {char_data.get('cha', 10)}
    """
    
    options = [
        {"key": "1", "desc": "Set Name", "goto": "set_name"},
        {"key": "2", "desc": "Choose Race", "goto": "choose_race"},
        {"key": "3", "desc": "Choose Class", "goto": "choose_class"},
        {"key": "4", "desc": "Allocate Stats", "goto": "allocate_stats"},
    ]
    
    # Add finish option if character is complete
    if all(char_data.get(key) for key in ['name', 'race', 'class']):
        options.append({"key": "f", "desc": "Finish Creation", "goto": "finish_creation"})
        
    return text, options

def set_name(caller, raw_string):
    """Set character name"""
    if not caller.ndb._char_creation:
        caller.ndb._char_creation = {}
        
    text = "Enter your character's name:"
    options = {"key": "_default", "goto": ("save_name", {"input": raw_string})}
    return text, options

def save_name(caller, raw_string, **kwargs):
    """Save the entered name"""
    name = kwargs.get("input", "").strip()
    
    if not name:
        caller.msg("Invalid name. Please try again.")
        return "set_name"
        
    if len(name) > 20:
        caller.msg("Name too long. Maximum 20 characters.")
        return "set_name"
        
    caller.ndb._char_creation["name"] = name
    caller.msg(f"Name set to: {name}")
    return "char_creation_menu"

# Start the menu
EvMenu(caller, "path.to.menu_module", startnode="char_creation_menu")
```

### Error Handling and Validation

```python
def safe_object_creation(typeclass, key, location=None, **kwargs):
    """Safely create object with error handling"""
    try:
        # Validate inputs
        if not key or not isinstance(key, str):
            raise ValueError("Invalid key provided")
            
        if location and not hasattr(location, 'contents'):
            raise ValueError("Invalid location provided")
            
        # Create object
        obj = create.create_object(
            typeclass=typeclass,
            key=key,
            location=location,
            **kwargs
        )
        
        # Verify creation
        if not obj:
            raise RuntimeError("Object creation failed")
            
        return obj, None
        
    except Exception as e:
        error_msg = f"Failed to create {typeclass}: {str(e)}"
        logger.log_err(error_msg)
        return None, error_msg

# Usage
obj, error = safe_object_creation(
    "typeclasses.objects.Weapon",
    "Magic Sword",
    location=room
)

if error:
    caller.msg(f"Error: {error}")
else:
    caller.msg(f"Created {obj.name} successfully!")
```

---

This documentation covers the core public APIs and components of the Evennia framework. For more advanced usage and specific implementation details, refer to the individual module documentation and the official Evennia documentation at https://www.evennia.com/docs/.