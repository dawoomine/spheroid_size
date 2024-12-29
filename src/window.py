import os.path
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog

from spheroid_size import measure_ellipse_short_axis


class WindowMain(tk.Tk):
    def __init__(self):
        super().__init__(className="Spheroid Size Checker")

        self.image_file_path_var = tk.StringVar()
        self.output_directory_var = tk.StringVar()
        self.scalebar_diameter_var = tk.StringVar()
        self.scalebar_diameter_var.set("μM")
        self.scalebar_diameter = 0
        self.ratio_var = tk.DoubleVar()
        self.ratio_var.set(1.0)
        self.result_var = tk.StringVar()

        self.config_frame = ttk.Frame(self, padding=10)
        self.config_frame.grid()

        row = 1
        ttk.Label(self.config_frame, text="Image File:", justify="right").grid(column=0, row=row)
        ttk.Label(self.config_frame, textvariable=self.image_file_path_var, justify="right").grid(column=1, row=row)
        ttk.Button(self.config_frame, text="Select", command=self.select_file).grid(column=2, row=row)

        row += 1
        ttk.Label(self.config_frame, text="Output directory: ", justify="right").grid(column=0, row=row)
        ttk.Label(self.config_frame, textvariable=self.output_directory_var, justify="left").grid(column=1, row=row)
        ttk.Button(self.config_frame, text="Select", command=self.select_output_directory).grid(column=2, row=row)

        row += 1
        ttk.Label(self.config_frame, text="Scalebar diameter: ", justify="right").grid(column=0, row=row)
        ttk.Label(self.config_frame, textvariable=self.scalebar_diameter_var, justify="right").grid(column=1, row=row)
        ttk.Button(self.config_frame, text="Input", command=self.input_feret).grid(column=2, row=row)

        row += 1
        ttk.Label(self.config_frame, text="Ratio: ", justify="right").grid(column=0, row=row)
        ttk.Label(self.config_frame, textvariable=self.ratio_var).grid(column=1, row=row)
        ttk.Button(self.config_frame, text="Input", command=self.input_scalebar_size).grid(column=2, row=row)

        self.execution_frame = ttk.Frame(self, padding=10)
        self.execution_frame.grid(row=3)

        ttk.Button(self.execution_frame, text="Measure", command=self.measure).pack(pady=10)
        ttk.Label(self.execution_frame, textvariable=self.result_var).pack(pady=10)
        ttk.Button(self.execution_frame, text="Quit", command=self.destroy).pack(pady=10)

    def select_file(self):
        file = filedialog.askopenfile(title="Select image file")
        if file:
            self.image_file_path_var.set(file.name)
            if not self.output_directory_var.get():
                self.output_directory_var.set(os.path.dirname(self.image_file_path_var.get()))

    def input_feret(self):
        scalebar_diameter = simpledialog.askinteger(title="Scalebar diameter", prompt="Input")
        if scalebar_diameter:
            self.scalebar_diameter = scalebar_diameter
            self.scalebar_diameter_var.set(f"{scalebar_diameter} μM")

    def input_scalebar_size(self):
        scalebar_size = simpledialog.askfloat(title="Ratio", prompt="Input")
        if scalebar_size:
            self.ratio_var.set(scalebar_size)

    def select_output_directory(self):
        answer = filedialog.askdirectory()
        if answer:
            self.output_directory_var.set(answer)

    def measure(self):
        if not self.image_file_path_var.get():
            tkinter.messagebox.showerror(message="Select the image file.", **{'icon': tkinter.messagebox.ERROR})
            return

        if not os.path.exists(self.image_file_path_var.get()):
            tkinter.messagebox.showerror(message=f"Image file {self.image_file_path_var.get()} does not exist.")
            return

        if self.scalebar_diameter < 1:
            tkinter.messagebox.showerror(message="Input the scalebar diameter.")
            return

        result = measure_ellipse_short_axis(
            self.image_file_path_var.get(),
            self.output_directory_var.get(),
            self.scalebar_diameter,
            self.ratio_var.get())
        self.result_var.set(("contours: {contours}\n"
                             + "ellipses: {ellipses}\n"
                             + "average: {average}\n"
                             + "standard deviation: {standard deviation}\n"
                             + "input image: {input image}\n"
                             + "output image: {output image}\n"
                             + "result: {result}").format(**result))
        tkinter.messagebox.showinfo(message="Done!")


if __name__ == "__main__":
    WindowMain().mainloop()