import bpy
import math
import json
import os
import pathlib
import re

print("start")

bpy.context.space_data.shading.type = 'MATERIAL'

# Importing Blender modules
clean_module = bpy.data.texts["Clean"].as_module()
colors_module = bpy.data.texts["Colors"].as_module()
object_control_module = bpy.data.texts["Object Control"].as_module()

object_control_module.change_mode(mode="OBJECT")

CONFIG_FILE_PATH = pathlib.Path(f"{bpy.data.filepath}/../../config-primary.json").as_posix()

print("imported blender modules")

# Reading config json
with open(CONFIG_FILE_PATH) as config_file:
    DATA = json.load(config_file)

print("read config json")

# Constants
ABSOLUTE_FOLDER_PATH = pathlib.Path(DATA["absolute_folder_path"]).as_posix()
INPUT_FOLDER = pathlib.Path(DATA["map_materials"]["input_folder"]).as_posix()
OUTPUT_FOLDER = pathlib.Path(DATA["map_materials"]["output_folder"]).as_posix()
COLORS_MATERIALS_MAP_FILE = pathlib.Path(DATA["map_materials"]["colors_materials_map_file"]).as_posix()
INPUT_FOLDER_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, INPUT_FOLDER)).as_posix()
OUTPUT_FOLDER_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, OUTPUT_FOLDER)).as_posix()
COLORS_MATERIALS_MAP_FILE_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, COLORS_MATERIALS_MAP_FILE)).as_posix()

print("defines constants")

# Gives error if input folder doesn't exist
assert os.path.exists(INPUT_FOLDER_PATH) == True, f"{INPUT_FOLDER_PATH} folder doesn't exist"
assert os.path.exists(COLORS_MATERIALS_MAP_FILE_PATH) == True, f"{COLORS_MATERIALS_MAP_FILE_PATH} file doesn't exist"

print("error occured")

# Reading colors json
with open(COLORS_MATERIALS_MAP_FILE_PATH) as colors_materials_map_file:
    COLORS_MATERIALS_MAP_DATA = json.load(colors_materials_map_file)
    print(COLORS_MATERIALS_MAP_DATA)

print("read colors json")

# Creates output folder
try:
    os.makedirs(OUTPUT_FOLDER_PATH)

print("created output folder")
    
except FileExistsError:
    pass

print("for loop")

for file in os.listdir(INPUT_FOLDER_PATH):
    scene_objects = [object for object in bpy.data.objects]
    clean_module.clean_all(scene_objects)
    
    import_file_path = pathlib.Path(os.path.join(INPUT_FOLDER_PATH, file)).as_posix()
    extension = re.findall("\.[^.]*$", file)[0]
    file_name = file.replace(extension, "") 
    if not object_control_module.import_model(import_file_path):
        continue 
    
    object_color_map = {}
    imported_meshes = [object for object in bpy.context.selected_objects if object.type == "MESH"]
    clean_module.clean_empty()
    for mesh in imported_meshes:
        material = mesh.active_material
        inputs = material.node_tree.nodes["Principled BSDF"].inputs
        color = inputs["Base Color"].default_value
        
        hex_color = colors_module.to_hex(color[0], color[1], color[2])
        object_color_map[mesh] = hex_color.upper()    
        
    for object, color in object_color_map.items():
        print("ovo je objekt",object,"ovo je color", color)
        if color in COLORS_MATERIALS_MAP_DATA:
            for slot in object.material_slots:
                try:
                    slot.material = bpy.data.materials[COLORS_MATERIALS_MAP_DATA[color]]
                
                except:
                    pass

    print("finished for loop")
    
    # Exporting file
    export_file_path = pathlib.Path(os.path.join(OUTPUT_FOLDER_PATH, file)).as_posix()        
    object_control_module.export_model(export_file_path, "gltf")

    print("exported file")
    
    # Deleting imported meshes
    clean_module.clean_all(imported_meshes)

    print("deleted imported mesh")

    # Remove unused meshes
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)

    print("removed unused mesh")