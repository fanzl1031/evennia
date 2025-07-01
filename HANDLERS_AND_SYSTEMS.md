# Evennia Handlers and Systems Documentation

This document covers the various handler systems and specialized components in Evennia that manage different aspects of the game engine.

## Table of Contents

1. [Handler Overview](#handler-overview)
2. [Session Handlers](#session-handlers)
3. [Attribute System](#attribute-system)
4. [Tag System](#tag-system)
5. [Lock System](#lock-system)
6. [Nick System](#nick-system)
7. [CmdSet System](#cmdset-system)
8. [Task and Ticker Handlers](#task-and-ticker-handlers)
9. [Web Components](#web-components)
10. [Database Managers](#database-managers)

---

## Handler Overview

Handlers in Evennia are specialized objects that manage specific aspects of game entities. They provide a consistent interface for common operations like storing data, managing permissions, and handling commands.

### Common Handler Patterns

Most handlers follow these patterns:

```python
# Add/Create
handler.add(key, value, category=None, **kwargs)

# Get/Retrieve  
value = handler.get(key, category=None, default=None)

# Remove/Delete
handler.remove(key, category=None)

# Check existence
exists = handler.has(key, category=None)

# List all
all_items = handler.all()

# Clear all
handler.clear()
```

---

## Session Handlers

### SESSION_HANDLER

Global handler managing all client sessions.

```python
from evennia import SESSION_HANDLER

# Get all active sessions
sessions = SESSION_HANDLER.get_sessions()

# Get sessions by account
account_sessions = SESSION_HANDLER.sessions_from_account(account)

# Get session by ID
session = SESSION_HANDLER.get_session_by_sessid(session_id)

# Session count
total_sessions = SESSION_HANDLER.session_count()

# Announce to all sessions
SESSION_HANDLER.announce_all("Server message to everyone!")

# Disconnect session
SESSION_HANDLER.disconnect(session, reason="Kicked by admin")
```

### Object Session Handler

Individual objects have their own session handlers:

```python
# Get sessions connected to this object
sessions = obj.sessions.all()

# Get primary session
primary = obj.sessions.get()

# Add session to object
obj.sessions.add(session)

# Remove session
obj.sessions.remove(session)

# Session count for this object
count = obj.sessions.count()
```

---

## Attribute System

Attributes store persistent data on objects with optional categories and locks.

### Basic Attribute Operations

```python
# Simple attribute storage
obj.db.health = 100
obj.db.name = "Hero"

# Access attributes
health = obj.db.health
name = obj.db.name

# Check existence
has_health = hasattr(obj.db, 'health')

# Delete attribute
del obj.db.health
```

### Advanced Attribute Handler

```python
# Add with category and locks
obj.attributes.add(
    key="secret_info",
    value="classified data", 
    category="secrets",
    lockstring="view:perm(Admin)"
)

# Get with category
secret = obj.attributes.get("secret_info", category="secrets")

# Get all in category
secrets = obj.attributes.get(category="secrets")

# Get with default
level = obj.attributes.get("level", default=1)

# Remove specific attribute
obj.attributes.remove("old_data")

# Remove by category
obj.attributes.remove(category="temp_data")

# Get all attributes
all_attrs = obj.attributes.all()

# Check access permissions
can_view = obj.attributes.has("secret_info", category="secrets")
```

### Attribute Properties

Define attributes as properties on typeclasses:

```python
from evennia.typeclasses.attributes import AttributeProperty

class Character(DefaultCharacter):
    
    # Simple attribute property
    level = AttributeProperty(default=1)
    
    # Attribute with category
    skills = AttributeProperty(default={}, category="character_data")
    
    # Attribute with validation
    def _validate_health(self, value):
        return max(0, min(1000, int(value)))
    
    health = AttributeProperty(default=100, autocreate=False)
    
    def at_object_creation(self):
        # Initialize with validation
        self.attributes.add("health", 100, validator=self._validate_health)

# Usage
char = create.create_object(Character, key="Hero")
char.level = 5  # Automatically saved
char.health = 150  # Validated and clamped
```

### Non-Persistent Attributes (NDB)

Store temporary data that doesn't persist through restarts:

```python
# Store temporary data
obj.ndb.combat_target = enemy
obj.ndb.temp_bonus = 10

# Access temporary data
target = obj.ndb.combat_target

# Clear on logout/restart
obj.ndb.clear()

# Common pattern for caching
def expensive_calculation(self):
    if not hasattr(self.ndb, '_cached_result'):
        self.ndb._cached_result = complex_computation()
    return self.ndb._cached_result
```

---

## Tag System

Tags provide categorical labeling and fast lookups for objects.

### Basic Tag Operations

```python
# Add simple tags
obj.tags.add("weapon")
obj.tags.add("magical")

# Add tag with category
obj.tags.add("steel", category="material")
obj.tags.add("sharp", category="properties")

# Check for tags
is_weapon = obj.tags.has("weapon")
is_steel = obj.tags.has("steel", category="material")

# Get all tags
all_tags = obj.tags.all()

# Get tags by category
materials = obj.tags.get(category="material")

# Remove tags
obj.tags.remove("old_tag")
obj.tags.remove(category="temp_tags")

# Clear all tags
obj.tags.clear()
```

### Special Tag Types

```python
# Alias tags (alternative names)
obj.tags.add("sword", category="aliases", tagtype="alias")

# Permission tags
obj.tags.add("builder", category="permissions", tagtype="permission")

# System tags (used internally)
obj.tags.add("no_save", category="system", tagtype="system")
```

### Tag Properties

Define tags as properties:

```python
from evennia.typeclasses.tags import TagProperty, TagCategoryProperty

class Weapon(DefaultObject):
    
    # Single tag property
    weapon_type = TagProperty(category="item_type")
    
    # Multiple tags in category
    properties = TagCategoryProperty(category="properties")
    
    def at_object_creation(self):
        self.weapon_type = "sword"
        self.properties = ["sharp", "metal", "enchanted"]

# Usage
weapon = create.create_object(Weapon, key="Magic Sword")
print(weapon.weapon_type)  # "sword"
print(weapon.properties)   # ["sharp", "metal", "enchanted"]

weapon.properties.append("glowing")  # Automatically saved
```

### Tag-Based Searches

```python
# Find all weapons
weapons = search.search_object_by_tag("weapon")

# Find steel weapons  
steel_weapons = search.search_object_by_tag("steel", category="material")

# Find objects with multiple tags
magical_weapons = obj.search_tag([("weapon", None), ("magical", None)])

# Search in specific location
room_weapons = obj.location.search_tag("weapon")
```

---

## Lock System

The lock system controls access to objects and commands with flexible boolean logic.

### Basic Lock Operations

```python
# Add simple lock
obj.locks.add("get:all()")  # Anyone can pick up

# Add multiple locks
obj.locks.add("get:all();drop:all();examine:all()")

# Complex access control
obj.locks.add("enter:perm(Builder) or id(123)")

# Check access
can_get = obj.access(character, "get")
can_enter = obj.access(character, "enter", default=False)

# Get lock string
lock_string = obj.locks.get("get")

# Remove lock
obj.locks.remove("old_lock")

# Check for lock existence
has_get_lock = obj.locks.has("get")
```

### Lock Functions

Common lock functions available:

```python
# Permission-based
"perm(Builder)"      # Has Builder permission
"pperm(Admin)"       # Account has Admin permission

# Identity-based  
"id(123)"           # Object ID 123
"dbref(#123)"       # Database reference 123

# Ownership
"owns()"            # Character owns the object
"controls()"        # Has control access

# Relationship
"holds(123)"        # Object 123 is in inventory
"inside(456)"       # Inside object 456

# Attribute-based
"attr(level, 5)"    # Has attribute level >= 5
"attrgte(hp, 50)"   # Attribute hp >= 50

# Time-based
"timeperiod(morning)"  # During morning hours

# Combined with logic
"perm(Builder) and attr(level, 10)"
"id(123) or perm(Admin)"
"not perm(Guest)"
```

### Custom Lock Functions

Create custom lock functions:

```python
# In a lockfuncs module
def has_gold(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Check if accessing object has enough gold.
    Usage: has_gold(100) - requires 100 gold
    """
    required = int(args[0]) if args else 1
    return getattr(accessing_obj.db, 'gold', 0) >= required

def in_same_guild(accessing_obj, accessed_obj, *args, **kwargs):
    """
    Check if objects are in same guild.
    Usage: in_same_guild()
    """
    return (getattr(accessing_obj.db, 'guild', None) == 
            getattr(accessed_obj.db, 'guild', None))

# Register in settings
# LOCK_FUNC_MODULES = ["world.lockfuncs"]

# Use in locks
door.locks.add("open:has_gold(50)")
guild_hall.locks.add("enter:in_same_guild()")
```

### Command Locks

Commands have special lock considerations:

```python
class CmdSpecial(Command):
    """
    A command with complex access control
    """
    
    key = "special"
    locks = "cmd:perm(Builder) and attr(level, 10)"
    
    def at_pre_cmd(self):
        """Additional runtime checks"""
        if not self.caller.db.special_key:
            self.caller.msg("You need a special key to use this command.")
            return False
        return True
```

---

## Nick System

Nicks provide shortcuts and aliases for common inputs.

### Basic Nick Operations

```python
# Add input replacement nick
obj.nicks.add("h", "health", category="inputline")

# Add object reference nick
obj.nicks.add("bob", target_obj, category="object")

# Add channel nick
obj.nicks.add("g", channel, category="channel")

# Use nick replacement
replaced = obj.nicks.nickreplace("h", categories=["inputline"])
# Returns "health"

# Remove nick
obj.nicks.remove("h", category="inputline")

# Get all nicks
all_nicks = obj.nicks.all()

# Get by category
input_nicks = obj.nicks.get(category="inputline")
```

### Nick Categories

Standard categories and their usage:

```python
# Input line replacement - command shortcuts
obj.nicks.add("l", "look", category="inputline")
obj.nicks.add("i", "inventory", category="inputline")

# Object references - character names
obj.nicks.add("friend", friend_character, category="object")

# Channel shortcuts
obj.nicks.add("ooc", ooc_channel, category="channel")

# Account-level nicks (shared across characters)
account.nicks.add("tell", "page", category="inputline") 
```

### Automatic Nick Replacement

Nicks are automatically applied in search and command contexts:

```python
# When player types "l", it becomes "look"
# When player types "tell bob hello", "bob" resolves to actual character

# Manual replacement in custom code
def custom_command_handler(self, raw_input):
    # Apply nick replacement
    processed = self.caller.nicks.nickreplace(
        raw_input, 
        categories=["inputline", "object", "channel"]
    )
    # Continue processing...
```

---

## CmdSet System

CmdSets group commands and manage their availability.

### Basic CmdSet Creation

```python
from evennia import CmdSet

class CharacterCmdSet(CmdSet):
    """Commands available to characters"""
    
    key = "character_commands"
    priority = 0  # Higher numbers override lower
    mergetype = "Union"  # How to merge with other cmdsets
    
    def at_cmdset_creation(self):
        """Add commands to this set"""
        self.add(CmdLook())
        self.add(CmdSay())
        self.add(CmdGet())
        self.add(CmdDrop())

class BuilderCmdSet(CmdSet):
    """Additional commands for builders"""
    
    key = "builder_commands" 
    priority = 1  # Higher priority than character commands
    mergetype = "Union"
    
    def at_cmdset_creation(self):
        self.add(CmdDig())
        self.add(CmdCreate())
        self.add(CmdDestroy())
```

### CmdSet Merge Types

```python
# Union: Combines all commands from both sets
cmdset.mergetype = "Union" 

# Replace: This cmdset replaces others entirely
cmdset.mergetype = "Replace"

# Intersect: Only commands that exist in both sets
cmdset.mergetype = "Intersect"
```

### Dynamic CmdSets

```python
class ContextualCmdSet(CmdSet):
    """CmdSet that changes based on conditions"""
    
    key = "contextual_commands"
    
    def at_cmdset_creation(self):
        """Dynamically add commands based on context"""
        
        # Always add basic commands
        self.add(CmdLook())
        
        # Add combat commands if in combat
        if self.obj and getattr(self.obj.ndb, '_in_combat', False):
            self.add(CmdAttack())
            self.add(CmdDefend())
            self.add(CmdFlee())
            
        # Add building commands if has permission
        if self.obj and self.obj.check_permstring("Builder"):
            self.add(CmdDig())
            self.add(CmdCreate())
```

### Managing CmdSets on Objects

```python
# Add cmdset to object
obj.cmdset.add(CharacterCmdSet)

# Add with options
obj.cmdset.add(BuilderCmdSet, permanent=True, priority=10)

# Remove cmdset
obj.cmdset.remove(BuilderCmdSet)

# Get current cmdsets
current = obj.cmdset.get()

# Check for specific cmdset
has_builder = obj.cmdset.has("builder_commands")

# Clear all cmdsets
obj.cmdset.clear()
```

### CmdSet Hooks

```python
def at_cmdset_get(self, **kwargs):
    """Called when cmdset is requested from object"""
    
    # Conditionally add/remove cmdsets
    if self.db.in_special_mode:
        self.cmdset.add(SpecialModeCmdSet, temporary=True)
    else:
        self.cmdset.remove(SpecialModeCmdSet)
        
    # Call parent to continue normal processing
    super().at_cmdset_get(**kwargs)
```

---

## Task and Ticker Handlers

### TASK_HANDLER

Manages delayed and repeated tasks.

```python
from evennia import TASK_HANDLER

# Add one-time delayed task
def delayed_function(obj):
    obj.msg("Delayed message!")

TASK_HANDLER.add(
    delay=10,  # 10 seconds
    callback=delayed_function,
    args=[character]
)

# Add repeating task
def heartbeat(obj):
    if hasattr(obj.db, 'health'):
        obj.db.health = min(obj.db.health + 1, 100)

task_id = TASK_HANDLER.add(
    delay=60,    # First run in 60 seconds
    interval=60, # Repeat every 60 seconds  
    callback=heartbeat,
    args=[character],
    persistent=True  # Survive server restart
)

# Cancel task
TASK_HANDLER.cancel(task_id)

# Get task info
task_data = TASK_HANDLER.get(task_id)
```

### TICKER_HANDLER

Optimized for many objects doing the same periodic action.

```python
from evennia import TICKER_HANDLER

# Subscribe object to ticker
TICKER_HANDLER.add(
    obj=character,
    interval=10,    # Every 10 seconds
    callback=character.at_heartbeat,  # Method to call
    idstring="character_tick"  # Identifier
)

# Subscribe multiple objects
TICKER_HANDLER.add(
    obj=[char1, char2, char3],
    interval=30,
    callback="at_maintenance"  # String method name
)

# Remove from ticker
TICKER_HANDLER.remove(character, "character_tick")

# Remove all subscriptions for object
TICKER_HANDLER.remove(character)

# Check subscriptions
subscribed = TICKER_HANDLER.get_subscriptions(character)
```

### Task Examples

```python
def delayed_message(target, message, sender=None):
    """Send message after delay"""
    target.msg(message, from_obj=sender)

def regeneration_tick(character):
    """Periodic health/mana regeneration"""
    if character.db.health < character.db.max_health:
        character.db.health += 5
        character.msg("You feel healthier.")
        
def save_reminder(character):
    """Remind player to save periodically"""  
    character.msg("Don't forget to save your progress!")
    
# Usage examples
TASK_HANDLER.add(5, delayed_message, [character, "Hello!", sender])

TICKER_HANDLER.add(character, 60, regeneration_tick, "regen")

TASK_HANDLER.add(300, save_reminder, [character], persistent=False)
```

---

## Web Components

### Web API Views

Evennia provides REST API endpoints:

```python
# In web/api/views.py extensions
from evennia.web.api.views import ObjectDBViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

class CustomObjectViewSet(ObjectDBViewSet):
    """Extended object API with custom endpoints"""
    
    @action(detail=True, methods=['post'])
    def move_object(self, request, pk=None):
        """Custom API endpoint to move object"""
        obj = self.get_object()
        target_id = request.data.get('target_id')
        
        try:
            target = ObjectDB.objects.get(id=target_id)
            obj.move_to(target)
            return Response({'status': 'moved'})
        except ObjectDB.DoesNotExist:
            return Response({'error': 'Target not found'}, status=404)
```

### Web Character Management

```python
# In web views
from django.contrib.auth.mixins import LoginRequiredMixin
from evennia.web.website.views.characters import CharacterDetailView

class CustomCharacterView(LoginRequiredMixin, CharacterDetailView):
    """Extended character management"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.get_object()
        
        # Add custom data to template context
        context['stats'] = {
            'level': character.db.level or 1,
            'health': character.db.health or 100,
            'experience': character.db.experience or 0
        }
        
        return context
```

### WebSocket Integration

```python
# In web/websocket.py extensions
from evennia.web.website.views.websocket import EvenniaWebSocketConsumer

class GameWebSocketConsumer(EvenniaWebSocketConsumer):
    """Extended WebSocket consumer"""
    
    def receive_json(self, content):
        """Handle custom WebSocket messages"""
        
        if content.get('type') == 'custom_command':
            # Handle custom commands from web client
            command = content.get('command')
            self.handle_custom_command(command)
        else:
            # Default handling
            super().receive_json(content)
    
    def handle_custom_command(self, command):
        """Process custom web commands"""
        if hasattr(self, 'account') and self.account:
            # Execute command through account
            self.account.execute_cmd(command)
```

---

## Database Managers

### Object Managers

Each typeclass has a manager for database operations:

```python
from evennia.objects.models import ObjectDB

# Basic queries
all_objects = ObjectDB.objects.all()
weapons = ObjectDB.objects.filter(db_typeclass_path__contains="Weapon")

# Manager methods
obj = ObjectDB.objects.get_object_with_dbref("#123")
objs = ObjectDB.objects.get_objs_with_key_or_alias("sword")

# Search methods
results = ObjectDB.objects.search_object(
    "sword",
    typeclass="typeclasses.objects.Weapon"
)

# Bulk operations
ObjectDB.objects.filter(db_location=room).update(db_location=new_room)
```

### Custom Manager Methods

```python
from evennia.objects.manager import ObjectManager

class WeaponManager(ObjectManager):
    """Custom manager for weapon objects"""
    
    def get_by_damage_range(self, min_damage, max_damage):
        """Get weapons in damage range"""
        return self.filter(
            db_attributes__db_key="damage",
            db_attributes__db_value__gte=min_damage,
            db_attributes__db_value__lte=max_damage
        )
    
    def get_magical_weapons(self):
        """Get all magical weapons"""
        return self.get_by_tag("magical")
    
    def get_weapons_by_material(self, material):
        """Get weapons made of specific material"""
        return self.get_by_tag(material, category="material")

class Weapon(DefaultObject):
    """Weapon with custom manager"""
    
    objects = WeaponManager()
    
    # Usage:
    # steel_swords = Weapon.objects.get_weapons_by_material("steel")
    # magic_items = Weapon.objects.get_magical_weapons()
```

### Performance Optimization

```python
# Use select_related for foreign keys
characters = ObjectDB.objects.select_related('db_location').all()

# Use prefetch_related for many-to-many
objects_with_attrs = ObjectDB.objects.prefetch_related('db_attributes').all()

# Bulk create for many objects
ObjectDB.objects.bulk_create([
    ObjectDB(db_key=f"object_{i}", db_typeclass_path="typeclasses.Object")
    for i in range(100)
])

# Use iterator for large datasets
for obj in ObjectDB.objects.filter(large_query=True).iterator():
    process_object(obj)
```

---

This documentation covers the major handler systems and components in Evennia. These systems work together to provide a comprehensive framework for managing all aspects of a MUD/MUX game, from basic object storage to complex command processing and web integration.