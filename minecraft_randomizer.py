import os
import random
import io
import zipfile
import json
import sys
import argparse
import re

LOOT_CATEGORIES = ['blocks', 'chests', 'entities', 'gameplay']
HINT_CATEGORIES = ['blocks']

DEFAULT_LOOT_BLACKLIST = ['.*_shulker_box\.json']
DEFAULT_CRAFTING_BLACKLIST = []
DEFAULT_LOOT_CATEGORIES = [cat for cat in LOOT_CATEGORIES]

TICK_FUNCTION = [
	'execute as @a[tag=!learnedallrecipes] run recipe give @a *',
	'tag @a[tag=!learnedallrecipes] add learnedallrecipes'
]

def hint_recipe(item_in, item_out):
	recipe_obj = {
		"type": "minecraft:crafting_shapeless",
		"ingredients": [
			{"item": "minecraft:barrier"},
			{"item": item_in}
		],
		"result": {
			"item": item_out
		}
	}
	return json.dumps(recipe_obj, indent=2)

def random_remapping(path_list):
	file_list = []
	remaining = []
	file_dict = {}
	for path in path_list:
		file_list.append(path)
		remaining.append(path)
	for key in file_list:
		i = random.randint(0, len(remaining)-1)
		file_dict[key] = remaining[i]
		del remaining[i]
	return file_dict

def get_childfiles(inzip, subpath, blacklist=[], categories=None):
	all_files = inzip.namelist()
	result_list = []
	blacklist = [re.compile(pattern) for pattern in blacklist]
	for path in all_files:
		path_parts = path.split('/')
		last_path = path_parts[-1]
		matches_subpath = path.startswith(subpath) and not inzip.getinfo(path).is_dir()
		matches_category = True
		if categories != None and matches_subpath and len(path_parts)>3:
			matches_category = path_parts[3] in categories
		if matches_subpath and matches_category and all(
			[not pattern.fullmatch(last_path) for pattern in blacklist]
		):
			result_list.append(path)
	return result_list

def randomize_loot(inzip, outzip, loot_file_dict, do_hints=False):
	hintno = 0
	for from_file in loot_file_dict:
		contents = ''
		with inzip.open(from_file) as content_file:
			contents = content_file.read()
		to_file = loot_file_dict[from_file]
		outzip.writestr(to_file, contents)
		if do_hints:
			loot_obj = json.loads(contents)
			to_paths = to_file.split('/')
			if to_paths[3] in HINT_CATEGORIES:
				item_in = 'minecraft:' + to_paths[-1].split('.')[0]
				if 'pools' in loot_obj:
					min_conditions = 999
					min_pool = None
					for pool in loot_obj['pools']:
						conditions = 0
						if 'conditions' in pool:
							conditions = len(pool['conditions'])
						if min_pool is None or conditions < min_conditions:
							min_conditions = conditions
							min_pool = pool
					if 'entries' in pool:
						entries = pool['entries']
						for entry in entries:
							if entry['type'] == 'minecraft:item' and 'name' in entry:
								item_out = entry['name']
								recipe_file = f'data/minecraft/recipes/hint_{hintno}.json'
								hintno += 1
								outzip.writestr(recipe_file, hint_recipe(item_in, item_out))

def randomize_crafting(inzip, outzip, craft_file_dict, passnum=1):
	remnant_list = []
	for from_file in craft_file_dict:
		from_contents = ''
		to_contents = ''
		with inzip.open(from_file) as content_file:
			from_contents = content_file.read()
		with inzip.open(craft_file_dict[from_file]) as content_file:
			to_contents = content_file.read()
		from_obj = json.loads(from_contents)
		to_obj = json.loads(to_contents)
		if 'result' not in from_obj:
			remnant_list.append(craft_file_dict[from_file])
			outzip.writestr(from_file,from_contents)
			continue
		if 'result' not in to_obj:
			continue
		to_obj['result'] = from_obj['result']
		outzip.writestr(craft_file_dict[from_file], json.dumps(to_obj, indent=2))
	if len(remnant_list) > 0:
		craft_file_dict = random_remapping(remnant_list)
		randomize_crafting(inzip, outzip, craft_file_dict, passnum+1)

def main(sysargs):
	parser = argparse.ArgumentParser(description='Generate a randomizer datapack.')
	parser.add_argument(
		'-s', '--seed', help='Randomization seed; defaults to a random value'
	)
	parser.add_argument(
		'-l', '--loot', help='Randomize loot tables; defaults to false.', action='store_true'
	)
	parser.add_argument(
		'-c', '--crafting', help='Randomize crafting recipes; defaults to false.', action='store_true'
	)
	parser.add_argument(
		'-o', '--output', help='Output file; defaults to mc_random.zip', default='mc_random.zip'
	)
	parser.add_argument(
		'--loot-blacklist', 
		help='List of regex patterns to exclude from loot randomization; defaults to excluding shulker boxes.',
		nargs='*', default=DEFAULT_LOOT_BLACKLIST
	)
	parser.add_argument(
		'--crafting-blacklist', 
		help='List of regex patterns to exclude from loot randomization; defaults to empty.',
		nargs='*', default=DEFAULT_CRAFTING_BLACKLIST
	)
	parser.add_argument(
		'--loot-categories', 
		help='List of loot categories to randomize. Choices are [blocks | chests | entities | gameplay]. Defaults to all categories.',
		choices=LOOT_CATEGORIES,
		nargs='*', default=DEFAULT_LOOT_CATEGORIES
	)
	parser.add_argument(
		'--unlock-recipes', 
		help='Adds a function to the datapack to grant players all recipes on joining the server. Defaults to false.',
		action='store_true'
	)
	parser.add_argument(
		'--loot-hints', 
		help='Adds unusable "hint" recipes that show the results of any 1-to-1 drops. Defaults to false.',
		action='store_true'
	)
	parser.add_argument('jarfile', type=str, help='path to minecraft jar file')
	args = parser.parse_args()
	datapack_name = 'mc_random'
	datapack_desc = ''

	if not (args.loot or args.crafting):
		print("------------------------------------------- WARNING ---------------------------------------------------")
		print("Neither --crafting nor --loot was specified; the generated datapack file is valid but will do nothing")
		print("This is probably not what you intended! Please use the --help flag for more information.")
		print("-------------------------------------------------------------------------------------------------------")

	if args.seed:
		seed = args.seed
		random.seed(seed)
		datapack_name = 'mc_random_{}'.format(seed)
		datapack_desc = 'Minecraft Randomizer, Seed: {}'.format(seed)
	else:
		seed = random.randrange(sys.maxsize)
		datapack_desc = 'Minecraft Randomizer, Seed: {}'.format(seed)
	datapack_filename = args.output
	print('Generating datapack...')

	minecraft_jar = zipfile.ZipFile(args.jarfile)
	all_files = minecraft_jar.namelist()
	loot_file_dict = random_remapping(
		get_childfiles(
			minecraft_jar, 
			'data/minecraft/loot_tables/', 
			blacklist=args.loot_blacklist, 
			categories=args.loot_categories
		)
	)
	craft_file_dict = random_remapping(
		get_childfiles(
			minecraft_jar,
			'data/minecraft/recipes/',
			blacklist=args.crafting_blacklist
		)
	)
	
	zipbytes = io.BytesIO()
	pack = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)
	pack.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))
	pack.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))
	pack.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Minecraft randomizer by ForOhForError, original by SethBling","color":"blue"}]')

	if args.unlock_recipes:
		pack.writestr('data/minecraft/tags/functions/tick.json', json.dumps({'values':['{}:giveallrecipes'.format(datapack_name)]}))
		pack.writestr('data/{}/functions/giveallrecipes.mcfunction'.format(datapack_name), '\n'.join(TICK_FUNCTION))

	if args.loot:
		randomize_loot(minecraft_jar, pack, loot_file_dict, do_hints=args.loot_hints)
	
	if args.crafting:
		randomize_crafting(minecraft_jar, pack, craft_file_dict)
		
	minecraft_jar.close()
	pack.close()
	with open(datapack_filename, 'wb') as pack_file:
		pack_file.write(zipbytes.getvalue())
		
	print('Created datapack "{}"'.format(datapack_filename))

if __name__ == '__main__':
	sys.exit(main(sys.argv))
