import os
import random
import io
import zipfile
import json
import sys
import argparse
import re

DEFAULT_LOOT_BLACKLIST = ['.*_shulker_box\.json']
DEFAULT_CRAFTING_BLACKLIST = []

TICK_FUNCTION = [
	'execute as @a[tag=!learnedallrecipes] run recipe give @a *',
	'tag @a[tag=!learnedallrecipes] add learnedallrecipes'
]

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

def get_childfiles(inzip, subpath, blacklist=[]):
	all_files = inzip.namelist()
	result_list = []
	blacklist = [re.compile(pattern) for pattern in blacklist]
	for path in all_files:
		last_path = path.split('/')[-1]
		if path.startswith(subpath) and not inzip.getinfo(path).is_dir() and all(
			[not pattern.fullmatch(last_path) for pattern in blacklist]
		):
			result_list.append(path)
	return result_list

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
		help='Regex patterns to exclude from loot randomization; defaults to excluding shulker boxes.',
		nargs='*', default=DEFAULT_LOOT_BLACKLIST
	)
	parser.add_argument(
		'--crafting-blacklist', 
		help='Regex patterns to exclude from loot randomization; defaults to empty.',
		nargs='*', default=DEFAULT_CRAFTING_BLACKLIST
	)
	parser.add_argument(
		'--unlock-recipes', 
		help='Adds a function to the datapack to grant players all recipes on joining the server. Defaults to false.',
		action='store_true'
	)
	parser.add_argument('jarfile', type=str, help='path to minecraft jar file')
	args = parser.parse_args()
	datapack_name = 'mc_random'
	datapack_desc = 'Minecraft Randomizer'

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
	datapack_filename = args.output
	print('Generating datapack...')

	minecraft_jar = zipfile.ZipFile(args.jarfile)
	all_files = minecraft_jar.namelist()
	loot_file_dict = random_remapping(get_childfiles(minecraft_jar, 'data/minecraft/loot_tables/', blacklist=args.loot_blacklist))
	craft_file_dict = random_remapping(get_childfiles(minecraft_jar, 'data/minecraft/recipes/', blacklist=args.crafting_blacklist))
	
	zipbytes = io.BytesIO()
	pack = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)
	pack.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))
	pack.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))
	pack.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Minecraft randomizer by ForOhForError, original by SethBling","color":"blue"}]')

	if args.unlock_recipes:
		pack.writestr('data/minecraft/tags/functions/tick.json', json.dumps({'values':['{}:giveallrecipes'.format(datapack_name)]}))
		pack.writestr('data/{}/functions/giveallrecipes.mcfunction'.format(datapack_name), '\n'.join(TICK_FUNCTION))

	if args.loot:
		for from_file in loot_file_dict:
			contents = ''
			with minecraft_jar.open(from_file) as content_file:
				contents = content_file.read()
			pack.writestr(loot_file_dict[from_file], contents)
	
	if args.crafting:
		randomize_crafting(minecraft_jar, pack, craft_file_dict)
		
	minecraft_jar.close()
	pack.close()
	with open(datapack_filename, 'wb') as pack_file:
		pack_file.write(zipbytes.getvalue())
		
	print('Created datapack "{}"'.format(datapack_filename))

if __name__ == '__main__':
	sys.exit(main(sys.argv))
