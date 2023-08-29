import subprocess

blender_executable = "C:/Program Files/Blender Foundation/Blender 3.2/blender.exe"  # Replace with the actual path to the Blender executable
script_path = "C:/primary/mm/mm.py"  # Replace with the path to your script

# Build the command to run Blender with the script
command = [blender_executable, "--background", "--python", script_path]

# Run the command
subprocess.call(command)

print("mm gotov")

# Specify the path to the other script
other_script_path = "C:/primary/fr/runs_fr.py"

# Execute the other script
exec(open(other_script_path).read())