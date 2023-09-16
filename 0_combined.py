import tkinter as tk
from tkinter import filedialog
import zipfile
import subprocess
import re

IsaacGymEnvs_path='/home/sujit/Desktop/IsaacGymEnvs-main/isaacgymenvs'
IsaacGym_path='/home/sujit/Desktop/isaacgym'
zippath = "/home/sujit/Desktop/isaacgymn envs frozen/"

print("Frozen state helper for IsaanGynEnvs by SujitVasanth Sep 2023")
print("=============================================================")
choice=input("1 to save state to a zip, 2 to restore from a zip\n\n")

if choice =="1":
    print("Save frozen files")
    filez=input("What would you like to call the zip? ")
    compression = zipfile.ZIP_DEFLATED

    # create the zip file first parameter path/name, second mode
    zf = zipfile.ZipFile(zippath+filez+".zip", mode="w")
    try:
        zf.write(IsaacGymEnvs_path+"/tasks/biped.py","biped.py", compress_type=compression)
        zf.write(IsaacGymEnvs_path+"/cfg/task/Biped.yaml","Biped.yaml", compress_type=compression)
        zf.write(IsaacGymEnvs_path+"/cfg/train/BipedPPO.yaml","BipedPPO.yaml", compress_type=compression)
        #zf.write(IsaacGym_path+"/assets/urdf/Biped.urdf","Biped.urdf", compress_type=compression)
        pattern = re.compile(r'(?<=").*\.urdf(?=")')
        results = []
        with open(IsaacGymEnvs_path+"/tasks/biped.py", "r") as file:
            for line in file:
                matches = pattern.findall(line)
                if matches:
                    results.extend(matches)
        for result in results:
            zf.write(IsaacGym_path+"/assets/"+result, result.split("/")[-1], compress_type=compression)
    except FileNotFoundError:
        print("Unsuccessful")
    finally:
        zf.close()
        print("Zip was created at "+zippath+filez+".zip")
        choice = input("Would you like to open the folder y or n? ")
        if choice=="y": subprocess.Popen(["xdg-open", zippath])

elif choice =="2":
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir=zippath,title="Select Frozen ZIP to restore", filetypes=[("ZIP files", "*.zip")])
    print(f"extracting from "+file_path)
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extract('biped.py', path=IsaacGymEnvs_path+'/tasks')
            zip_ref.extract('Biped.yaml', path=IsaacGymEnvs_path+'/cfg/task')
            zip_ref.extract('BipedPPO.yaml', path=IsaacGymEnvs_path+'/cfg/train')
            for name in zip_ref.namelist():
                if name.endswith('.urdf'):
                    file_name = name.split('/')[-1]  # Extract the file name without any directories
                    zip_ref.extract(name, path=IsaacGym_path+'/assets/urdf/')
    except: FileNotFoundError; print("File error caused only partial zip extraction")
    finally:
        print("Extraction successful")
        root.destroy()# Close the GUI window
        

        print(f"Checkings that tasks list includes Biped at /tasks/__init__.py")
        with open(IsaacGymEnvs_path+"/tasks/__init__.py", 'r') as f:
            lines = f.readlines()
        changes=0

        import_statement = "from tasks.biped import Biped"
        if import_statement not in [line.strip() for line in lines]:
            last_import_index = max(idx for idx, line in enumerate(lines) if line.strip().startswith("from tasks.") or line.strip().startswith("from isaacgymenvs.tasks."))
            lines.insert(last_import_index + 1, import_statement + '\n')
            changes=changes+1

        isaacgym_task_map_index = next(i for i, line in enumerate(lines) if 'isaacgym_task_map' in line)
        closing_bracket_index = next(i for i, line in enumerate(lines[isaacgym_task_map_index:]) if '}' in line) + isaacgym_task_map_index
        # Check if Biped is already in the dictionary
        dict_entry = '"Biped": Biped'
        if not any(dict_entry in line.strip() for line in lines[isaacgym_task_map_index:closing_bracket_index]):
            # Ensure the closing bracket is on its own line
            if not lines[closing_bracket_index].strip() == "}":
                split_line = lines[closing_bracket_index].split("}")
                lines[closing_bracket_index] = split_line[0] + "\n"
                lines.insert(closing_bracket_index + 1, "}" + split_line[1] + "\n")
                closing_bracket_index += 1
            # Add a comma to the line before the closing bracket
            if not lines[closing_bracket_index - 1].strip().endswith(","):
                lines[closing_bracket_index - 1] = lines[closing_bracket_index - 1].rstrip() + ",\n"
            # Insert the Biped entry just before the closing bracket
            lines.insert(closing_bracket_index, "    "+dict_entry+"\n")
            changes=changes+1

        if changes>0:
            # Write the updated content back to the file
            with open(IsaacGymEnvs_path+"/tasks/__init__.py", 'w') as f:
                f.writelines(lines)
            print(f"imports and dictionary updated")
        else:
            print(f"Biped config already present - no changes needed")

else:
    print(f"Invalid choice - closing")
