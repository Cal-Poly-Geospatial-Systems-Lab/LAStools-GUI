# Gabriel J. Young
# Feb 2025
# gjyoung@calpoly.edu

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import subprocess
import os
import sys
import math
from pathlib import Path

# Static global constants
WINDOW_TITLE = "Simple LasTools GUI"
WINDOW_SIZE = "1600x900"  # Increased size to fit new elements
LASTOOLS_PATH = "C:\\lastools"

# Layout settings
TITLE_PADY = (10, 10)
TITLE_PADX = (10, 10)
H1_PADY = (8, 8)
H1_PADX = (8, 8)

VIEW_BTN_PADX = (0, 5)

# Title settings
TITLE_FONT = ("Arial", 14, "bold")
H1_FONT = ("Arial", 14)
H2_FONT = ("Arial", 12)
H2_PADX = (5, 5)

# Textbox settings
TEXTBOX_HEIGHT = 20
INFOBOX_HEIGHT = 20

MIN_COL_0_W = 700

DEF_GRD_STEP = "5"
DEF_DEM_STEP = "0.5"
DEF_DEM_AZIMUTH = 270
DEF_DEM_ALTITUDE = 45
DEF_DEM_R_FACTOR = 1
DEF_GRD_OP_PARAMS_DEC_ENTRY = ["stddev", "offset", "bulge", "spike", "sub"]


### math ultilty
def sph2cart(azimuth,elevation,r):
    x = r * math.cos(math.radians(elevation)) * math.cos(math.radians(azimuth))
    y = r * math.cos(math.radians(elevation)) * math.sin(math.radians(azimuth))
    z = r * math.sin(math.radians(elevation))
    return x, y, z


class CommandWrapperApp():
    def __init__(self, root, lastools_path):
        self.root = root
        self.lastools_path = lastools_path
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        # Create a container frame
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        #canvas
        self.base_canvas = tk.Canvas(self.root)
        self.base_canvas.grid(row=0, column=0, sticky=tk.NSEW)

        #scrollbar
        self.base_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.base_canvas.yview)
        self.base_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        #configure canvas
        self.base_canvas.configure(yscrollcommand=self.base_scrollbar.set)

        self.base_frame = ttk.Frame(self.base_canvas)
        self.base_window = self.base_canvas.create_window((0, 0), window=self.base_frame, anchor=tk.NW)
        # Update the scroll region
        self.base_frame.bind("<Configure>", self.on_canvas_configure)

        # Create UI components
        ttk.Label(self.base_frame, text=WINDOW_TITLE, font=TITLE_FONT).grid(row=0, column=0, padx=10, pady=10)

        self.create_widgets(self.base_frame)

        # Expand frame width as canvas resizes
        self.base_frame.bind("<Configure>", self.on_frame_configure)

    def on_frame_configure(self, event):
        self.base_canvas.configure(scrollregion=self.base_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Ensure the inner frame matches the width of the canvas."""
        self.base_canvas.itemconfig(self.base_window, width=event.width)

    ### File I/O utility functions

    def select_file(self, input_file: ttk.Entry, filetypes_list):
        """
        selects file and updates ttk Entry <input_file>
        :param input_file: ttk Entry
        """
        file_path = filedialog.askopenfilename(filetypes=filetypes_list)
        if file_path:
            input_file.config(state=tk.NORMAL)
            input_file.delete(0, tk.END)
            input_file.insert(0, file_path)
            input_file.config(state=tk.DISABLED)


    def select_folder(self, folder: ttk.Entry):
        """
        selects folder and updates ttk Entry <input_file>
        :param folder: ttk Entry
        """
        file_path = filedialog.askdirectory()
        if file_path:
            folder.config(state=tk.NORMAL)
            folder.delete(0, tk.END)
            folder.insert(0, file_path)
            folder.config(state=tk.DISABLED)


    def create_info_button(self, frame: ttk.Frame, file : str):
        """
        return: ttk Button
        """
        return ttk.Button(
            frame,
            text="Doc. View",
            command=lambda: self.update_info_box(
                resource_path(f"data/{file}.txt")
            ),
        )


    ### Run LASTools Commands

    def run_las_view(self, file_path: str):
        if os.path.exists(file_path):
            self.update_output(f"lasview: {file_path}")
            command = self.lastools_path + "\\"
            command += f"lasview64.exe {file_path}"
            self.update_output(command)
            returncode = self.check_output(command)

            ### check return code
            if returncode != 0:
                print("Error. lasview failed.")
                sys.exit(1)
        else:
            self.update_output(f"Invalid input: {file_path}\n")

    def run_las_ground(self, input_path: str, output_path: str, las_args: str):
        #check input and output paths 
        if input_path:
            self.update_output(f"lasground: {input_path}")
            command = self.lastools_path + "\\"
            command += f"lasground64.exe -v -i {input_path} -o {output_path} {las_args}"
            self.update_output(command)
            print(command)
            returncode = self.check_output(command)

            ### check return code
            if returncode != 0:
                print("Error. lasground failed.")
                sys.exit(1)
        else:
            self.update_output(f"Invalid input: {input_path}\n")

    def run_blast2dem(self, input_path: str, output_path: str, las_args: str):
        if input_path:
            self.update_output(f"lasview: {input_path}")
            command = self.lastools_path + "\\"
            command += f"blast2dem64.exe -v -keep_class 2 -i {input_path} -o {output_path} {las_args}"
            self.update_output(command)
            print(command)
            returncode = self.check_output(command)

            ### check return code
            if returncode != 0:
                print("Error. lasground failed.")
                sys.exit(1)
        else:
            self.update_output(f"Invalid input: {input_path}\n")

    def run_hillshade(self, input_path: str, output_path: str, las_args: str):
        if input_path:
            x, y, z = sph2cart(float(self.dem_azimuth.get()), float(self.dem_altitude.get()), float(self.dem_r_factor.get()))
            self.update_output(f"lasview: {input_path}")
            command = self.lastools_path + "\\"
            command += f"blast2dem64.exe -v -hillshade -opng -i -light {round(x, 3)} {round(y, 3)} {round(z, 3)} \
            {input_path} -o {output_path}"
            self.update_output(command)
            print(command)
            returncode = self.check_output(command)

            ### check return code
            if returncode != 0:
                print("Error. lasground failed.")
                sys.exit(1)
        else:
            self.update_output(f"Invalid input: {input_path}\n")

    def check_output(self, command):
        """Handles the execution of a command and returns the output."""
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        while True:
            out = process.stdout.read(1)
            returncode = process.poll()
            if out == b"" and returncode is not None:
                break
            else:
                self.update_output(out.decode("utf-8"))
        returncode = process.poll()
        return returncode

    ### LASTools command builder utility functions

    def decimal_validation(self, P):
        if P == "":  # Allow empty input (for backspacing)
            return True
        try:
            float(P)  # Try converting the input to a float
            return True
        except ValueError:
            return False

    def set_args(self, toggle_args_dict):
        """
        :param input_file: toggle_args_dict dict of arguments, each argument is a dict of {"is_enabled"<bool>, "entry"<string>}
        :returns arg list of <str>
        """
        ret_args = ""
        for arg in toggle_args_dict:
            if toggle_args_dict.get(arg).get("is_enabled").get():
                ret_args += " -" + str(arg)
                sub_arg = toggle_args_dict.get(arg).get("entry")
                if sub_arg:  # handle args without subargs
                    ret_args += " " + str(sub_arg.get())
        return ret_args
    

    ### Second-level frames

    def create_grd_input_frame(self, parent_frame):
        # Frame for input selector and button
        input_frame = ttk.Frame(parent_frame)
        ttk.Label(input_frame, text="Select File:").pack(side=tk.LEFT, padx=H2_PADX)
        # File entry field
        self.grd_input_path = ttk.Entry(input_frame, state=tk.DISABLED)
        self.grd_input_path.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)
        # Browse button
        browse_button = ttk.Button(
            input_frame,
            text="...",
            command=lambda: [
                self.select_file(self.grd_input_path, [("las files", "*.las")]),
                self.update_grd_out_file(os.path.basename(self.grd_input_path.get())),
                self.update_grd_out_folder(os.path.dirname(self.grd_input_path.get())),
            ],
        )
        browse_button.pack(side=tk.LEFT)
        # Run command button
        view_button = ttk.Button(
            input_frame,
            text="View",
            command=lambda: self.run_las_view(self.grd_input_path.get()),
        )
        view_button.pack(side=tk.RIGHT)

        return input_frame

    def create_processing_frame(self, parent_frame):
        processing_frame = ttk.Frame(parent_frame)
        processing_frame_row = 0

        processing_frame.columnconfigure(processing_frame_row, minsize=MIN_COL_0_W)

        self.create_ground_command_frame(processing_frame).grid(
            row=0, column=0, pady=2, sticky=tk.W
        )

        self.create_dem_command_frame(processing_frame).grid(
            row=1, column=0, pady=2, sticky=tk.W
        )

        return processing_frame

    def create_ground_command_frame(self, parent_frame):
        # Dictionary to store frames, variables, and entry values
        grd_params_dict = {}

        # grd frame
        grd_command_frame = ttk.Frame(parent_frame)
        grd_command_frame_row = 0
        grd_command_frame.columnconfigure(grd_command_frame_row, minsize=MIN_COL_0_W)

        # grd label
        ground_lb_frame = ttk.Frame(grd_command_frame)
        ground_lb = ttk.Label(ground_lb_frame, text="Lasground", font=H2_FONT)
        ground_lb.pack(side=tk.LEFT, padx=H1_PADX, pady=H1_PADY)

        # Info button
        self.create_info_button(ground_lb_frame, "grd_lasground").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        ground_lb_frame.grid(row=grd_command_frame_row, column=0, pady=2, sticky=tk.W)
        grd_command_frame_row += 1

        # out file
        grd_out_file_selector = ttk.Frame(grd_command_frame)
        ttk.Label(grd_out_file_selector, text="Output File:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        self.grd_out_file = ttk.Entry(grd_out_file_selector)
        self.grd_out_file.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)

        grd_out_file_selector.grid(
            row=grd_command_frame_row, column=0, pady=2, sticky=tk.EW
        )
        grd_command_frame_row += 1

        # out folder
        grd_out_folder_frame = ttk.Frame(grd_command_frame)
        ttk.Label(grd_out_folder_frame, text="Output Folder:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        # File entry field
        self.grd_out_folder = ttk.Entry(grd_out_folder_frame, state=tk.DISABLED)
        self.grd_out_folder.insert(0, f"{os.path.basename(self.grd_input_path.get())}")
        self.grd_out_folder.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX
        )
        # Browse button
        browse_button = ttk.Button(
            grd_out_folder_frame,
            text="...",
            command=lambda: self.select_folder(self.grd_out_folder),
        )
        browse_button.pack(side=tk.LEFT)

        grd_out_folder_frame.grid(row=grd_command_frame_row, column=0, pady=2, sticky=tk.EW)
        grd_command_frame_row += 1

        # step parameter
        sub_frame = ttk.Frame(grd_command_frame)
        ttk.Label(sub_frame, text="Step:").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = sub_frame.register(self.decimal_validation)
        # Info button
        self.create_info_button(sub_frame, "grd_step").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        self.grd_step = ttk.Entry(
            sub_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.grd_step.insert(0, DEF_GRD_STEP)
        self.grd_step.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

        sub_frame.grid(row=grd_command_frame_row, column=0, pady=2, stick=tk.W)
        grd_command_frame_row += 1

        tk_bool_true = tk.BooleanVar()
        tk_bool_true.set(True)
        grd_params_dict["step"] = {
            "is_enabled": tk_bool_true,
            "entry": self.grd_step,
        }


        # compute height parameter
        grd_compute_h_frame = ttk.Frame(grd_command_frame)
        ttk.Label(grd_compute_h_frame, text="Compute Height:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        self.compute_height = tk.BooleanVar()

        ttk.Checkbutton(grd_compute_h_frame, variable=self.compute_height).pack(
            side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX
        )

        grd_params_dict["compute_height"] = {
            "is_enabled": self.compute_height,
            "entry": None,
        }

        # Info button
        self.create_info_button(grd_compute_h_frame, "grd_compute_height").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        grd_compute_h_frame.grid(
            row=grd_command_frame_row, column=0, pady=2, stick=tk.W
        )
        grd_command_frame_row += 1

        def toggle_Entry(var: tk.IntVar, entry: tk.Entry):
            if var.get() == True:
                entry.config(state=tk.NORMAL)
            else:
                entry.config(state=tk.DISABLED)

        # optional params with entry fields
        toggle_param_list = DEF_GRD_OP_PARAMS_DEC_ENTRY

        for param in toggle_param_list:
            frame = ttk.Frame(grd_command_frame)
            var = tk.BooleanVar()

            #create the entry first so it can be referenced by the checkbox
            v_dec_cmd = frame.register(self.decimal_validation)
            entry = ttk.Entry(frame, validate="all", validatecommand=(v_dec_cmd, "%P"))
            entry.insert(0, 0)
            entry.config(state=tk.DISABLED)

            # Store in dictionary
            grd_params_dict[param] = {"is_enabled": var, "entry": entry}

            ttk.Checkbutton(
                frame,
                text=f"Enable {param.capitalize()}",
                variable=var,
                command=lambda v=var, e=grd_params_dict[param].get("entry"): (
                   toggle_Entry(v, e)
                ),
            ).pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

            ttk.Label(frame, text=f"{param.capitalize()}:").pack(
                side=tk.LEFT, padx=VIEW_BTN_PADX
            )
            #pack the entry here so it goes in the right place
            entry.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

            # Info button
            self.create_info_button(frame, f"grd_{param}").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

            # Pack frame into parent processing frame
            frame.grid(row=grd_command_frame_row, column=0, pady=2, stick=tk.W)
            grd_command_frame_row += 1

        # Run command button update dem inputs on run
        ttk.Button(
            grd_command_frame,
            text="Run",
            command=lambda: [
                self.run_las_ground(self.grd_input_path.get(),
                    os.path.join(self.grd_out_folder.get(), self.grd_out_file.get()),
                    self.set_args(grd_params_dict)),
                self.update_dem_in_path(os.path.join(self.grd_out_folder.get(), self.grd_out_file.get())),
                self.update_dem_ele_file(os.path.basename(self.grd_input_path.get())),
                self.update_dem_hill_file(os.path.basename(self.grd_input_path.get())),
                self.update_dem_out_folder(os.path.dirname(self.grd_input_path.get())),
            ],
        ).grid(row=grd_command_frame_row, column=1, pady=2)

        #view button
        ttk.Button(
            grd_command_frame,
            text="View",
            command=lambda: self.run_las_view(
                os.path.join(self.grd_out_folder.get(), self.grd_out_file.get())
            ),
        ).grid(row=grd_command_frame_row, column=2, pady=2)

        return grd_command_frame
    
    def create_dem_input_frame(self, parent_frame):
        # Frame for input selector and button
        input_frame = ttk.Frame(parent_frame)
        ttk.Label(input_frame, text="Select File:").pack(side=tk.LEFT, padx=H2_PADX)
        # File entry field
        self.dem_input_path = ttk.Entry(input_frame, state=tk.DISABLED)
        self.dem_input_path.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)
        # Browse button
        browse_button = ttk.Button(
            input_frame,
            text="...",
            command=lambda: [
                self.select_file(self.dem_input_path, [("las files", "*.las")]),
                self.update_dem_ele_file(os.path.basename(self.dem_input_path.get())),
                self.update_dem_hill_file(os.path.basename(self.dem_input_path.get())),
                self.update_dem_out_folder(os.path.dirname(self.dem_input_path.get())),
            ],
        )
        browse_button.pack(side=tk.LEFT)
        # Run command button
        view_button = ttk.Button(
            input_frame,
            text="View",
            command=lambda: self.run_las_view(self.dem_input_path.get()),
        )
        view_button.pack(side=tk.RIGHT)

        return input_frame   

    def create_dem_command_frame(self, parent_frame):
        # Dictionary to store frames, variables, and entry values
        dem_params_dict = {}
        #dem frame
        dem_command_frame = ttk.Frame(parent_frame)
        dem_command_frame_row = 0
        dem_command_frame.columnconfigure(dem_command_frame_row, minsize=MIN_COL_0_W)

        #dem label
        dem_lb_frame = ttk.Frame(dem_command_frame)
        dem_lb = ttk.Label(dem_lb_frame, text="Compute DEM", font=H2_FONT)
        dem_lb.pack(side=tk.LEFT, padx=H1_PADX, pady=H1_PADY)

        # Info button
        self.create_info_button(dem_lb_frame, "dem_blast2dem").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        dem_lb_frame.grid(row=dem_command_frame_row, column=0, pady=2, sticky=tk.W)
        dem_command_frame_row += 1

        #Input Path
        ttk.Label(dem_command_frame, text="Input Selection", font=H2_FONT).grid(
            row=dem_command_frame_row, column=0, pady=2, sticky=tk.W)
        dem_command_frame_row+=1

        self.create_dem_input_frame(dem_command_frame).grid(
            row=dem_command_frame_row, column=0, pady=2, sticky=tk.EW)
        dem_command_frame_row+=1

        # Out file elevation
        dem_ele_file_selector = ttk.Frame(dem_command_frame)
        ttk.Label(dem_ele_file_selector, text="Output Elevation File:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        self.dem_ele_file = ttk.Entry(dem_ele_file_selector)
        self.dem_ele_file.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)

        dem_ele_file_selector.grid(
            row=dem_command_frame_row, column=0, pady=2, sticky=tk.EW
        )
        dem_command_frame_row += 1

        # Out file hillshade
        dem_hill_file_selector = ttk.Frame(dem_command_frame)
        ttk.Label(dem_hill_file_selector, text="Output Hillshade File:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        self.dem_hill_file = ttk.Entry(dem_hill_file_selector)
        self.dem_hill_file.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)

        dem_hill_file_selector.grid(
            row=dem_command_frame_row, column=0, pady=2, sticky=tk.EW
        )
        dem_command_frame_row += 1

        # out folder
        dem_out_folder_frame = ttk.Frame(dem_command_frame)
        ttk.Label(dem_out_folder_frame, text="Output Folder:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        # File entry field
        self.dem_out_folder = ttk.Entry(dem_out_folder_frame, state=tk.DISABLED)
        self.dem_out_folder.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX
        )
        # Browse button
        browse_button = ttk.Button(
            dem_out_folder_frame,
            text="...",
            command=lambda: self.select_folder(self.grd_out_folder),
        )
        browse_button.pack(side=tk.LEFT)

        dem_out_folder_frame.grid(row=dem_command_frame_row, column=0, pady=2, sticky=tk.EW)
        dem_command_frame_row += 1

        #Resolution Parameter
        dem_step_frame = ttk.Frame(dem_command_frame)
        ttk.Label(dem_step_frame, text="Step (Resolution):").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = dem_step_frame.register(self.decimal_validation)
        # Info button
        self.create_info_button(dem_step_frame, "dem_step").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        #step param
        self.dem_step = ttk.Entry(
            dem_step_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.dem_step.insert(0, DEF_DEM_STEP)
        self.dem_step.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)
        dem_step_frame.grid(row=dem_command_frame_row, column=0, pady=2, stick=tk.W)
        dem_command_frame_row += 1
        dem_step_enabled = tk.BooleanVar()
        dem_step_enabled.set(True)
        dem_params_dict["step"] = {
            "is_enabled": dem_step_enabled,
            "entry": self.dem_step,
        }
        
        #Hillshade Option
        ttk.Label(dem_command_frame, text="Hillshading", font=H2_FONT).grid(
            row=dem_command_frame_row, column=0, pady=2, sticky=tk.W)
        dem_command_frame_row+=1

        #Azimuth suboption
        sub_frame = ttk.Frame(dem_command_frame)
        ttk.Label(sub_frame, text="Azimuth (degree):").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = sub_frame.register(self.decimal_validation)
        # Info button
        self.create_info_button(sub_frame, "dem_azimuth").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        self.dem_azimuth = ttk.Entry(
            sub_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.dem_azimuth.insert(0, DEF_DEM_AZIMUTH)
        self.dem_azimuth.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

        sub_frame.grid(row=dem_command_frame_row, column=0, pady=2, stick=tk.W)
        dem_command_frame_row += 1

        #Altitude suboption
        sub_frame = ttk.Frame(dem_command_frame)
        ttk.Label(sub_frame, text="Altitude (degree):").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = sub_frame.register(self.decimal_validation)
        # Info button
        self.create_info_button(sub_frame, "dem_altitude").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        self.dem_altitude = ttk.Entry(
            sub_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.dem_altitude.insert(0, DEF_DEM_ALTITUDE)
        self.dem_altitude.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

        sub_frame.grid(row=dem_command_frame_row, column=0, pady=2, stick=tk.W)
        dem_command_frame_row += 1

        # r-value suboption
        sub_frame = ttk.Frame(dem_command_frame)
        ttk.Label(sub_frame, text="R factor:").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = sub_frame.register(self.decimal_validation)
        # Info button
        self.create_info_button(sub_frame, "dem_r_factor").pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        self.dem_r_factor = ttk.Entry(
            sub_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.dem_r_factor.insert(0, DEF_DEM_R_FACTOR)
        self.dem_r_factor.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

        sub_frame.grid(row=dem_command_frame_row, column=0, pady=2, stick=tk.W)
        dem_command_frame_row += 1

        #Run Command Button
        ttk.Button(
            dem_command_frame,
            text="Run",
            command=lambda : [
                self.run_blast2dem(self.dem_input_path.get(),
                os.path.join(self.dem_out_folder.get(), self.dem_ele_file.get()),
                self.set_args(dem_params_dict)),
                self.run_hillshade(os.path.join(self.dem_out_folder.get(), self.dem_ele_file.get()),
                                   os.path.join(self.dem_out_folder.get(), self.dem_hill_file.get()),
                                   "")
            ]
        ).grid(row=dem_command_frame_row, column=1, pady=2)

        return dem_command_frame


    ### GRD Command Callbacks

    def update_grd_out_file(self, output_file):
        if output_file:
            self.grd_out_file.delete(0, tk.END)
            self.grd_out_file.insert(0, f"grd_{output_file}")

    def update_grd_out_folder(self, output_folder):
        if output_folder:
            self.grd_out_folder.config(state=tk.NORMAL)
            self.grd_out_folder.delete(0, tk.END)
            self.grd_out_folder.insert(0, f"{output_folder}")
            self.grd_out_folder.config(state=tk.DISABLED)

    ### DEM Command Callbacks

    def update_dem_in_path(self, input_path):
        if input_path:
            self.dem_input_path.config(state=tk.NORMAL)
            self.dem_input_path.delete(0, tk.END)
            self.dem_input_path.insert(0, f"{input_path}")
            self.dem_input_path.config(state=tk.DISABLED)

    def update_dem_ele_file(self, output_file):
        if output_file:
            self.dem_ele_file.delete(0, tk.END)
            self.dem_ele_file.insert(0, f"dem_elevation_{Path(output_file).stem}.bil")

    def update_dem_hill_file(self, output_file):
        if output_file:
            self.dem_hill_file.delete(0, tk.END)
            self.dem_hill_file.insert(0, f"dem_hillshade_{Path(output_file).stem}.png")

    def update_dem_out_folder(self, output_folder):
        if output_folder:
            self.dem_out_folder.config(state=tk.NORMAL)
            self.dem_out_folder.delete(0, tk.END)
            self.dem_out_folder.insert(0, f"{output_folder}")
            self.dem_out_folder.config(state=tk.DISABLED)

    ### Main Textboxes

    def update_output(self, message):
        """Updates the output_text widget with the given message."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message)  # Appends new message
        self.output_text.update_idletasks()
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def update_info_box(self, filename):
        """Reads a text file and updates the output_text widget with its content."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                content = file.read()

            self.infobox.config(state=tk.NORMAL)
            self.infobox.delete("1.0", tk.END)  # Clear previous content
            self.infobox.insert(tk.END, content)  # Insert new content
            self.infobox.config(state=tk.DISABLED)

        except FileNotFoundError:
            print(f"Error: {filename} not found.")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    def create_widgets(self, parent_frame: ttk.Frame):
        """Create all widgets for the UI."""

        ### widgets
        # Title label
        title_lb = ttk.Label(parent_frame, text=WINDOW_TITLE, font=TITLE_FONT)

        input_lb = ttk.Label(parent_frame, text="Input Selection", font=H1_FONT)
        input_frame = self.create_grd_input_frame(parent_frame)

        # processing frame
        processing_lb = ttk.Label(parent_frame, text="Processing", font=H1_FONT)
        processing_frame = self.create_processing_frame(parent_frame)

        # output box
        output_lb = ttk.Label(parent_frame, text="Output:", font=H1_FONT)
        self.output_text = scrolledtext.ScrolledText(
            parent_frame, wrap=tk.WORD, height=TEXTBOX_HEIGHT, state=tk.DISABLED
        )

        # output box
        infobox_lb = ttk.Label(parent_frame, text="Documentation:", font=H1_FONT)
        self.infobox = scrolledtext.ScrolledText(
            parent_frame, wrap=tk.WORD, height=INFOBOX_HEIGHT, state=tk.DISABLED
        )

        ### grid layout
        parent_frame.columnconfigure(
            0, minsize=MIN_COL_0_W
        )  # Set minimum size for column 0
        title_lb.grid(row=0, column=0, pady=2)

        ttk.Separator(parent_frame, orient="horizontal").grid(
            row=1, column=0, sticky=tk.EW, pady=2
        )
        input_lb.grid(row=2, column=0, sticky=tk.EW, pady=2, padx=TITLE_PADX)
        input_frame.grid(row=3, column=0, sticky=tk.EW, pady=2)

        ttk.Separator(parent_frame, orient="horizontal").grid(
            row=4, column=0, sticky=tk.EW, pady=2
        )
        processing_lb.grid(row=5, column=0, sticky=tk.W, pady=2, padx=TITLE_PADX)
        processing_frame.grid(row=6, column=0, sticky=tk.EW, pady=2, padx=TITLE_PADX)

        ttk.Separator(parent_frame, orient="horizontal").grid(
            row=7, column=0, sticky=tk.EW, pady=2
        )
        output_lb.grid(row=8, column=0, sticky=tk.EW, pady=2, padx=TITLE_PADX)
        self.output_text.grid(row=9, column=0, pady=2, sticky=tk.NS)

        infobox_lb.grid(row=2, column=1, pady=2, padx=TITLE_PADX)
        self.infobox.grid(row=3, column=1, rowspan=8, pady=2, padx=2, sticky=tk.NS)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_usr_input_lastools_path():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Enter LASTOOLS path e.g. ../lastools/bin/")


def main():
    """Main function to start the application."""
    lastools_path = LASTOOLS_PATH + "\\bin"
    while not os.path.exists(lastools_path):
        print(f"Cannot find .\\lastools\\bin at {lastools_path}")
        usr_input = get_usr_input_lastools_path()
        if not usr_input:
            print("No path provided")
            sys.exit(1)
        lastools_path = usr_input.strip()
   
    print(f"Found {lastools_path} ...")
    # Create Tkinter root window and pass it to the app
    root = tk.Tk()
    app = CommandWrapperApp(root, lastools_path)

    # Start the Tkinter loop
    root.mainloop()


if __name__ == "__main__":
    main()