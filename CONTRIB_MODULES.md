# Evennia Contrib Modules Documentation

Evennia includes a comprehensive collection of contrib modules that provide ready-to-use systems and examples for common MUD features. These modules are found in the `evennia/contrib/` directory and can be imported and customized for your game.

## Table of Contents

1. [Base Systems](#base-systems)
2. [RPG Systems](#rpg-systems)
3. [Game Systems](#game-systems)
4. [Grid and World Building](#grid-and-world-building)
5. [Tutorials and Examples](#tutorials-and-examples)
6. [Full Game Systems](#full-game-systems)
7. [Utilities](#utilities)
8. [Integration Examples](#integration-examples)

---

## Base Systems

### Email Login (`base_systems/email_login`)

Alternative login system using email addresses instead of usernames.

```python
# In server/conf/settings.py
INSTALLED_APPS += ['evennia.contrib.base_systems.email_login']

# In mygame/commands/default_cmdsets.py
from evennia.contrib.base_systems.email_login import EmailLoginCmdSet

class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(EmailLoginCmdSet)
```

Features:
- Login with email/password instead of username/password
- Email validation during account creation
- Compatible with existing account system

### Color Markups (`base_systems/color`)

Extended color markup systems beyond standard ANSI.

```python
from evennia.contrib.base_systems.color import xterm256_markup, hex_markup

# Use extended color palettes
colored_text = xterm256_markup("This is {256bright red}colored{/256} text!")
hex_text = hex_markup("This uses {#FF0000}hex colors{/}!")
```

### Ingame Reports (`base_systems/ingame_reports`)

Player report system for bugs, ideas, and issues.

```python
# Install the system
from evennia.contrib.base_systems.ingame_reports import install_reports_system

install_reports_system()

# Players can now use:
# report bug There's an issue with the combat system
# report idea Add fishing to the game
# report typo "recieve" should be "receive"

# Admins can manage reports:
# reports list
# reports view 1
# reports resolve 1
```

---

## RPG Systems

### Character Creator (`rpg/character_creator`)

Comprehensive character creation system with stats, traits, and skills.

```python
# Import the character creator
from evennia.contrib.rpg.character_creator import CharCreationCmdSet

# Add to unloggedin cmdset
class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CharCreationCmdSet)

# Customize the creation process in your own module
from evennia.contrib.rpg.character_creator.character_creator import create_character

def custom_character_creation(account, character_name, **kwargs):
    """Custom character creation logic"""
    character = create_character(
        account, 
        character_name,
        race=kwargs.get('race', 'human'),
        class_name=kwargs.get('class', 'warrior')
    )
    
    # Set custom attributes
    character.db.stats = {
        'strength': kwargs.get('str', 10),
        'dexterity': kwargs.get('dex', 10),
        'constitution': kwargs.get('con', 10),
        'intelligence': kwargs.get('int', 10),
        'wisdom': kwargs.get('wis', 10),
        'charisma': kwargs.get('cha', 10)
    }
    
    return character
```

### Dice System (`rpg/dice`)

Comprehensive dice rolling system for RPG mechanics.

```python
from evennia.contrib.rpg.dice import roll_dice

# Basic dice rolling
result = roll_dice("3d6+2")  # Roll 3 six-sided dice, add 2
print(f"Result: {result.total}, Rolls: {result.rolls}")

# Advanced dice expressions
damage = roll_dice("2d8+5")
skill_check = roll_dice("1d20+skill_modifier")

# In commands
class CmdRoll(Command):
    """
    Roll dice
    
    Usage:
        roll <dice_expression>
        
    Examples:
        roll 1d20
        roll 3d6+2
        roll 2d10+5-1
    """
    
    key = "roll"
    
    def func(self):
        if not self.args:
            self.caller.msg("Roll what dice?")
            return
            
        try:
            result = roll_dice(self.args.strip())
            self.caller.msg(f"Rolling {self.args}: {result.total}")
            self.caller.location.msg_contents(
                f"{self.caller.name} rolls {self.args} and gets {result.total}",
                exclude=[self.caller]
            )
        except Exception as e:
            self.caller.msg(f"Invalid dice expression: {e}")
```

### Buffs System (`rpg/buffs`)

Temporary effect system for spells, diseases, and status effects.

```python
from evennia.contrib.rpg.buffs.buff import Buff, BaseBuff

class StrengthBuff(BaseBuff):
    """Temporary strength enhancement"""
    
    name = "Strength Enhancement"
    duration = 300  # 5 minutes
    
    def at_buff_start(self, **kwargs):
        """Called when buff is applied"""
        self.owner.db.strength_bonus = self.owner.db.strength_bonus or 0
        self.owner.db.strength_bonus += 5
        self.owner.msg("You feel stronger!")
    
    def at_buff_end(self, **kwargs):
        """Called when buff expires"""
        self.owner.db.strength_bonus -= 5
        self.owner.msg("The strength enhancement fades.")

# Apply buff to character
buff = StrengthBuff(character)
buff.start()

# Check active buffs
active_buffs = character.buffs.all()

# Remove specific buff
character.buffs.remove(StrengthBuff)
```

### RP System (`rpg/rpsystem`)

Roleplay-focused systems with poses, emotes, and social commands.

```python
# Import the RP system
from evennia.contrib.rpg.rpsystem import RPCmdSet

# Add to character cmdset
class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(RPCmdSet)

# Players can now use:
# pose sits down at the table
# emote *character* nods thoughtfully
# say Hello there!
# whisper friend This is a secret
```

### LLM NPC (`rpg/llm_npc`)

AI-powered NPCs using Large Language Models.

```python
from evennia.contrib.rpg.llm_npc import LLMCharacter, LLMCmdSet

class SmartNPC(LLMCharacter):
    """An NPC powered by AI"""
    
    def at_object_creation(self):
        super().at_object_creation()
        
        # Configure the AI personality
        self.db.llm_config = {
            "personality": "A wise old wizard who speaks in riddles",
            "background": "Lives in a tower studying ancient magic",
            "knowledge": [
                "Magic spells and potions",
                "Ancient history",
                "Mystical creatures"
            ]
        }
        
        # Add conversation commands
        self.cmdset.add(LLMCmdSet)

# Players can talk to the NPC:
# talk wizard Hello, can you teach me magic?
# ask wizard about ancient spells
```

---

## Game Systems

### Crafting System (`game_systems/crafting`)

Complete crafting system with recipes, materials, and skills.

```python
from evennia.contrib.game_systems.crafting import CraftingCmdSet, Recipe

# Add crafting commands
class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CraftingCmdSet)

# Define recipes
sword_recipe = Recipe(
    name="Iron Sword",
    ingredients={
        "iron_ingot": 3,
        "wood": 1,
        "leather": 1
    },
    skill_required="smithing",
    skill_level=25,
    tools_required=["forge", "hammer"],
    result="iron_sword",
    experience=50
)

# Players can use:
# craft list                    # List available recipes
# craft iron sword              # Craft an iron sword
# craft show iron sword         # Show recipe details
```

### Economics (`game_systems/economics`)

Economic system with shops, currency, and trading.

```python
from evennia.contrib.game_systems.economics import ShopCmdSet, TradeGood

# Create a shop
class Blacksmith(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        
        # Add shop commands
        self.cmdset.add(ShopCmdSet)
        
        # Stock the shop
        self.db.shop_goods = {
            "sword": TradeGood("Iron Sword", price=100, stock=5),
            "armor": TradeGood("Leather Armor", price=75, stock=3),
            "shield": TradeGood("Wooden Shield", price=25, stock=10)
        }

# Players can use:
# shop list                     # List items for sale
# shop buy sword                # Buy a sword
# shop sell old_armor           # Sell an item
```

### Mail System (`game_systems/mail`)

In-game mail system for player communication.

```python
from evennia.contrib.game_systems.mail import MailCmdSet

# Add mail commands to characters
class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(MailCmdSet)

# Players can use:
# mail                          # List mail
# mail read 1                   # Read message 1
# mail send Alice Hello there!  # Send mail to Alice
# mail reply Thanks for the message!
# mail delete 1                 # Delete message 1
```

### Achievements (`game_systems/achievements`)

Achievement/trophy system for recognizing player accomplishments.

```python
from evennia.contrib.game_systems.achievements import Achievement, AchievementHandler

# Define achievements
first_kill = Achievement(
    key="first_kill",
    name="First Blood",
    description="Defeat your first enemy",
    points=10
)

explorer = Achievement(
    key="explorer",
    name="Explorer",
    description="Visit 50 different rooms",
    points=25
)

# Award achievements
character.achievements.award("first_kill")

# Check progress
progress = character.achievements.get_progress("explorer")
unlocked = character.achievements.list_unlocked()
```

---

## Grid and World Building

### Wilderness (`grid/wilderness`)

Procedural wilderness generation system.

```python
from evennia.contrib.grid.wilderness import create_wilderness

# Create a wilderness area
wilderness = create_wilderness(
    name="Dark Forest",
    size=(20, 20),
    map_provider="forest_map",
    preserve_items=True
)

# Configure terrain types
terrain_config = {
    'forest': {'symbol': '🌲', 'difficulty': 1},
    'mountain': {'symbol': '⛰️', 'difficulty': 3},
    'river': {'symbol': '🌊', 'difficulty': 2}
}
```

### Simple Door (`grid/simpledoor`)

Smart door system with keys, locks, and automation.

```python
from evennia.contrib.grid.simpledoor import create_door

# Create a door between two rooms
door = create_door(
    location=room1,
    destination=room2,
    key="wooden door",
    back_exit="wooden door",
    locked=True,
    key_id="brass_key"
)

# Players can:
# open door                     # Open the door
# close door                    # Close the door  
# lock door                     # Lock with key
# unlock door                   # Unlock with key
```

### Map Display (`grid/ingame_map_display`)

In-game ASCII map display system.

```python
from evennia.contrib.grid.ingame_map_display import MapDisplay

# Create a map display
map_display = MapDisplay(
    start_room=starting_room,
    max_distance=5,
    symbols={
        'player': '@',
        'room': '·',
        'exit': '-'
    }
)

# Show map to player
map_string = map_display.get_map_string(player.location)
player.msg(map_string)
```

---

## Tutorials and Examples

### Tutorial World (`tutorials/tutorial_world`)

Complete example world demonstrating Evennia features.

```python
# Install the tutorial world
from evennia.contrib.tutorials.tutorial_world import create_tutorial_world

create_tutorial_world()
```

Features included:
- Interactive rooms with special mechanics
- NPCs with behavior scripts
- Puzzle rooms and challenges
- Combat examples
- Object interaction demonstrations

### Talking NPC (`tutorials/talking_npc`)

Simple conversational NPC example.

```python
from evennia.contrib.tutorials.talking_npc import TalkingNPC

class Shopkeeper(TalkingNPC):
    def at_object_creation(self):
        super().at_object_creation()
        
        # Define conversation topics
        self.db.conversation_topics = {
            "greeting": "Welcome to my shop! How can I help you?",
            "inventory": "I have weapons, armor, and supplies.",
            "prices": "My prices are fair and reasonable.",
            "rumors": "I hear there are monsters in the nearby caves."
        }

# Players can talk to the NPC:
# talk shopkeeper
# ask shopkeeper about inventory
# tell shopkeeper about rumors
```

### Red Button (`tutorials/red_button`)

Tutorial demonstrating complex object interactions.

```python
from evennia.contrib.tutorials.red_button import RedButton

# The red button tutorial shows:
# - Multi-state objects
# - Complex command parsing
# - State-dependent commands
# - Object transformation
```

### EvAdventure (`tutorials/evadventure`)

Complete RPG tutorial game system.

```python
# Full RPG system including:
# - Character classes and races
# - Combat system (turn-based and twitch)
# - Equipment and inventory
# - Quest system
# - Shops and economy
# - Dungeon generation

from evennia.contrib.tutorials.evadventure import EvAdventureCmdSet
```

---

## Full Game Systems

### EvMenu Examples

Advanced menu system examples for complex interactions.

```python
from evennia.contrib.utils.tree_select import TreeSelectMenu

# Create hierarchical menus
menu_data = {
    "Character Creation": {
        "Choose Race": ["Human", "Elf", "Dwarf", "Orc"],
        "Choose Class": ["Warrior", "Mage", "Rogue", "Cleric"],
        "Allocate Stats": "stat_allocation_submenu"
    },
    "Game Options": {
        "Display Settings": ["Colors", "Screen Width", "Timestamps"],
        "Sound Settings": ["Volume", "Sound Effects", "Music"]
    }
}

TreeSelectMenu(caller, menu_data, select_callback=handle_selection)
```

### FieldFill System (`utils/fieldfill`)

Advanced form creation and field validation.

```python
from evennia.contrib.utils.fieldfill import EvForm

# Create complex forms with validation
character_sheet = EvForm("character_sheet_template")

# Add field validation
character_sheet.add_field(
    "name", 
    validator=lambda x: len(x) >= 3,
    error_msg="Name must be at least 3 characters"
)

character_sheet.add_field(
    "age",
    validator=lambda x: x.isdigit() and 16 <= int(x) <= 100,
    error_msg="Age must be between 16 and 100"
)
```

---

## Utilities

### Git Integration (`utils/git_integration`)

Integrate Git version control into your game.

```python
from evennia.contrib.utils.git_integration import GitCmdSet

# Add git commands for developers
class BuilderCmdSet(CmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(GitCmdSet)

# Developers can use:
# git status                    # Check repository status
# git add filename.py           # Stage files
# git commit "Added new feature"
# git push                      # Push changes
```

### Extended Room (`utils/extended_room`)

Enhanced room class with additional features.

```python
from evennia.contrib.utils.extended_room import ExtendedRoom

class MyRoom(ExtendedRoom):
    def at_object_creation(self):
        super().at_object_creation()
        
        # Rooms support multiple descriptions
        self.db.spring_desc = "Flowers bloom everywhere in spring."
        self.db.winter_desc = "Snow covers the ground in winter."
        
        # Automatic seasonal descriptions
        self.db.seasonal_desc = True
```

### Clothing System (`utils/clothing`)

Wearable clothing and armor system.

```python
from evennia.contrib.utils.clothing import ClothingCmdSet, ClothingObject

class Shirt(ClothingObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.clothing_type = "shirt"
        self.db.worn_on = ["torso"]

# Players can:
# wear shirt                    # Put on clothing
# remove shirt                  # Take off clothing
# clothing                      # List worn items
```

---

## Integration Examples

### Using Multiple Systems Together

```python
# Example: Combining multiple contrib systems
from evennia.contrib.rpg.character_creator import CharCreationCmdSet
from evennia.contrib.rpg.dice import DiceCmdSet  
from evennia.contrib.game_systems.crafting import CraftingCmdSet
from evennia.contrib.game_systems.mail import MailCmdSet

class AdvancedCharacterCmdSet(CmdSet):
    """Character cmdset with multiple contrib systems"""
    
    def at_cmdset_creation(self):
        # Add multiple contrib systems
        self.add(DiceCmdSet)
        self.add(CraftingCmdSet)
        self.add(MailCmdSet)
        
        # Add custom commands
        self.add(CmdAdvancedStats())
        self.add(CmdGuildManagement())

class RPGCharacter(DefaultCharacter):
    """Character using multiple contrib systems"""
    
    def at_object_creation(self):
        super().at_object_creation()
        
        # Initialize contrib systems
        self.cmdset.add(AdvancedCharacterCmdSet)
        
        # Set up character data
        self.db.stats = {
            'strength': 10, 'dexterity': 10, 'constitution': 10,
            'intelligence': 10, 'wisdom': 10, 'charisma': 10
        }
        
        self.db.skills = {
            'smithing': 1, 'combat': 1, 'magic': 1
        }
        
        # Initialize crafting
        self.db.known_recipes = []
        
        # Initialize buffs
        self.buffs = BuffHandler(self)
```

### Custom Contrib Module

Create your own contrib-style module:

```python
# In mygame/contrib/my_system/
# __init__.py
"""My Custom Game System

A comprehensive system for managing custom game mechanics.
"""

from .commands import MySystemCmdSet
from .objects import MyCustomObject
from .handlers import MySystemHandler

__all__ = ["MySystemCmdSet", "MyCustomObject", "MySystemHandler"]

# commands.py
from evennia import Command, CmdSet

class CmdMySystem(Command):
    """
    Use my custom system
    
    Usage:
        mysystem <action>
    """
    
    key = "mysystem"
    
    def func(self):
        # Implementation here
        pass

class MySystemCmdSet(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdMySystem)

# objects.py  
from evennia import DefaultObject

class MyCustomObject(DefaultObject):
    def at_object_creation(self):
        super().at_object_creation()
        self.db.custom_property = "default_value"

# handlers.py
class MySystemHandler:
    def __init__(self, obj):
        self.obj = obj
        
    def process_action(self, action):
        # Custom logic here
        pass
```

### Installation Patterns

Common patterns for installing contrib modules:

```python
# Method 1: Direct import in cmdsets
from evennia.contrib.rpg.dice import DiceCmdSet

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(DiceCmdSet)

# Method 2: Module-level installation
# In server/conf/settings.py
INSTALLED_APPS += [
    'evennia.contrib.base_systems.email_login'
]

# Method 3: Initialization in typeclasses
class Character(DefaultCharacter):
    def at_object_creation(self):
        super().at_object_creation()
        
        # Initialize contrib systems
        from evennia.contrib.rpg.buffs import BuffHandler
        self.buffs = BuffHandler(self)

# Method 4: Settings configuration
# In server/conf/settings.py
CONTRIB_CONFIG = {
    'dice_system': {
        'default_sides': 20,
        'exploding_dice': True
    },
    'crafting_system': {
        'skill_gain_rate': 1.5,
        'tool_durability': True
    }
}
```

---

The contrib modules provide a rich ecosystem of ready-to-use systems that can be mixed and matched to create your unique game. Each module is designed to be modular and customizable, allowing you to adapt them to your specific needs while learning from well-implemented examples.

For the most up-to-date list of contrib modules and their features, check the `evennia/contrib/` directory in your Evennia installation or browse the online documentation.