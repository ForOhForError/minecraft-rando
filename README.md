# Minecraft Rando

Utility for generating randomizer datapacks for minecraft. At the moment, it randomizes the following:

* Loot tables (including block drops, mob drops, loot chests, etc. indiscriminately)
* Crafting recipes

## Usage

Clone the repository to download the script:

```bash

git clone https://github.com/ForOhForError/minecraft-rando

```

Or download it directly with ```wget```

```bash

wget https://raw.githubusercontent.com/ForOhForError/minecraft-rando/master/minecraft_randomizer.py

```

Run with the following syntax:

```bash

python3 minecraft_randomizer.py [-h] [-s SEED] [-l] [-c] [-o OUTPUT] [--loot-blacklist [LOOT_BLACKLIST [LOOT_BLACKLIST ...]]] [--crafting-blacklist [CRAFTING_BLACKLIST [CRAFTING_BLACKLIST ...]]]
                               [--loot-categories [{blocks,chests,entities,gameplay} [{blocks,chests,entities,gameplay} ...]]] [--unlock-recipes] [--loot-hints]
                               jarfile

Generate a randomizer datapack.

positional arguments:
  jarfile               path to minecraft jar file

optional arguments:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  Randomization seed; defaults to a random value
  -l, --loot            Randomize loot tables; defaults to false.
  -c, --crafting        Randomize crafting recipes; defaults to false.
  -o OUTPUT, --output OUTPUT
                        Output file; defaults to mc_random.zip
  --loot-blacklist [LOOT_BLACKLIST [LOOT_BLACKLIST ...]]
                        List of regex patterns to exclude from loot randomization; defaults to excluding shulker boxes.
  --crafting-blacklist [CRAFTING_BLACKLIST [CRAFTING_BLACKLIST ...]]
                        List of regex patterns to exclude from loot randomization; defaults to empty.
  --loot-categories [{blocks,chests,entities,gameplay} [{blocks,chests,entities,gameplay} ...]]
                        List of loot categories to randomize. Choices are [blocks | chests | entities | gameplay]. Defaults to all categories.
  --unlock-recipes      Adds a function to the datapack to grant players all recipes on joining the server. Defaults to false.
  --loot-hints          Adds unusable "hint" recipes that show the results of any 1-to-1 drops. Defaults to false.

```

Note that:

* The ```jarfile``` argument is required; the loot tables are randomized from those present in the file specified.
* The command defualts to not running either loot or crafting randomization. Running it without the ```--loot``` or ```--crafting``` flags set will result in a datapack that does nothing. This will additionally produce a warning on standard out.

## Datapack installation

See instructions [here](https://minecraft.fandom.com/wiki/Tutorials/Installing_a_data_pack).

## Credit

Based on [SethBling's 1.14 randomizer script](https://www.youtube.com/watch?v=3JEXAZOrykQ).
