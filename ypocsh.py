# importing required module 
import winreg as wrg
import traceback
import shutil
import os
import msvcrt
import logging
from tkinter import filedialog
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class DataContainer():
    def __init__(self):
        self.flcrc = False
        self.common_path = False
        self.registry_entry = False
    def set_flcrc(self, value):
        self.flcrc = value
    def get_flcrc(self):
        if self.flcrc:
            return self.flcrc
        else:
            raise Exception("Retrieving empty flcrc")
    def set_common(self, value):
        self.common_path = value
    def get_common(self):
        if self.common_path:
            return self.common_path
        else:
            raise Exception("Retrieving empty common_path")
    def set_registry(self, value):
        self.registry_entry = value
    def get_registry(self):
        if self.registry_entry:
            return self.registry_entry
        else:
            raise Exception("Retrieving empty registry entry")    

logger = logging.getLogger("log")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

logging.basicConfig(filename='log.log', level=logging.INFO, filemode="w")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                              "%Y-%m-%d %H:%M:%S")
formatter2 = logging.Formatter("%(message)s")
handler.setFormatter(formatter2)
logger.addHandler(handler)
container = DataContainer()
    

def main_menu():
    print("\n\nMAIN MENU\n\nSlot list: ")
    slots = verify_slots()
    for i in range(len(slots)):
        print(f"{i+1} - {'Occupied' if slots[i] else 'Not occupied'}")
    print("Please select a slot number or press Esc to exit program")
    while True:
        try:
            response = msvcrt.getch().decode("ascii")
            break
        except:
            continue
    if response == "\x1b" or response == "\x03":
        print("Exiting...")
        return
    else:
        try:
            response = int(response)
        except:
            pass #in case the response is invalid just ignore
    while response not in [1,2,3,4,5]:
        try:
            response = msvcrt.getch().decode("ascii")
        except:
            continue
        if response == "\x1b" or response == "\x03":
            print("Exiting...")
            return
        else:
            try:
                response = int(response)
            except:
                pass #in case the response is invalid just ignore
    handle_slot_pick(response)
def handle_slot_pick(slot_number):
    print(f"\n\nSelected slot {slot_number}\n")
    if verify_slot(slot_number):
        handle_full_slot(slot_number)
    else:
        handle_empty_slot(slot_number)
def handle_empty_slot(slot_number):
    print("Please select an option or press Esc to go back to main menu.\n1) Save backup to this slot")
    response = msvcrt.getch().decode("ascii")
    if response == "\x1b":
        main_menu()
    elif response == "\x03":
        print("Exiting...")
        return
    else:
        try:
            response = int(response)
        except:
            pass #in case the response is invalid just ignore
    while response != 1:
        response = msvcrt.getch().decode("ascii")
        if response == "\x1b":
            main_menu()
        elif response == "\x03":
            print("Exiting...")
            return
        else:
            try:
                response = int(response)
            except:
                pass #in case the response is invalid just ignore
    try:
        save_backup(slot_number)
        info(f"Backup saved at slot {slot_number}.")
        print("Going back to menu!")
        main_menu()
    except:
        info(f"Backup process failed: {traceback.format_exc()}")
def handle_full_slot(slot_number):
    print("Please select an option or press Esc to go back to main menu.\n1) Save backup to this slot\n2) Load this backup to disk")
    response = msvcrt.getch().decode("ascii")
    if response == "\x1b":
        main_menu()
    elif response == "\x03":
        print("Exiting...")
        return
    else:
        try:
            response = int(response)
        except:
            pass #in case the response is invalid just ignore
    while response not in [1,2]:
        response = msvcrt.getch().decode("ascii")
        if response == "\x1b":
            main_menu()
        elif response == "\x03":
            print("Exiting...")
            return
        else:
            try:
                response = int(response)
            except:
                pass #in case the response is invalid just ignore
    if response == 1:
        try:
            save_backup(slot_number)
            print("Backup saved! Going back to menu.")
            main_menu()
        except:
            print(f"Oh no... {traceback.format_exc()}")
    elif response == 2:
        load_backup(slot_number)
def save_backup(slot_number):
    try:
        a = open(f"{slot_number}/flcrc.txt", "wb")
    except FileNotFoundError:
        os.mkdir(f"{slot_number}")
        a = open(f"{slot_number}/flcrc.txt", "wb")
    with a:
        a.write(container.get_flcrc())
        shutil.copy2(container.get_common()+r"\system.dat", f"{slot_number}/system.dat")
def load_backup(slot_number):
    print("Doing this will overwrite your Yu-Gi-Oh! Power Of Chaos save data!\nConfirm this action by pressing ENTER or press Esc to go back to main menu.")
    while True:
        try:
            response = msvcrt.getch().decode("ascii")
        except:
            continue
        if response == "\x1b" or response == "\x03":
            print("Going back to menu...")
            main_menu()
        elif response=="\r":
            break
        else:
            continue
    
    backslash = r"\\"
    a = open(f"{slot_number}/flcrc.txt", "rb")
    with a:
        flcrc = a.read()
    reg_folder = container.get_registry()
    location = handle_location(reg_folder[0])
    path_list = reg_folder[1].split("/")
    backslash = r'\\'
    path = backslash.join(path_list)
    info("Attempting to copy system.dat to common folder...")
    try:
        shutil.copy2(f"{slot_number}/system.dat", container.get_common()+r"\system.dat")
        info("SUCCESS!")
    except:
        error(f"Could not copy system.dat to common folder: {traceback.format_exc()}")
    info("Attempting to modify registry entry...")
    try:
        key_folder = wrg.OpenKeyEx(handle_location(container.get_registry()[0]), fr'{container.get_registry()[1].replace("/", backslash)}', 0, wrg.KEY_SET_VALUE)
        wrg.SetValueEx(key_folder, "flcrc", 0, wrg.REG_BINARY, flcrc)
        info("SUCCESS!")
        key_folder.Close()
    except:
        error(f"Could not modify registry entry: {traceback.format_exc()}")
        return
    info("Backup successfully loaded!")
    print("Going back to main menu...")
    main_menu()
    
    
def verify_slot(slot_number):
    return os.path.exists(f"{slot_number}/system.dat") and os.path.exists(f"{slot_number}/flcrc.txt")
def verify_slots():
    slots = []
    for i in range(1, 6):
        if verify_slot(i):
            slots.append(True)
        else:
            slots.append(False)
    return slots
    
def debug(message):
    logger.log(10, message)
def info(message):
    logger.log(20, message)
def warn(message):
    logger.log(30, message)
def error(message):
    logger.log(40, message)

def handle_location(loc):
    if loc=="current_user":
        return wrg.HKEY_CURRENT_USER
    elif loc == "classes_root":
        return wrg.HKEY_CLASSES_ROOT
    elif loc == "local_machine":
        return wrg.HKEY_LOCAL_MACHINE
def checkForFlcrc(location, path):
    backslash = r"\\"
    key_path = backslash.join(path)+backslash
    key = wrg.OpenKey(location, key_path, 0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY)
    counter = 0
    while True:
        try:
            value = wrg.EnumValue(key, counter)
            if value[0] == "flcrc":
                return True
            counter += 1
        except:
            key.Close()
            return False
def searchUntilSystem(location, path): #search registry tree until system folder is found
    backslash = r"\\"
    key_path = backslash.join(path)+backslash
    try:
        key = wrg.OpenKey(location, key_path, 0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY)
    except FileNotFoundError:
        try:
            key = wrg.OpenKey(location, key_path, 0, wrg.KEY_READ | wrg.KEY_WOW64_32KEY)
        except FileNotFoundError:
            return False
    except PermissionError:
        return False
    sub_keys = []
    counter = 0
    while True:
        try:
            subkey = wrg.EnumKey(key, counter)
        except FileNotFoundError:
            counter += 1
        except OSError:
            #print(traceback.format_exc())
            return False
        try:
            if subkey == 'system':
                path.append("system")
                if checkForFlcrc(location, path):
                    info(f"FOUND SYSTEM: {key_path+'system'}")
                    return fr"{key_path}"
            else:
                new_path = path + [subkey]
                path_candidate = searchUntilSystem(location, new_path)
                if path_candidate:
                    return path_candidate
                    
            counter += 1
        
        
        except:
            counter+=1   
def searchRegistryFolder():
    backslash = r"\\"
    locations = ["local_machine", "current_user", "classes_root"]
    for location in locations:
        info(f"Scanning location: {location}")
        location_code = handle_location(location)
        key = wrg.OpenKey(location_code, "", 0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY)
        
        counter = 0
        while True:
            try:
                #print(wrg.EnumKey(key, counter))
                path = searchUntilSystem(location_code, [wrg.EnumKey(key, counter)])
                if path:
                    return [location, fr"{path}system", "system"]
                counter += 1
            except:
                break
            
def lookForFolder(location, path, folder_name):
    location = handle_location(location)
    path_list = path.split("/")
    backlash_char = r"\\"
    try:
        key = wrg.OpenKey(location, fr"{backlash_char.join(path_list)}", 0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY)
    except:
        return False
    counter = 0
    while True:
        try:
            if wrg.EnumKey(key, counter) == folder_name:
                return True
            counter+=1
        except:
            return False
        
def lookForKey(location, path, key_name):
    location = handle_location(location)
    path_list = path.split("/")
    backlash_char = r"\\"    
    key = wrg.OpenKey(location, fr"{backlash_char.join(path_list)}", 0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY)
    counter = 0
    while True:
        try:
            if wrg.EnumValue(key, counter)[0] == key_name:
                return True
            counter += 1
        except:
            return False
        
def findRegistryFolder():
    possible_folders = [("classes_root", "VirtualStore/MACHINE/SOFTWARE/WOW6432Node/KONAMI/Yu-Gi-Oh! Power Of Chaos", "system")]
    for folder in possible_folders:
        if lookForFolder(*folder): #check if key exists in registry
            if lookForKey(folder[0], folder[1]+"/"+folder[2], "flcrc"):
                return folder
            else:
                return False
    else:
        return False
def verifyCommonFolder(folder_path):
    if os.path.exists(folder_path):
        info("Found common dir on disk.")
    else:
        error(f"Common dir not found at {folder_path}")
        return False
    if os.path.exists(folder_path+r"\system.dat"):
        info("Found system.dat")
    else:
        error(f"system.dat not found at {folder_path}")
        return False
    return True
    
def getSubKeys(folder):
    return_dict = {"flcrc": None, "common_path": None}
    location = handle_location(folder[0])
    path_list = folder[1].split("/")
    backlash_char = r"\\"
    try:
        key = wrg.OpenKey(location, fr"{backlash_char.join(path_list)}", 0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY)
    except FileNotFoundError:
        key = wrg.OpenKey(location, fr"{backlash_char.join(path_list)}", 0, wrg.KEY_READ | wrg.KEY_WOW64_32KEY)
    counter = 0
    while True:
        try:
            value = wrg.EnumValue(key, counter)
            if value[0] == "flcrc":
                info(f"Found flcrc in registry - {value[1]}")
                return_dict["flcrc"] = value[1]
            elif value[0] == "CommonDir":
                info(f"Found common dir in registry - {value[1]}")
                return_dict["common_path"] = value[1]
            counter += 1
        except:
            return return_dict
def main(folder=False):
    backslash = r"\\"
    if folder:
        debug(f"Found registry key - {folder}")
        container.set_registry(folder)
        sub_keys = getSubKeys(folder)
        for sub_key in sub_keys:
            if sub_keys[sub_key] == None:
                error(f"Cannot fetch required data.\nData fetched:\n{sub_keys}\nData that is 'None' wasn't fetched properly!\n")
                os.system('pause')
                return
        common_path = sub_keys["common_path"]
        while not verifyCommonFolder(common_path):
            print("1) Manually locate common folder\n2) Exit the program")
            response = msvcrt.getch().decode("ascii")
            if response.lower() == "1":
                common_path = filedialog.askdirectory(title="Please locate Yu-Gi-Oh! Power Of Chaos Common folder")
            elif response.lower() == "2":
                return
        if common_path != sub_keys["common_path"]:
            info("The registry entry for common folder and the actual folder path do no match.\nDo you want to fix the registry entry? (NOT recommended if everything is working correctly)\n1) Fix common path in registry\n2) Proceed with the program")
            while True:
                response = msvcrt.getch().decode("ascii")
                if response.lower() == "1":
                    info("Attempting to modify registry entry...")
                    try:
                        key_folder = wrg.OpenKeyEx(handle_location(container.get_registry()[0]), (container.get_registry()[1]+"/"+container.get_registry()[2]).replace("/", backslash), 0, wrg.KEY_SET_VALUE)
                        wrg.SetValueEx(key_folder, "CommonDir", 0, wrg.REG_SZ, common_path.replace("/", "\\"))
                        info("SUCCESS!")
                        key_folder.Close()
                        break
                    except:
                        error(f"Could not modify registry entry: {traceback.format_exc()}")
                elif response.lower() == "2":
                    break
        container.set_common(common_path)
        container.set_flcrc(sub_keys["flcrc"])
        main_menu()
    else:
        info("Searching through registry for required key...")
        
        folder = searchRegistryFolder()
        if folder:
            main(folder)
        else:
            error("Failed to find registry folder. Exiting.")




if is_admin():
    main()
else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)