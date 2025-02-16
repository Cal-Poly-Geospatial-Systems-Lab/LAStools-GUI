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


class CommandWrapperApp:
    def __init__(self, root, lastools_path):
        self.root = root
        self.lastools_path = lastools_path
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.cur_doc_name = ""

        # Create UI components
        self.create_widgets()

    def update_grd_out_file(self, output_file):
        self.grd_out_file.delete(0, tk.END)
        self.grd_out_file.insert(0, f"grd_{output_file}")

    def update_grd_out_folder(self, output_folder):
        self.grd_out_folder.delete(0, tk.END)
        self.grd_out_folder.insert(0, f"{output_folder}")

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

    def decimal_validation(self, P):
        if P == "":  # Allow empty input (for backspacing)
            return True
        try:
            float(P)  # Try converting the input to a float
            return True
        except ValueError:
            return False

    def create_processing_frame(self):
        processing_frame = ttk.Frame(self.root)

        processing_frame.columnconfigure(0, minsize=MIN_COL_0_W)
        # grd
        ground_lb_frame = ttk.Frame(processing_frame)

        ground_lb = ttk.Label(ground_lb_frame, text="Lasground", font=H2_FONT)
        ground_lb.pack(side=tk.LEFT, padx=H1_PADX, pady=H1_PADY)

        # Info button
        info_button = ttk.Button(
            ground_lb_frame,
            text="View Info",
            command=lambda: self.update_info_box(f"docs/grd_lasground.txt"),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        ground_lb_frame.grid(row=0, column=0, pady=2, sticky=tk.W)

        # out file
        grd_out_file_selector = ttk.Frame(processing_frame)
        ttk.Label(grd_out_file_selector, text="Output File:").pack(
            side=tk.LEFT, padx=VIEW_BTN_PADX
        )
        self.grd_out_file = ttk.Entry(grd_out_file_selector)
        self.grd_out_file.insert(0, f"grd_{self.input_path.get()}")
        self.grd_out_file.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=VIEW_BTN_PADX)

        grd_out_file_selector.grid(row=1, column=0, pady=2, sticky=tk.EW)

        # out folder
        grd_out_folder = ttk.Frame(processing_frame)
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

        grd_out_folder.grid(row=2, column=0, pady=2, sticky=tk.EW)

        # step parameter
        grd_step_frame = ttk.Frame(processing_frame)
        ttk.Label(grd_step_frame, text="Step:").pack(side=tk.LEFT, padx=VIEW_BTN_PADX)
        v_dec_cmd = grd_step_frame.register(self.decimal_validation)
        # Info button
        info_button = ttk.Button(
            grd_step_frame,
            text="View Info",
            command=lambda: self.update_info_box(f"docs/grd_step.txt"),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

        self.grd_step = ttk.Entry(
            grd_step_frame, validate="all", validatecommand=(v_dec_cmd, "%P")
        )
        self.grd_step.insert(0, DEF_GRD_STEP)
        self.grd_step.pack(side=tk.LEFT, fill=tk.X, padx=VIEW_BTN_PADX)
        grd_step_frame.grid(row=3, column=0, pady=2, stick=tk.W)

        def toggle_Entry(var: tk.IntVar, entry: tk.Entry):
            if var.get() == 1:
                entry.config(state=tk.NORMAL)
            else:
                entry.config(state=tk.DISABLED)

        toogle_parameters_frame = ["stddev", "offset", "bulge", "spike", "sub"]

        # Dictionary to store frames, variables, and entry widgets
        toggle_elements = {}

        start_row = 4
        for param in toogle_parameters_frame:
            frame = ttk.Frame(processing_frame)
            var = tk.IntVar()

            ttk.Checkbutton(
                frame,
                text=f"Enable {param.capitalize()}",
                variable=var,
                command=lambda v=var, e=param: toggle_Entry(
                    v, toggle_elements[e]["entry"]
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
                text="View Info",
                command=lambda e=param: self.update_info_box(f"docs/grd_{e}.txt"),
            )
            info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)

            # Store in dictionary
            toggle_elements[param] = {"var": var, "entry": entry}

            # Pack frame into parent processing frame
            frame.grid(row=start_row, column=0, pady=2, stick=tk.W)
            start_row += 1

        # Run command button
        run_grd_button = ttk.Button(
            processing_frame,
            text="Run",
            command=lambda: [
                self.set_args(toggle_elements),
                self.run_las_ground(
                    self.input_path.get(),
                    os.path.join(self.grd_out_folder.get(), self.grd_out_file.get()),
                    self.grd_args,
                ),
            ],
        )
        run_grd_button.grid(row=9, column=1, pady=2)

        view_button = ttk.Button(
            processing_frame,
            text="View",
            command=lambda: self.run_las_view(
                os.path.join(self.grd_out_folder.get(), self.grd_out_file.get())
            ),
        )
        view_button.grid(row=9, column=2, pady=2)


        #hillshade
        ground_lb_frame = ttk.Frame(processing_frame)

        ground_lb = ttk.Label(ground_lb_frame, text="Hillshade", font=H2_FONT)
        ground_lb.pack(side=tk.LEFT, padx=H1_PADX, pady=H1_PADY)

        # Info button
        info_button = ttk.Button(
            ground_lb_frame,
            text="View Info",
            command=lambda: self.update_info_box(f"docs/hill_blast.txt"),
        )
        info_button.pack(side=tk.RIGHT, padx=VIEW_BTN_PADX)
        ground_lb_frame.grid(row=10, column=0, pady=2, sticky=tk.W)

        return processing_frame

    def set_args(self, toggle_args_dict):
        self.grd_args = " -step " + self.grd_step.get()
        for arg in toggle_args_dict:
            print(toggle_args_dict.get(arg).get("var").get())
            if toggle_args_dict.get(arg).get("var").get() == 1:
                self.grd_args += (
                    " -"
                    + str(arg)
                    + " "
                    + str(toggle_args_dict.get(arg).get("entry").get())
                )

    def create_widgets(self):
        """Create all widgets for the UI."""

        ### widgets
        # Title label
        title_lb = ttk.Label(self.root, text=WINDOW_TITLE, font=TITLE_FONT)

        input_lb = ttk.Label(self.root, text="Input Selection", font=H1_FONT)

        # Frame for input selector and button
        input_frame = ttk.Frame(self.root)
        ttk.Label(input_frame, text="Select File:").pack(
            side=tk.LEFT, padx=H2_PADX
        )
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

        # processing frame
        processing_lb = ttk.Label(self.root, text="Processing", font=H1_FONT)
        processing_frame = self.create_processing_frame()

        # blast_lb = ttk.Label(self.root, text="blast2dem", font=H2_FONT)
        # hillshade_lb = ttk.Label(self.root, text="hillshade", font=H2_FONT)

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
        # self.root.columnconfigure(1, minsize=MIN_COL_0_W)  # Set minimum size for column 0

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

    def run_las_view(self, file_path):
        if os.path.exists(file_path):
            self.update_output(f"lasview: {file_path}")
            command = self.lastools_path + "\\"
            command += f"lasview64.exe {file_path}"
            print(command)
            returncode = self.check_output(command)

            ### check return code
            if returncode != 0:
                print("Error. lasview failed.")
                sys.exit(1)
        else:
            self.update_output(f"No input specified: {file_path}\n")

    def run_las_ground(self, input_path, output_path, las_args):
        if input_path:
            self.update_output(f"lasview: {input_path}")
            command = self.lastools_path + "\\"
            command += f"lasground64.exe -v -i {input_path} -o {output_path} {las_args}"
            print(command)
            returncode = self.check_output(command)

            ### check return code
            if returncode != 0:
                print("Error. lasground failed.")
                sys.exit(1)
        else:
            self.update_output(f"No input specified: {input_path}\n")

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

    def run_command(self):
        """Placeholder for a generic command run, for future expansion."""
        file_path = self.input_path.get()
        self.update_output(f"Running command with file: {file_path}")


def main():
    """Main function to start the application."""
    lastools_path = LASTOOLS_PATH + "\\bin"
    if not os.path.exists(lastools_path):
        print(f"Cannot find .\\lastools\\bin at {lastools_path}")
        sys.exit(1)
    else:
        print(f"Found {lastools_path} ...")

    # Create Tkinter root window and pass it to the app
    root = tk.Tk()
    app = CommandWrapperApp(root, lastools_path)

    # Start the Tkinter loop
    root.mainloop()


if __name__ == "__main__":
    main()
