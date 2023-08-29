import bpy
import json
import pathlib
import os
import mathutils


# Importing Blender modules
clean_module = bpy.data.texts["Clean"].as_module()
smart_uv_module = bpy.data.texts["Smart UV"].as_module()
object_control_module = bpy.data.texts["Object Control"].as_module()

object_control_module.change_mode(mode="OBJECT")

CONFIG_FILE_PATH = pathlib.Path(f"{bpy.data.filepath}/../../config-primary.json").as_posix()

# Reading config json
with open(CONFIG_FILE_PATH) as config_file:
    DATA = json.load(config_file)

# Constants
ABSOLUTE_FOLDER_PATH = pathlib.Path(DATA["absolute_folder_path"]).as_posix()
INPUT_FOLDER = pathlib.Path(DATA["center_scale_rotate"]["input_folder"]).as_posix()
OUTPUT_FOLDER = pathlib.Path(DATA["center_scale_rotate"]["output_folder"]).as_posix()
SCALE_CUBE_DIMENSIONS = tuple(DATA["center_scale_rotate"]["scale_cube_dimensions"])
EXPORT_FORMAT = DATA["center_scale_rotate"]["export_format"]
INPUT_FOLDER_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, INPUT_FOLDER)).as_posix()
OUTPUT_FOLDER_PATH = pathlib.Path(os.path.join(ABSOLUTE_FOLDER_PATH, OUTPUT_FOLDER)).as_posix()

# Gives error if input folder doesn't exist
assert os.path.exists(INPUT_FOLDER_PATH) == True, f"{INPUT_FOLDER_PATH} folder doesn't exist"

# Creates output folder
try:
    os.makedirs(OUTPUT_FOLDER_PATH)
    
except FileExistsError:
    pass


for file in os.listdir(INPUT_FOLDER_PATH):
    scene_objects = [object for object in bpy.data.objects]
    clean_module.clean_all(scene_objects)
    
    import_file_path = pathlib.Path(os.path.join(INPUT_FOLDER_PATH, file)).as_posix() 
    if not object_control_module.import_model(import_file_path):
        continue
    
    # Cleaning empties and sorting imported objects into meshes and empties
    imported_meshes = [object for object in bpy.context.selected_objects if object.type == "MESH"]
    clean_module.clean_empty()
    object_control_module.rename(imported_meshes, "mesh")
     
    # Joining objects
    imported_meshes = [object for object in bpy.context.selected_objects if object.name.startswith("mesh_")]
    active_object = bpy.data.objects["mesh_1"]
    object_control_module.join(imported_meshes, active_object)    
    
    # Rotating
    quaternion_angles = (active_object.rotation_quaternion.w, 
                        active_object.rotation_quaternion.x, 
                        active_object.rotation_quaternion.y, 
                        active_object.rotation_quaternion.z)
                        
    degree_angles = object_control_module.quaternion_to_degrees(*quaternion_angles)
    degree_angles = [angle % 360 for angle in degree_angles]
    
    for component in range(3):
        if degree_angles[component] % 90 != 0:
            if degree_angles[component] > 0 and degree_angles[component] < 90:
                degree_angles[component] = 90 if abs(90 - degree_angles[component]) < degree_angles[component] else 0    
            
            elif degree_angles[component] > 90 and degree_angles[component] < 180:
                degree_angles[component] = 180 if abs(180 - degree_angles[component]) < abs(90 - degree_angles[component]) else 90
                
            elif degree_angles[component] > 180 and degree_angles[component] < 270:
                degree_angles[component] = 270 if abs(270 - degree_angles[component]) < abs(180 - degree_angles[component]) else 180
                
            else:
                degree_angles[component] = 0 if abs(360 - degree_angles[component]) < abs(270 - degree_angles[component]) else 270
    
    object_control_module.rotate(active_object, 90, 0,0)
    
    # Scaling
    object_control_module.scale(active_object, SCALE_CUBE_DIMENSIONS)
    
    # Centering
    location = (0.0, 0.0, 0.0)
    object_control_module.move(active_object, location)
    
    # Merge by distance and smoothing
    object_control_module.merge_by_distance(active_object)
    
    # Separating object by lose parts
    object_control_module.separate(active_object)
    
    # Renaming all meshes
    meshes = [object for object in bpy.data.objects if object.name.startswith("mesh_")]
    object_control_module.rename(meshes, "mesh")
    
    # Smart UV for materials
    smart_uv_module.smart_uv()
    
    # Exporting file
    export_file_path = pathlib.Path(os.path.join(OUTPUT_FOLDER_PATH, file)).as_posix()        
    object_control_module.export_model(export_file_path, EXPORT_FORMAT)
    
    # Deleting meshes
    meshes = [object for object in bpy.data.objects if object.type == "MESH"]
    clean_module.clean_all(meshes)
    
    # Delete unused meshes
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)

    print("gotovo")