import sys
import os
import json

current_directory = os.getcwd()

def create_folder_structure_json(directory, output_file=None, exclude_folders=None):
    """
    Creates a JSON file representing the folder structure and files of the given directory.
    
    Args:
        directory (str): The root directory to scan.
        output_file (str): The JSON file to write the structure to.
        exclude_folders (list): List of folder names to exclude from the structure.
    """
    # Default to an empty list if no folders are specified to exclude
    exclude_folders = exclude_folders or []

    def folder_to_dict(path):
        """
        Recursively builds a dictionary representation of the folder structure.
        
        Args:
            path (str): The path to the folder to process.
        
        Returns:
            dict: Dictionary representing the folder structure, or None if folder is excluded.
        """
        # Skip excluded folders
        if os.path.basename(path) in exclude_folders:
            return None

        folder_dict = {'name': os.path.basename(path), 'type': 'folder', 'children': []}
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    subfolder = folder_to_dict(item_path)
                    if subfolder:  # Only append non-None results (folders that are not excluded)
                        folder_dict['children'].append(subfolder)
                else:
                    folder_dict['children'].append({'name': item, 'type': 'file'})
        except PermissionError:
            folder_dict['children'].append({'name': 'Permission Denied', 'type': 'error'})
        
        return folder_dict

    # Build the structure starting from the root directory
    folder_structure = folder_to_dict(directory)
    
    # If the root folder is excluded, return an empty structure
    if not folder_structure:
        folder_structure = {'name': 'root', 'type': 'folder', 'children': []}
    
    # Write the structure to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(folder_structure, f, indent=4)
    
    print(f"Folder structure saved to {output_file}")

# Example usage
create_folder_structure_json(os.path.join(current_directory, "1908235722"), "folder_structure.json", exclude_folders=["__pycache__"])
