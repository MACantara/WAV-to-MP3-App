import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style
from pathlib import Path
import subprocess

class ModernConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WAV to MP3 Converter")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        self.style = Style()
        self.style.configure("Modern.TButton", padding=10, font=("Segoe UI", 10))
        self.style.configure("Modern.Horizontal.TProgressbar", 
                           background='#2196F3', 
                           troughcolor='#E0E0E0',
                           thickness=15)

        self.source_files = []
        self.output_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.current_file_var = tk.StringVar(value="Ready to convert...")
        
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title_label = tk.Label(main_frame, 
                             text="WAV to MP3 Converter",
                             font=("Segoe UI", 16, "bold"),
                             bg="#f0f0f0",
                             fg="#333333")
        title_label.pack(pady=(0, 20))

        # Source selection frame
        source_frame = tk.Frame(main_frame, bg="#f0f0f0")
        source_frame.pack(fill="x", pady=(0, 10))
        
        self.source_label = tk.Label(source_frame,
                                   text="No files or folder selected",
                                   bg="#f0f0f0",
                                   font=("Segoe UI", 10))
        self.source_label.pack(side="top", anchor="w")

        button_frame = tk.Frame(source_frame, bg="#f0f0f0")
        button_frame.pack(fill="x", pady=(5, 0))

        self.browse_files_button = tk.Button(button_frame,
                                           text="Select WAV Files",
                                           command=self.select_source_files,
                                           bg="#2196F3",
                                           fg="white",
                                           font=("Segoe UI", 10),
                                           relief="flat",
                                           padx=15)
        self.browse_files_button.pack(side="left", padx=(0, 10))

        self.browse_folder_button = tk.Button(button_frame,
                                            text="Select WAV Folder",
                                            command=self.select_source_folder,
                                            bg="#2196F3",
                                            fg="white",
                                            font=("Segoe UI", 10),
                                            relief="flat",
                                            padx=15)
        self.browse_folder_button.pack(side="left")

        # Output selection
        output_frame = tk.Frame(main_frame, bg="#f0f0f0")
        output_frame.pack(fill="x", pady=10)
        
        self.output_label = tk.Label(output_frame,
                                   text="No output folder selected",
                                   bg="#f0f0f0",
                                   font=("Segoe UI", 10))
        self.output_label.pack(side="top", anchor="w")

        self.browse_output_button = tk.Button(output_frame,
                                            text="Select Output Folder",
                                            command=self.select_output_folder,
                                            bg="#2196F3",
                                            fg="white",
                                            font=("Segoe UI", 10),
                                            relief="flat",
                                            padx=15)
        self.browse_output_button.pack(side="left", pady=(5, 0))

        # Progress section
        progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        progress_frame.pack(fill="x", pady=20)

        self.current_file_label = tk.Label(progress_frame,
                                         textvariable=self.current_file_var,
                                         bg="#f0f0f0",
                                         font=("Segoe UI", 9))
        self.current_file_label.pack(anchor="w")

        self.progress_bar = Progressbar(progress_frame,
                                      variable=self.progress_var,
                                      maximum=100,
                                      style="Modern.Horizontal.TProgressbar")
        self.progress_bar.pack(fill="x", pady=(5, 10))

        # Start button
        self.start_button = tk.Button(main_frame,
                                    text="Start Conversion",
                                    command=self.start_conversion,
                                    bg="#4CAF50",
                                    fg="white",
                                    font=("Segoe UI", 11, "bold"),
                                    relief="flat",
                                    padx=20,
                                    pady=10)
        self.start_button.pack(pady=10)

    def select_source_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder with WAV Files")
        if folder_path:
            self.source_files = [str(p) for p in Path(folder_path).glob("**/*.wav")]
            self.update_source_label()

    def select_source_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select WAV Files",
            filetypes=[("WAV files", "*.wav")]
        )
        if file_paths:
            self.source_files = list(file_paths)
            self.update_source_label()

    def update_source_label(self):
        if self.source_files:
            self.source_label.config(text=f"Selected {len(self.source_files)} WAV files")
        else:
            self.source_label.config(text="No files or folder selected")

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            self.output_var.set(folder_path)
            self.output_label.config(text=f"Output: {folder_path}")

    def convert_files(self):
        total_files = len(self.source_files)
        for index, file_path in enumerate(self.source_files, 1):
            try:
                # Update current file label
                file_name = os.path.basename(file_path)
                self.current_file_var.set(f"Converting: {file_name} ({index}/{total_files})")
                
                # Get the filename without extension
                filename = os.path.splitext(os.path.basename(file_path))[0]
                output_file = os.path.join(self.output_var.get(), f"{filename}.mp3")

                # FFmpeg command
                subprocess.run(
                    ['ffmpeg', '-i', file_path, '-q:a', '0', output_file],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )

                # Update progress
                self.progress_var.set(index / total_files * 100)

            except Exception as e:
                messagebox.showerror("Error", f"Error converting {file_path}: {str(e)}")

        self.current_file_var.set("Conversion complete!")
        messagebox.showinfo("Success", "All files have been converted!")
        self.enable_buttons()

    def start_conversion(self):
        if not self.source_files:
            messagebox.showerror("Error", "Please select WAV files or a folder.")
            return

        if not self.output_var.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return

        # Disable buttons during conversion
        self.disable_buttons()
        
        # Reset progress
        self.progress_var.set(0)
        self.current_file_var.set("Starting conversion...")

        # Run the conversion in a separate thread
        threading.Thread(target=self.convert_files, daemon=True).start()

    def disable_buttons(self):
        for btn in [self.start_button, self.browse_files_button, 
                   self.browse_folder_button, self.browse_output_button]:
            btn.config(state=tk.DISABLED)

    def enable_buttons(self):
        for btn in [self.start_button, self.browse_files_button, 
                   self.browse_folder_button, self.browse_output_button]:
            btn.config(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernConverter()
    app.run()
