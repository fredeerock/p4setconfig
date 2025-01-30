import subprocess
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QFileDialog, QLineEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def find_project_root():
    """Finds the nearest directory containing an .uproject file."""
    current_dir = os.getcwd()
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        for file in os.listdir(current_dir):
            if file.endswith(".uproject"):
                return current_dir
        current_dir = os.path.dirname(current_dir)  # Move up one level
    return None  # Not found

def get_p4_variable(var_name, directory):
    """Runs 'p4 set' in the specified directory and extracts the value of a given Perforce variable."""
    try:
        result = subprocess.run(["p4", "set"], cwd=directory, capture_output=True, text=True, check=True)
        if result.returncode != 0:
            print(f"Error running 'p4 set': {result.stderr}")
            return None
        print(f"Output of 'p4 set':\n{result.stdout}")  # Display the output before parsing
        for line in result.stdout.splitlines():
            if line.startswith(f"{var_name}="):
                return line.split("=")[1].split(" ")[0].strip()  # Extract value before any spaces
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

def create_p4config(project_root):
    """Creates a .p4config file with the active Perforce workspace, user, server, and ignore file."""
    p4client = get_p4_variable("P4CLIENT", project_root)
    p4user = get_p4_variable("P4USER", project_root)
    p4port = get_p4_variable("P4PORT", project_root)
    
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
        error_message = "Error: Could not retrieve all Perforce settings. Ensure you are logged into Perforce."
        print(error_message)
        return error_message

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

class P4ConfigGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('P4 Config Generator')
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

        self.status_label = QLabel('This program generates a .p4conifg and .p4ignore file for an Unreal Project.\n\n1. Make sure you are logged into Perforce.\n2. Either run this program next to your .uproject file or browse to its locaiton.\n3. Press the button to generate .p4config and .p4ignore files.')
        self.status_label.setFont(QFont('Segoe UI', 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText('Enter path to the folder with .uproject file or leave empty to auto-detect')
        layout.addWidget(self.path_input)

        self.browse_button = QPushButton('Browse')
        self.browse_button.setFont(QFont('Segoe UI', 10))
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.generate_button = QPushButton('Generate Config Files')
        self.generate_button.setFont(QFont('Segoe UI', 10))
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.generate_button.clicked.connect(self.generate_files)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path:
            self.path_input.setText(folder_path)

    def generate_files(self):
        project_root = self.path_input.text() or find_project_root()
        if project_root and os.path.exists(project_root):
            os.chdir(project_root)
            create_p4ignore(project_root)
            error_message = create_p4config(project_root)
            if error_message:
                QMessageBox.critical(self, 'Error', error_message)
            else:
                QMessageBox.information(self, 'Success', "Files created successfully")
        else:
            error_message = 'Could not find Unreal project root. Please provide a valid directory or run this script inside an Unreal project directory.'
            QMessageBox.critical(self, 'Error', error_message)

# Main script execution
if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    gui = P4ConfigGUI()
    gui.show()
    app.exec()

