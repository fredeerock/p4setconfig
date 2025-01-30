import subprocess
import os

def find_project_root():
    """Finds the nearest directory containing an .uproject file."""
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        for file in os.listdir(current_dir):
            if file.endswith(".uproject"):
                return current_dir
        current_dir = os.path.dirname(current_dir)  # Move up one level
    return None  # Not found

def get_p4_variable(var_name):
    """Runs 'p4 set' and extracts the value of a given Perforce variable."""
    try:
        result = subprocess.run(["p4", "set", var_name], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if line.startswith(f"{var_name}="):
                return line.split("=")[1].split(" (")[0].strip()  # Extract value before any parentheses
    except subprocess.CalledProcessError:
        pass
    return None

def create_p4config(project_root):
    """Creates a .p4config file with the active Perforce workspace, user, server, and ignore file."""
    p4client = get_p4_variable("P4CLIENT")
    p4user = get_p4_variable("P4USER")
    p4port = get_p4_variable("P4PORT")
    
    p4ignore_path = os.path.join(project_root, ".p4ignore")  # Ensure P4IGNORE is in the config

    if p4client and p4user and p4port:
        config_content = f"""P4CLIENT={p4client}
P4USER={p4user}
P4PORT={p4port}
P4IGNORE={p4ignore_path}
"""
        config_path = os.path.join(project_root, ".p4config")

        with open(config_path, "w") as config_file:
            config_file.write(config_content)

        print(f".p4config file created successfully in {project_root}:\n{config_content}")
    else:
        print("Error: Could not retrieve all Perforce settings. Ensure you are logged into Perforce.")

def create_p4ignore(project_root):
    """Creates a .p4ignore file with Unreal Engine project ignore rules."""
    ignore_content = """# Unreal Engine Ignore Rules

# Binaries, intermediates, and temporary files
Binaries/
DerivedDataCache/
Intermediate/
Saved/
Build/
*.sln
*.VC.db
*.VC.opendb
*.sdf
*.suo
*.tmp
*.log
*.dmp
*.pdb

# Ignore Unreal Engine autosave files
*_Backup_*/
*.autosave

# Ignore built and packaged files
Packages/
BuildOutput/
Dist/

# Ignore specific Unreal Engine files
*.xcodeproj
*.xcworkspace
*.DS_Store
Thumbs.db
"""

    ignore_path = os.path.join(project_root, ".p4ignore")

    with open(ignore_path, "w") as ignore_file:
        ignore_file.write(ignore_content)

    print(f".p4ignore file created successfully in {project_root}.")

# Main script execution
project_root = find_project_root()
if project_root:
    os.chdir(project_root)  # Ensure we are in the project root
    print(f"Unreal project root detected: {project_root}")
    create_p4ignore(project_root)  # Ensure .p4ignore exists before referencing it
    create_p4config(project_root)
else:
    print("Error: Could not find Unreal project root. Please run this script inside an Unreal project directory.")

