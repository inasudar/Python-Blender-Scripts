import subprocess

blender_executable = "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe"  # Replace with the actual path to the Blender executable
script_path = "C:/primary/fr/fr.py"  # Replace with the path to your script

# Build the command to run Blender with the script
command = [blender_executable, "--background", "--python", script_path]

# Run the command
subprocess.call(command)

print("fr gotov")