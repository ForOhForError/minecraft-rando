import os
import random
import io
import zipfile
import json
import sys
import argparse

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

def get_childfiles(inzip, subpath):
	all_files = inzip.namelist()
	result_list = [
		path for path in all_files if 
		path.startswith(subpath) and
		zipfile.Path(inzip, path).is_file()
	]
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
		'-s', '--seed', type=int, help='randomization seed'
	)
	parser.add_argument(
		'--loot', help='randomize loot tables', action='store_true'
	)
	parser.add_argument(
		'--crafting', help='randomize crafting recipes', action='store_true'
	)
	parser.add_argument(
		'-o', '--output', help='output file', default='mc_random.zip'
	)
	parser.add_argument('jarfile', type=str, help='path to minecraft jar file')
	args = parser.parse_args()
	datapack_name = 'mc_random'
	datapack_desc = 'Minecraft Randomizer'

	if args.seed:
		seed = args.seed
		random.seed(seed)
		datapack_name = 'mc_random_{}'.format(seed)
		datapack_desc = 'Minecraft Randomizer, Seed: {}'.format(seed)
	datapack_filename = args.output
	print('Generating datapack...')

	minecraft_jar = zipfile.ZipFile(args.jarfile)
	all_files = minecraft_jar.namelist()
	loot_file_dict = random_remapping(get_childfiles(minecraft_jar, 'data/minecraft/loot_tables/'))
	craft_file_dict = random_remapping(get_childfiles(minecraft_jar, 'data/minecraft/recipes/'))
	minecraft_jar.close()
	minecraft_jar = zipfile.ZipFile(args.jarfile)
	
	zipbytes = io.BytesIO()
	pack = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)
	pack.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))
	pack.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))
	pack.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Minecraft randomizer by ForOhForError, original by SethBling","color":"blue"}]')

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
