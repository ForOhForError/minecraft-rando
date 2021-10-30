# Minecraft Rando

Utility for generating randomizer datapacks for minecraft. At the moment, it randomizes the following:

* Loot tables (including block drops, mob drops, loot chests, etc. indiscriminately)
* Crafting recipes

## Usage

Clone the repository to download the script:

```bash

git clone https://github.com/ForOhForError/minecraft-rando

```

Run with the following syntax:

```bash

python3 minecraft_randomizer.py [-h] [-s SEED] [--loot] [--crafting] [-o OUTPUT] jarfile

positional arguments:
  jarfile               path to minecraft jar file

optional arguments:
  -h, --help            show help message and exit
  -s SEED, --seed SEED  randomization seed
  --loot                randomize loot tables, defualts to false
  --crafting            randomize crafting recipes, defaults to false
  -o OUTPUT, --output OUTPUT
                        output file (defaults to mc_random.zip)

```

Note that:

* The ```jarfile``` argument is required; the loot tables are randomized from those present in the file specified.
* The command defualts to not running either loot or crafting randomization. Running it without the ```--loot``` or ```--crafting``` flags set will result in a datapack that does nothing

## Datapack installation

See instructions [here](https://minecraft.fandom.com/wiki/Tutorials/Installing_a_data_pack).

## Credit

Based on [SethBling's 1.14 randomizer script](https://www.youtube.com/watch?v=3JEXAZOrykQ).
