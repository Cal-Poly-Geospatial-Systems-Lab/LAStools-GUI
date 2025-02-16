# Gabriel J. Young
# Feb 2025
# gjyoung@calpoly.edu

import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import os
import sys
from tkinter import scrolledtext

# Static global constants
WINDOW_TITLE = "Simple LasTools GUI"
WINDOW_SIZE = "1536x864"  # Increased size to fit new elements
LASTOOLS_PATH = "F:\\gjyoung\\lastools"

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
DEF_GRD_OP_PARAMS_DEC_ENTRY = ["stddev", "offset", "bulge", "spike", "sub"]


class CommandWrapperApp:
    def __init__(self, root, lastools_path):
        self.root = root
        self.lastools_path = lastools_path
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.cur_doc_name = ""

        # Create UI components
        self.create_widgets()

    ### File I/O utility functions

    def select_file(self, input_file: ttk.Entry):
        """
        selects file and updates ttk Entry <input_file>
        :param input_file: ttk Entry
        """
        file_path = filedialog.askopenfilename(filetypes=[("las files", "*.las")])
        if file_path:
            input_file.delete(0, tk.END)
            input_file.insert(0, file_path)

    def select_folder(self, folder: ttk.Entry):
        """
        selects folder and updates ttk Entry <input_file>
        :param folder: ttk Entry
        """
        file_path = filedialog.askdirectory()
        if file_path:
            folder.delete(0, tk.END)
            folder.insert(0, file_path)

    ### Run LASTools Commands

    def run_las_view(self, file_path):
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

    def run_las_ground(self, input_path, output_path, las_args):
        if input_path:
            self.update_output(f"lasview: {input_path}")
            command = self.lastools_path + "\\"
            command += f"lasground64.exe -v -i {input_path} -o {output_path} {las_args}"
            self.update_output(command)
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

    def create_input_frame(self):
        # Frame for input selector and button
        input_frame = ttk.Frame(self.root)
        ttk.Label(input_frame, text="Select File:").pack(side=tk.LEFT, padx=H2_PADX)
        # File entry field
        self.input_path = ttk.Entry(input_frame)
        self.input_path.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)
        # Browse button
        browse_button = ttk.Button(
            input_frame,
            text="...",
            command=lambda: [
                self.select_file(self.input_path),
                self.update_grd_out_file(os.path.basename(self.input_path.get())),
                self.update_grd_out_folder(os.path.dirname(self.input_path.get())),
            ],
        )
        browse_button.pack(side=tk.LEFT)
        # Run command button
        view_button = ttk.Button(
            input_frame,
            text="View",
            command=lambda: self.run_las_view(self.input_path.get()),
        )
        view_button.pack(side=tk.RIGHT)

        return input_frame

    def create_processing_frame(self):
        processing_frame = ttk.Frame(self.root)
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
        grd_prams_dict = {}

        # grd frame
        grd_command_frame = ttk.Frame(parent_frame)
        grd_command_frame_row = 0
        grd_command_frame.columnconfigure(grd_command_frame_row, minsize=MIN_COL_0_W)

        # grd label
        ground_lb_frame = ttk.Frame(grd_command_frame)
        ground_lb = ttk.Label(ground_lb_frame, text="Lasground", font=H2_FONT)
        ground_lb.pack(side=tk.LEFT, padx=H1_PADX, pady=H1_PADY)

        # Info button
        info_button = ttk.Button(
            ground_lb_frame,
            text="Doc. View",
            command=lambda: self.update_info_box(
                resource_path("data/grd_lasground.txt")
            ),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        ground_lb_frame.grid(row=grd_command_frame_row, column=0, pady=2, sticky=tk.W)
        grd_command_frame_row += 1

        # out file
        grd_out_file_selector = ttk.Frame(grd_command_frame)
        ttk.Label(grd_out_file_selector, text="Output File:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        self.grd_out_file = ttk.Entry(grd_out_file_selector)
        self.grd_out_file.insert(0, f"grd_{self.input_path.get()}")
        self.grd_out_file.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)

        grd_out_file_selector.grid(
            row=grd_command_frame_row, column=0, pady=2, sticky=tk.EW
        )
        grd_command_frame_row += 1

        # out folder
        grd_out_folder = ttk.Frame(grd_command_frame)
        ttk.Label(grd_out_folder, text="Output Folder:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        # File entry field
        self.grd_out_folder = ttk.Entry(grd_out_folder)
        self.grd_out_folder.insert(0, f"{os.path.basename(self.input_path.get())}")
        self.grd_out_folder.pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX
        )
        # Browse button
        browse_button = ttk.Button(
            grd_out_folder,
            text="...",
            command=lambda: self.select_folder(self.grd_out_folder),
        )
        browse_button.pack(side=tk.LEFT)

        grd_out_folder.grid(row=grd_command_frame_row, column=0, pady=2, sticky=tk.EW)
        grd_command_frame_row += 1

        # step parameter
        grd_step_frame = ttk.Frame(grd_command_frame)
        ttk.Label(grd_step_frame, text="Step:").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = grd_step_frame.register(self.decimal_validation)
        # Info button
        info_button = ttk.Button(
            grd_step_frame,
            text="Doc. View",
            command=lambda: self.update_info_box(resource_path("data/grd_step.txt")),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        self.grd_step = ttk.Entry(
            grd_step_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.grd_step.insert(0, DEF_GRD_STEP)
        self.grd_step.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)
        grd_step_frame.grid(row=grd_command_frame_row, column=0, pady=2, stick=tk.W)
        grd_command_frame_row += 1
        grd_step_enabled = tk.BooleanVar()
        grd_step_enabled.set(True)
        grd_prams_dict["step"] = {
            "is_enabled": grd_step_enabled,
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

        grd_prams_dict["compute_height"] = {
            "is_enabled": self.compute_height,
            "entry": None,
        }

        # Info button
        info_button = ttk.Button(
            grd_compute_h_frame,
            text="Doc. View",
            command=lambda: self.update_info_box(
                resource_path("data/grd_compute_height.txt")
            ),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
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

            ttk.Checkbutton(
                frame,
                text=f"Enable {param.capitalize()}",
                variable=var,
                command=lambda v=var, e=param: (
                    grd_prams_dict[e]["entry"].config(state=tk.NORMAL)
                    if v.get() is True
                    else grd_prams_dict[e]["entry"].config(state=tk.DISABLED)
                ),
            ).pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

            ttk.Label(frame, text=f"{param.capitalize()}:").pack(
                side=tk.LEFT, padx=VIEW_BTN_PADX
            )

            v_dec_cmd = frame.register(self.decimal_validation)
            entry = ttk.Entry(frame, validate="all", validatecommand=(v_dec_cmd, "%P"))
            entry.insert(0, 0)
            entry.config(state=tk.DISABLED)
            entry.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)

            # Info button
            info_button = ttk.Button(
                frame,
                text="Doc. View",
                command=lambda e=param: self.update_info_box(
                    resource_path(f"data/grd_{e}.txt")
                ),
            )
            info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

            # Store in dictionary
            grd_prams_dict[param] = {"is_enabled": var, "entry": entry}

            # Pack frame into parent processing frame
            frame.grid(row=grd_command_frame_row, column=0, pady=2, stick=tk.W)
            grd_command_frame_row += 1

        # Run command button
        run_grd_button = ttk.Button(
            grd_command_frame,
            text="Run",
            command=lambda: self.run_las_ground(
                self.input_path.get(),
                os.path.join(self.grd_out_folder.get(), self.grd_out_file.get()),
                self.set_args(grd_prams_dict),
            ),
        )
        run_grd_button.grid(row=grd_command_frame_row, column=1, pady=2)

        view_button = ttk.Button(
            grd_command_frame,
            text="View",
            command=lambda: self.run_las_view(
                os.path.join(self.grd_out_folder.get(), self.grd_out_file.get())
            ),
        )
        view_button.grid(row=grd_command_frame_row, column=2, pady=2)

        return grd_command_frame

    def create_dem_command_frame(self, parent_frame):
        #dem frame
        dem_command_frame = ttk.Frame(parent_frame)
        dem_command_frame_row = 0
        dem_command_frame.columnconfigure(dem_command_frame_row, minsize=MIN_COL_0_W)

        #dem label
        dem_lb_frame = ttk.Frame(dem_command_frame)
        dem_lb = ttk.Label(dem_lb_frame, text="Compute DEM", font=H2_FONT)
        dem_lb.pack(side=tk.LEFT, padx=H1_PADX, pady=H1_PADY)

        # Info button
        info_button = ttk.Button(
            dem_lb_frame,
            text="Doc. View",
            command=lambda: self.update_info_box(
                resource_path("data/dem_blast2dem.txt")
            ),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        dem_lb_frame.grid(row=dem_command_frame_row, column=0, pady=2, sticky=tk.W)
        dem_command_frame_row += 1

        #Input Path

        #Output File

        #Output Folder

        #Resolution Parameter

        #Hillshade Option

            #Azimuth suboption

            #Altitude suboption

        #Run Command Button

        return dem_command_frame


    ### GRD Command Callbacks

    def update_grd_out_file(self, output_file):
        self.grd_out_file.delete(0, tk.END)
        self.grd_out_file.insert(0, f"grd_{output_file}")

    def update_grd_out_folder(self, output_folder):
        self.grd_out_folder.delete(0, tk.END)
        self.grd_out_folder.insert(0, f"{output_folder}")

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

    def create_widgets(self):
        """Create all widgets for the UI."""

        ### widgets
        # Title label
        title_lb = ttk.Label(self.root, text=WINDOW_TITLE, font=TITLE_FONT)

        input_lb = ttk.Label(self.root, text="Input Selection", font=H1_FONT)
        input_frame = self.create_input_frame()

        # processing frame
        processing_lb = ttk.Label(self.root, text="Processing", font=H1_FONT)
        processing_frame = self.create_processing_frame()

        # output box
        output_lb = ttk.Label(self.root, text="Output:", font=H1_FONT)
        self.output_text = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=TEXTBOX_HEIGHT, state=tk.DISABLED
        )

        # output box
        infobox_lb = ttk.Label(self.root, text="Documentation:", font=H1_FONT)
        self.infobox = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=INFOBOX_HEIGHT, state=tk.DISABLED
        )

        ### grid layout
        self.root.columnconfigure(
            0, minsize=MIN_COL_0_W
        )  # Set minimum size for column 0
        title_lb.grid(row=0, column=0, pady=2)

        ttk.Separator(self.root, orient="horizontal").grid(
            row=1, column=0, sticky=tk.EW, pady=2
        )
        input_lb.grid(row=2, column=0, sticky=tk.EW, pady=2, padx=TITLE_PADX)
        input_frame.grid(row=3, column=0, sticky=tk.EW, pady=2)

        ttk.Separator(self.root, orient="horizontal").grid(
            row=4, column=0, sticky=tk.EW, pady=2
        )
        processing_lb.grid(row=5, column=0, sticky=tk.W, pady=2, padx=TITLE_PADX)
        processing_frame.grid(row=6, column=0, sticky=tk.EW, pady=2, padx=TITLE_PADX)

        ttk.Separator(self.root, orient="horizontal").grid(
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


def main():
    """Main function to start the application."""
    lastools_path = LASTOOLS_PATH + "\\bin"
    if not os.path.exists(lastools_path):
        print(f"Cannot find .\\lastools\\bin at {lastools_path}")
        sys.exit(1)
    else:
        print(f"Found {lastools_path} ...")

    print(os.getcwd())
    # Create Tkinter root window and pass it to the app
    root = tk.Tk()
    app = CommandWrapperApp(root, lastools_path)

    # Start the Tkinter loop
    root.mainloop()


if __name__ == "__main__":
    main()
