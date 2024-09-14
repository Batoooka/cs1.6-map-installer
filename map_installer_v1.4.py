import tkinter as tk
import shutil
import sys
import os
import subprocess
import json
import requests
from tkinter import messagebox, filedialog, ttk
import customtkinter as ctk
from PIL import Image, ImageTk

VERSION = 1.4
# for fetch() & search()
current_page = 1
results_per_page = 50
# cstrike folder path & Wanrar.exe path
game_folder = ""
exe_folder = ""
# user wanna delete the src file after extract it and move it to game folder
delete_after_extract = False
# is the setting window active
is_on = False
# for extract & moving game files conditions & cases
exepted_dirs = ["env", "gfx", "maps", "overviews", "models", "sound", "sprites", "cstrike"]
# color variables
# bg stand for background
bg_color = "white"
# active foreground 
afg_color = "#b2b2c0"
# fg stand for foreground
fg_color = "#7b7b7e"

# gui window
root = ctk.CTk()
root.title("Map Installer")
root.configure(bg=bg_color)
# postion the window in the mid of screen & window size
WINDOW_WIDTH = 450
WINDOW_HEIGHT = 600
display_width = root.winfo_screenwidth()
display_hieght = root.winfo_screenheight()

left = int(display_width / 2 - WINDOW_WIDTH / 2)
top = int(display_hieght / 2 - WINDOW_HEIGHT / 2)
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{left}+{top}")

# make the window un resizable
root.resizable(False , False)
# bind to close the gui window
root.bind("<Escape>", lambda event : root.quit())

#https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# create json file & show settings for first runtime gui
def load_settings():
    global game_folder, exe_folder , delete_after_extract
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            settings = json.load(f)
            game_folder = settings.get("game_folder", "")
            exe_folder = settings.get("exe_folder", "")
            delete_after_extract = settings.get("delete_after_extract", False)
    else:
        show_settings()
# save settings in .json file
def save_settings():
    with open("settings.json", "w") as f:
        json.dump({"game_folder": game_folder,
                    "exe_folder": exe_folder,
                    "delete_after_extract": delete_after_extract}, f)

def settings_page():
    global is_on ,settings_window
    if is_on == False:
        show_settings()
        is_on = True
    else:
        settings_window.destroy()
        is_on = False

# settings window
def show_settings():
    global game_folder_entry, exe_folder_entry, delete_after_extract_var,settings_window
    settings_window = ctk.CTkToplevel(root)
    # fix settings window on top of the main window
    settings_window.transient(root)
    settings_window.title("Settings")
    # make the window un resizable
    settings_window.resizable(False , False)
    # bind to close the gui window
    settings_window.bind("<Escape>", lambda event : settings_window.destroy())
    #ask for game folder path location
    game_folder_label = tk.Label(settings_window,
                                width=50,
                                height=3,
                                anchor="center",
                                bg="black",fg=bg_color,
                                font= ("Arial",22),
                                text="Game Folder (must end /cstrike):")
    game_folder_label.pack(pady=20)

    game_folder_entry = tk.Entry(settings_window,justify="center",width=45,font=("Arial",22))
    game_folder_entry.pack(padx=10,pady=20,ipady=10)
    game_folder_entry.insert(0, game_folder)

    game_folder_browse_button = tk.Button(settings_window,
                                        font=("Arial",20),
                                        width=10,
                                        text="Browse",
                                        command=browse_game_folder)
    game_folder_browse_button.pack(pady=20)

    #ask for Winrar.exe path location
    exe_folder_label = tk.Label(settings_window,
                                width=50,
                                height=3,
                                anchor="center",
                                bg="black",
                                fg=bg_color,
                                font= ("Arial",22),
                                text="WinRAR Executable File (must end winrar.exe):")
    exe_folder_label.pack(pady=20)

    exe_folder_entry = tk.Entry(settings_window ,justify="center",width=45,font=("Arial",22))
    exe_folder_entry.pack(padx=10,pady=20,ipady=10)
    exe_folder_entry.insert(0, exe_folder)

    exe_folder_browse_button = tk.Button(settings_window,
                                        font=("Arial",20),
                                        width=10,
                                        text="Browse",
                                        command=browse_exe_folder)
    exe_folder_browse_button.pack(pady=20)
    # ask if the user wanna delete the src map file after extract
    delete_after_extract_var = tk.BooleanVar()
    delete_after_extract_var.set(delete_after_extract)
    delete_after_extract_checkbox = ctk.CTkCheckBox(settings_window,
                                                    width=20,
                                                    height=10,
                                                    font=("Arial",15),
                                                    text="Delete map source file after extracting",
                                                    variable=delete_after_extract_var)
    delete_after_extract_checkbox.pack(pady=20)

    def save_and_close():
        global delete_after_extract
        delete_after_extract = delete_after_extract_var.get()
        save_settings()
        settings_window.destroy()

    tk.Button(settings_window,font=("Arial",20),width=10, text="Save", command=save_and_close).pack(pady=30)

# cstrike folder path validation
def browse_game_folder():
    global game_folder
    folder = filedialog.askdirectory(title="Select Game Folder")
    if os.path.exists(folder) and os.path.isdir(folder):
        game_folder_entry.delete(0, tk.END)
        game_folder_entry.insert(0, folder)
        game_folder = folder
        save_settings()
    else:
        messagebox.showerror("Error",
            f"this file '{folder}' doesn't exist in this path & directory, or the given path is not a directory")
# Winrar excutable path validation
def browse_exe_folder():
    global exe_folder
    folder = filedialog.askopenfilename(title="Select WinRAR Executable file (.exe)")
    if os.path.exists(folder) and os.path.isfile(folder):
        if os.access(folder, os.X_OK):
            exe_folder_entry.delete(0, tk.END)
            exe_folder_entry.insert(0, folder)
            exe_folder = folder
            save_settings()
        else:
            messagebox.showerror("Error",
            "file has no execute permissions, you'll need to update the permissions or use a different executable.")
    else:
        messagebox.showerror("Error",f"this file '{folder}' doesn't exist in this path & directory")
# call the save & load .json file (settings)
load_settings()

# put a source map file (.zip/.rar/.7z) to extract ,this case when u get the map source file apart from download function in the gui.
def browse_file():
    # get the src file
    s_file = filedialog.askopenfilenames(title="Select Map File/Files (Must end zip/rar/7z)")
    if s_file:
        file_entry.delete(0, tk.END)
        if isinstance(s_file, tuple):  # multiple files selected case
            full_file_paths = [os.path.abspath(f) for f in s_file]
            file_entry.insert(0, ', '.join(full_file_paths))
            for full_file_path in full_file_paths:
                map_name, file_extension = os.path.splitext(os.path.basename(full_file_path))
                if file_extension in [".zip",".rar",".7z"]:
                    extract_map(full_file_path)  # Pass the full path to extract_map
                else:
                    messagebox.showerror("Error","the file must be archive (zip/rar/7z)")
        else:  # single file selected
            full_file_path = os.path.abspath(s_file)
            file_entry.insert(0, full_file_path)
            map_name, file_extension = os.path.splitext(os.path.basename(full_file_path))
            if file_extension in [".zip",".rar",".7z"]:
                extract_map(full_file_path)  # Pass the full path to extract_map
            else:
                messagebox.showerror("Error","the file must be archive (zip/rar/7z)")
    else:
        messagebox.showinfo("No files selected", "No files selected for extraction.")

# switch between pages & buttons bar
def switch(indicator,page):
    """switch between pages and trigger them"""
    for child in options_frame.winfo_children():
        if isinstance(child,tk.Label):
            child["bg"] = "white"

    indicator["bg"]= fg_color
    for frame in main_frame.winfo_children():
        frame.destroy()
        root.update()
    page()

def search_maps():
    global current_page
    current_page = 1
    fetch_maps()
# show maps on the list box
def fetch_maps():
    s = search_entry.get()
    url = f"https://gamebanana.com/apiv11/Util/Search/Results?_sSearchString={s}&_nPage={current_page}&_nPerpage={results_per_page}&_sModelName=Mod&_sOrder=best_match&_csvFields=name,description,article,attribs,studio,owner,credits&_idGameRow=4254"
    # we handle the internet connection access
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # api related stuff
            results = response.json().get("_aRecords", [])
            if results:
                listbox.delete(0, tk.END)
                for record in results:
                    map_name = record.get("_sName", "No Name")
                    root_category = record.get("_aRootCategory", {}).get("_sName", "")
                    # we only list the maps
                    if root_category == "Maps":
                        listbox.insert(tk.END, map_name)
            else:
                messagebox.showinfo("No Results", "No maps found for your search.")
        else:
            messagebox.showerror("Error", "Failed to retrieve search results.")
    except:
        messagebox.showerror("Error","Connection error, check ur internet access")
# download maps logic
def download_map():
    selected = listbox.curselection()
    if selected:
        map_name = listbox.get(selected[0])
        s = search_entry.get()
        url = f"https://gamebanana.com/apiv11/Util/Search/Results?_sSearchString={s}&_nPage={current_page}&_nPerpage={results_per_page}&_sModelName=Mod&_sOrder=best_match&_csvFields=name,description,article,attribs,studio,owner,credits&_idGameRow=4254"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                results = response.json().get("_aRecords", [])
                idd = None
                for record in results:
                    # get the id for the next api of the map we need to download (api related stuff)
                    if record.get("_sName", "No Name") == map_name:
                        idd = record["_idRow"]
                        break
                if idd:
                    url2 = f"https://gamebanana.com/apiv11/Mod/{idd}?_csvProperties=_aFiles"
                    try:
                        response2 = requests.get(url2)
                        if response2.status_code == 200:
                            # api related stuff to get the src map name
                            file_info = response2.json()['_aFiles'][0]
                            file_name = file_info['_sFile'] # src map name
                            file_extension = file_name.split('.')[-1]  # get the src file extension
                            download_url = file_info['_sDownloadUrl']
                            full_file_path = f'{map_name}.{file_extension}'
                            # check if the src map file already downloaded
                            if os.path.exists(full_file_path):
                                messagebox.showinfo("Info", "File already downloaded.")
                                if messagebox.askyesno("Extract File", f"Do you want to extract the {full_file_path} file?"):
                                    extract_map(full_file_path)
                                    return
                            try:
                                response = requests.get(download_url, stream=True)
                                if response.status_code == 200:
                                    # download progress bar
                                    progress_window = ctk.CTkToplevel(root)
                                    # fix progress window on top of the main window
                                    progress_window.transient(root)
                                    progress_window.title("Downloading")
                                    # make the window un resizable
                                    progress_window.resizable(False , False)
                                    # bind to close the download window & force end to download proccess
                                    progress_window.bind("<Escape>", lambda event : progress_window.destroy())
                                    progress_label = tk.Label(progress_window,
                                                            width=40,
                                                            height=2,
                                                            anchor="center",
                                                            bg=fg_color,
                                                            fg=bg_color,
                                                            font= ("Arial",22),
                                                            text="Downloading file, please wait...")
                                    progress_label.pack()
                                    progress_bar = ttk.Progressbar(progress_window,
                                                                orient="horizontal",
                                                                length=500,
                                                                mode="determinate")
                                    progress_bar.pack(pady=10,ipady=15)
                                    total_length = int(response.headers.get('content-length'))
                                    downloaded = 0
                                    # download the map
                                    with open(full_file_path, 'wb') as f:
                                        for chunk in response.iter_content(1024):
                                            if chunk:
                                                f.write(chunk)
                                                downloaded += len(chunk)
                                                progress_bar['value'] = (downloaded / total_length) * 100
                                                progress_label.config(text=f"{full_file_path} | {downloaded / total_length * 100:.2f}%")
                                                progress_window.update()
                                    progress_window.destroy()
                                    messagebox.showinfo("Success", "File downloaded successfully.")
                                    #check for the requierments paths & winrar
                                    if game_folder and exe_folder:
                                        if messagebox.askyesno("Extract File", f"Do you want to extract the {full_file_path} file?"):
                                            extract_map(full_file_path)
                                    else:
                                        messagebox.showerror("Error","Please select the game folder and WinRAR executable folder.")
                                else:
                                    raise Exception("Failed to download file.")
                            except Exception as e:
                                messagebox.showerror("Error", f"Failed to download file: {e}")
                        else:
                            messagebox.showerror("Error", "Failed to retrieve download URL.")
                    except:
                        messagebox.showerror("Error", "Connection error, check ur internet access")
                else:
                    messagebox.showerror("Error", "Map ID not found.")
            else:
                messagebox.showerror("Error", "Failed to retrieve search results.")
        except:
            messagebox.showerror("Error", "Connection error, check ur internet access")
    else:
        messagebox.showwarning("No Selection", "Please select a map to download.")

# extract map logic
def extract_map(full_file_path):
    # initilize a variable that help in logic cases & conditions to extract the map in cstrike according to map creators pathes
    map_dir = ""
    if game_folder and exe_folder:
        map_name, file_extension = os.path.splitext(os.path.basename(full_file_path))
        # Create a temporary directory to extract files to
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        # extract the downloded file and put them in temp folder
        try:
            subprocess.run([exe_folder, 'x', full_file_path, temp_dir])
        except Exception as e:
            messagebox.showerror("Error", f"{e}")
            # delete the temp folder in case the map does not extracted
            shutil.rmtree(temp_dir)
            return
        # Move extracted files to the game folder
        try:
            for base, dirs, files in os.walk(temp_dir):
                for dir in dirs:
                    dir_path = os.path.join(base, dir)
                    rel_path = os.path.relpath(dir_path, temp_dir)
                    top_level_dir = rel_path.split(os.sep)[0]
                    if top_level_dir not in exepted_dirs:
                        map_dir= rel_path.split(os.sep)[0]
                    # print(f"map dir > {map_dir} its type > {print(type(map_dir))}")

                for file in files:
                    # print(f"file : {file}")
                    file_path = os.path.join(base, file)
                    rel_path = os.path.relpath(file_path, temp_dir)
                    # print(f"file_path : {file_path}")
                    # print(f"rel_path : {rel_path}")
                    # print(f"map_dir : {map_dir}")

                    # first case when the mapper put his map files inside two dirs (the map name and cstrike dirs)
                    if "cstrike" in rel_path.split(os.sep)[:2] and map_dir in rel_path.split(os.sep)[:2] :
                        # print("ok both dirs exist")
                        # so we don't move these two dirs (most likely there is other dirs that exist in cstrike game folder)
                        dest_file = os.path.join(game_folder, *rel_path.split(os.sep)[2:])
                        dest_dir = os.path.dirname(dest_file)
                        # print(f"dest_file : {dest_file}")
                        # print(f"dest_dir : {dest_dir}")
                        os.makedirs(dest_dir, exist_ok=True)
                    # the case when the mapper put his map files without any requiered dirs (like (maps , sound ,etc..)) but he mostlikely put a one top level dir (either cstrike or map name)only
                    elif file_path.split(os.sep)[-2]== "temp" or file_path.split(os.sep)[-2]== map_dir or file_path.split(os.sep)[-2]== "cstrike":
                        # print(file_path.split(os.sep)[-2])
                        # we check for all possiable files extension to put them in the correct game dir
                        if file.endswith('.bsp') or file.endswith('.res') or file.endswith('.nav') or file.endswith(f'{map_dir}.text'):
                            # print("there is a bsp file")
                            # Move the .bsp (or whatever should) files to the maps directory
                            dest_dir = os.path.join(game_folder, 'maps')
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                        if os.path.splitext(file)[1] == ".tga":
                            # print("there is a tga file")
                            dest_dir = os.path.join(game_folder, "gfx" , "env")
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                        if os.path.splitext(file)[1] == ".mdl":
                            # print("there is a mdl file")
                            dest_dir = os.path.join(game_folder, "models" )
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                        if os.path.splitext(file)[1] == ".wav":
                            # print("there is a wav file")
                            dest_dir = os.path.join(game_folder, "sound" )
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                        if os.path.splitext(file)[1] == ".spr":
                            # print("there is a spr file")
                            dest_dir = os.path.join(game_folder, "sprites" )
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                        if os.path.splitext(file)[1] == ".wad" or os.path.splitext(file)[1] == ".text":
                            # print("there is a wad/text file")
                            dest_dir = os.path.join(game_folder)
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                        if os.path.splitext(file)[1] == ".jpg" or os.path.splitext(file)[1] == ".png" or os.path.splitext(file)[1] == ".bmp" or os.path.splitext(file)[1] == ".jpeg":
                            # print("there is a overview related file")
                            dest_dir = os.path.join(game_folder, "overviews")
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)

                    # case where the mapper put the map files inside one dir (either map name or cstrike dir) with requiered dirs (maps,sound,models,etc..)
                    elif "cstrike" in rel_path.split(os.sep)[:2] or map_dir in rel_path.split(os.sep)[:2] :
                        # print("ok eather cstrike or map name dir exist")
                        # we exclude this dir from moving to game folder
                        dest_file = os.path.join(game_folder, *rel_path.split(os.sep)[1:])
                        dest_dir = os.path.dirname(dest_file)
                        os.makedirs(dest_dir, exist_ok=True)
                    # mostlikely the case without any dirs ,while there is the requiered dirs(maps,models,etc...)
                    else:
                        # print("its the case with no dirs")
                        dest_file = os.path.join(game_folder, rel_path)
                        dest_dir = os.path.dirname(dest_file)
                        # print(f"2dest_file second : {dest_file}")
                        # print(f"2dest_dir second: {dest_dir}")
                        os.makedirs(dest_dir, exist_ok=True)
                    # move to game folder
                    try:
                        shutil.move(file_path, dest_file)
                    except PermissionError as e:
                        messagebox.showerror("Error", f"Permission denied: {e}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error moving {file_path}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"{e}")
        # Remove the temporary directory & map src file
        try:
            shutil.rmtree(temp_dir)
            if delete_after_extract:
                os.remove(full_file_path)
            messagebox.showinfo("Success", f"{map_name} extracted successfully.")
        except Exception as e:
            messagebox.showerror("Error",
            f"Error removing {temp_dir} or {full_file_path}: {e}.either temp folder doesn't exist or please delete {temp_dir} folder in file location or delete {full_file_path} manually")
    else:
        messagebox.showerror("Error", "Please select the game folder and WinRAR executable folder.")
# next button command to show the next loaded maps in listbox
def next_page():
    global current_page
    current_page += 1
    fetch_maps()
# previous button command to show the previous loaded maps in listbox
def prev_page():
    global current_page
    if current_page > 1:
        current_page -= 1
        fetch_maps()

#options frame (buttons bar)
options_frame = tk.Frame(root,bg=bg_color,background=bg_color)
options_frame.pack(padx=5)
options_frame.pack_propagate(False)
# options_frame.configure(width=350,height=35)
options_frame.configure(width=720,height=70)

download_button= tk.Button(options_frame, text="download",font=("Arial",26),bg="white",
                        bd=0,fg=fg_color,activeforeground=fg_color,
                        command=lambda:switch(indicator=download_indicator,
                                            page=download_page))
download_button.place(x=90,y=0,width=250)

download_indicator= tk.Label(options_frame,background="white",bg=fg_color)
download_indicator.place(x=120 ,y=60 ,width=185, height=5)

extract_button= tk.Button(options_frame, text="extract",font=("Arial",26),bg="white",
                        bd=0,fg=fg_color,activeforeground=fg_color,
                        command=lambda:switch(indicator=extract_indicator,
                                            page=extract_page))

extract_button.place(x=400,y=0,width=250)

extract_indicator= tk.Label(options_frame,background="white")
extract_indicator.place(x=435 ,y=60 ,width=175, height=5)

#main frame
main_frame = tk.Frame(root,bg=fg_color)
main_frame.pack(expand=True ,fill="both",pady=5,padx=5)

icon=Image.open(resource_path("assets\\settings.ico")).resize((100,100))
setting_icon = ImageTk.PhotoImage(icon)

setting_button = tk.Button(
    root,
    image=setting_icon,
    width=50,
    height=50,
    bg=fg_color,
    activebackground=afg_color,
    bd=0,
    highlightthickness=0,
    command=lambda: settings_page()
    )
setting_button.place(relx=0.9,rely=0.09)
setting_button.lift()

# landing & download page
def download_page():
    global search_entry, listbox
    download_frame =tk.Frame(main_frame,bg=fg_color)
    download_frame.pack(expand=True ,fill="both")

    tk.Label(download_frame,
            width=50,
            height=1,
            anchor="s",
            bg=fg_color,
            fg="black",
            text="Search for map:",
            font=("Arial",22)
            ).pack(pady=25)
    search_entry = tk.Entry(download_frame,justify="center",width=30,font=("Arial",22))
    search_entry.pack(pady=15,ipadx=10,ipady=10)

    search_button = tk.Button(download_frame,
                            width=10,
                            text="Search",
                            font=("Arial",20),
                            activeforeground=afg_color,
                            command=search_maps)
    search_button.pack(pady=20)

    listbox = tk.Listbox(download_frame, width=35, height=15,justify="center",font=("Arial",24))
    listbox.pack(pady=20)

    download_button = tk.Button(download_frame,
                                font=("Arial",20),
                                width=10, text="Download",
                                activeforeground=afg_color,
                                command=download_map)
    download_button.pack(pady=30)

    pagination_frame = tk.Frame(download_frame,bg=fg_color)
    pagination_frame.pack(pady=20)

    prev_button = tk.Button(pagination_frame,
                            font=("Arial",20),
                            width=10,
                            text="Previous",
                            activeforeground=afg_color,
                            command=prev_page)
    prev_button.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(pagination_frame,
                            font=("Arial",20),
                            width=10, text="  Next  ",
                            activeforeground=afg_color,
                            command=next_page)
    next_button.pack(side=tk.RIGHT, padx=10)
# extract page
def extract_page():
    global file_entry
    extract_frame =tk.Frame(main_frame,bg=fg_color)
    extract_frame.pack(expand=True ,fill="both")

    file_label = tk.Label(extract_frame,
                        width=50,
                        height=3,
                        anchor="s",
                        bg=fg_color,
                        fg="black",
                        font= ("Arial",22),
                        text="Extract source map to game folder\nSelect Map/Maps Source files (Must end zip/rar/7z):")
    file_label.pack(pady=70)
    file_entry = tk.Entry(extract_frame,justify="center",width=40,font=("Arial",22))
    file_entry.pack(pady=15,ipadx=10,ipady=10,padx=10)
    file_browse_button = tk.Button(extract_frame,
                                font=("Arial",20),
                                width=10,
                                text="Browse",
                                activeforeground=afg_color,
                                command=browse_file)
    file_browse_button.pack(pady=15)

    indicator= tk.Label(extract_frame,background="white")
    indicator.place(x=140,y=550 ,width=600, height=5)

    info_label = tk.Label(
        extract_frame,
        text="Counter-Strike 1.6 map installer v1.4.1\nfor info read 'map_installer_get_started.txt'",
        font=("Arial",24),fg='black',bg=fg_color)
    info_label.place(relx=0.16,rely=0.60)

    abd_label = tk.Label(
        extract_frame,
        text="by ao | aka Batooka",
        font=("Arial",16),fg='black',bg=fg_color)
    abd_label.place(relx=0.76,rely=0.963)

if __name__ == "__main__":
    download_page()
    root.mainloop()
