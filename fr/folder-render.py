import bpy
import os
import json
import math
import pathlib
import re


# Importing blender modules
clean_module = bpy.data.texts["Clean"].as_module()
render_module = bpy.data.texts["Render"].as_module()
object_control_module = bpy.data.texts["Object Control"].as_module()

object_control_module.change_mode(mode="OBJECT")

CONFIG_FILE_PATH = pathlib.Path(f"{bpy.data.filepath}/../../config-primary.json").as_posix()

# Reading config json
with open(CONFIG_FILE_PATH) as config_file:
    DATA = json.load(config_file)

# Constants
ABSOLUTE_FOLDER_PATH = pathlib.Path(DATA["absolute_folder_path"]).as_posix()
MODELS_FOLDER = pathlib.Path(DATA["render"]["input_folder"]).as_posix()
RENDERS_FOLDER = pathlib.Path(DATA["render"]["output_folder"]).as_posix()
FORMAT = DATA["render"]["format"]
COMPANY_NAME = DATA["company_name"]
MODELS_FOLDER_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, MODELS_FOLDER)).as_posix()
RENDERS_FOLDER_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, RENDERS_FOLDER)).as_posix()

# Current working camera views
VIEWS = [object.name for object in bpy.context.scene.objects if object.type == "CAMERA"]

# Gives error if models folder doesn't exist
assert os.path.exists(MODELS_FOLDER_PATH) == True, f"{MODELS_FOLDER_PATH} folder doesn't exist"

# Creates renders_folder
try:
    os.makedirs(RENDERS_FOLDER_PATH)
    
except FileExistsError:
    pass


for file in os.listdir(MODELS_FOLDER_PATH):
    import_file_path = pathlib.Path(os.path.join(MODELS_FOLDER_PATH, file)).as_posix() 
    extension = re.findall("\.[^.]*$", file)[0]
    file_name = file.replace(extension, "")
    if not object_control_module.import_model(import_file_path):
        continue
    
    imported_meshes = [object for object in bpy.context.selected_objects if object.type == "MESH"]
    clean_module.clean_empty()        
    
    for view in VIEWS:
        if DATA["render"]["views"][view] == 1:
            # Setting up view
            bpy.context.scene.camera = bpy.data.objects[view]
            
            # Rendering
            render_module.render(file, view, FORMAT, RENDERS_FOLDER_PATH, COMPANY_NAME)
                           
    clean_module.clean_all(imported_meshes)
    
    # Remove unused meshes
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)