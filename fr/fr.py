import bpy
import os

# Specify the path to the blend file
blend_file_path = "C:/Users/Challenge08/Documents/bb-renderer/scripts-primary/folder-render.blend"

# Specify the name of the text data block to run
text_block_name = "Text"

# Open the blend file
bpy.ops.wm.open_mainfile(filepath=blend_file_path)

# Get the text data block by its name
text_block = bpy.data.texts.get(text_block_name)

# Check if the text block exists
if text_block:
    # Execute the text block as a Python script
    exec(text_block.as_string())
else:
    print(f"Text block '{text_block_name}' not found.")
