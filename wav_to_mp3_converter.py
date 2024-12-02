import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.ttk import Progressbar, Style
from pathlib import Path
import subprocess
import shutil
from google_services import GoogleServices

class ModernConverter:
    def __init__(self):
        # Check for FFmpeg
        if not self.check_ffmpeg():
            messagebox.showerror("Error", "FFmpeg is not installed or not found in PATH. Please install FFmpeg to use this application.")
            exit(1)

        self.root = tk.Tk()
        self.root.title("Podcast Episode Uploader")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        self.style = Style()
        self.style.configure("Modern.TButton", padding=10, font=("Segoe UI", 10))
        self.style.configure("Conversion.Horizontal.TProgressbar", 
                           background='#2196F3', 
                           troughcolor='#E0E0E0',
                           thickness=15)
        self.style.configure("Upload.Horizontal.TProgressbar", 
                           background='#4CAF50', 
                           troughcolor='#E0E0E0',
                           thickness=15)

        self.source_files = []
        self.output_var = tk.StringVar()
        self.conversion_progress_var = tk.DoubleVar()
        self.upload_progress_var = tk.DoubleVar()
        self.current_file_var = tk.StringVar(value="Ready to convert...")
        
        # Google Drive folders
        self.google_drive_folder = tk.StringVar()
        self.folders_list = []
        
        # Google Sheets
        self.spreadsheet_id = tk.StringVar()
        self.sheet_range = tk.StringVar(value="Sheet1!A:A")  # Default range
        
        try:
            self.google_services = GoogleServices()
            self.folders_list = self.google_services.get_folder_list()
        except Exception as e:
            messagebox.showerror("Google Services Error", 
                               "Failed to initialize Google Services. Please ensure credentials.json is present.\n\nError: " + str(e))
        
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title_label = tk.Label(main_frame, 
                             text="Podcast Episode Uploader",
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

        # Google Drive folder selection
        drive_frame = tk.Frame(main_frame, bg="#f0f0f0")
        drive_frame.pack(fill="x", pady=10)
        
        tk.Label(drive_frame,
                text="Select Google Drive Folder:",
                bg="#f0f0f0",
                font=("Segoe UI", 10)).pack(side="top", anchor="w")

        self.folder_combobox = ttk.Combobox(drive_frame,
                                          textvariable=self.google_drive_folder,
                                          values=[f"{f.get('name')} ({f.get('id')})" for f in self.folders_list],
                                          state="readonly",
                                          font=("Segoe UI", 10))
        self.folder_combobox.pack(fill="x", pady=(5, 0))

        # Google Sheets configuration
        sheets_frame = tk.Frame(main_frame, bg="#f0f0f0")
        sheets_frame.pack(fill="x", pady=10)
        
        tk.Label(sheets_frame,
                text="Google Sheets Configuration:",
                bg="#f0f0f0",
                font=("Segoe UI", 10, "bold")).pack(side="top", anchor="w")

        # Spreadsheet selection
        spreadsheet_frame = tk.Frame(sheets_frame, bg="#f0f0f0")
        spreadsheet_frame.pack(fill="x", pady=(5, 0))
        
        tk.Label(spreadsheet_frame,
                text="Select Google Sheet:",
                bg="#f0f0f0",
                font=("Segoe UI", 10)).pack(side="top", anchor="w")

        self.spreadsheet_combobox = ttk.Combobox(spreadsheet_frame,
                                               state="readonly",
                                               font=("Segoe UI", 10))
        self.spreadsheet_combobox.pack(fill="x", pady=(5, 0))
        self.spreadsheet_combobox.bind('<<ComboboxSelected>>', self.on_spreadsheet_selected)

        # Sheet/tab selection
        sheet_frame = tk.Frame(sheets_frame, bg="#f0f0f0")
        sheet_frame.pack(fill="x", pady=(10, 0))
        
        tk.Label(sheet_frame,
                text="Select Sheet:",
                bg="#f0f0f0",
                font=("Segoe UI", 10)).pack(side="top", anchor="w")

        self.sheet_combobox = ttk.Combobox(sheet_frame,
                                        state="readonly",
                                        font=("Segoe UI", 10))
        self.sheet_combobox.pack(fill="x", pady=(5, 0))
        self.sheet_combobox.bind('<<ComboboxSelected>>', self.on_sheet_selected)

        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.pack(pady=10)

        # Convert button
        self.convert_button = tk.Button(buttons_frame,
                                    text="Convert to MP3",
                                    command=self.start_conversion,
                                    bg="#2196F3",
                                    fg="white",
                                    font=("Segoe UI", 11, "bold"),
                                    relief="flat",
                                    padx=20,
                                    pady=10)
        self.convert_button.pack(side="left", padx=10)

        # Upload button
        self.upload_button = tk.Button(buttons_frame,
                                   text="Upload to Drive",
                                   command=self.start_upload,
                                   bg="#4CAF50",
                                   fg="white",
                                   font=("Segoe UI", 11, "bold"),
                                   relief="flat",
                                   padx=20,
                                   pady=10,
                                   state=tk.DISABLED)  # Initially disabled
        self.upload_button.pack(side="left", padx=10)

        # Progress section
        progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        progress_frame.pack(fill="x", pady=20)

        # Conversion progress
        conversion_label_frame = tk.Frame(progress_frame, bg="#f0f0f0")
        conversion_label_frame.pack(fill="x")
        
        tk.Label(conversion_label_frame,
                text="Conversion Progress:",
                bg="#f0f0f0",
                font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.conversion_status = tk.Label(conversion_label_frame,
                                      text="0%",
                                      bg="#f0f0f0",
                                      font=("Segoe UI", 9))
        self.conversion_status.pack(side="right")

        self.conversion_progress = Progressbar(progress_frame,
                                           variable=self.conversion_progress_var,
                                           maximum=100,
                                           style="Conversion.Horizontal.TProgressbar")
        self.conversion_progress.pack(fill="x", pady=(5, 10))

        # Upload progress
        upload_label_frame = tk.Frame(progress_frame, bg="#f0f0f0")
        upload_label_frame.pack(fill="x")
        
        tk.Label(upload_label_frame,
                text="Upload Progress:",
                bg="#f0f0f0",
                font=("Segoe UI", 9, "bold")).pack(side="left")
        
        self.upload_status = tk.Label(upload_label_frame,
                                  text="0%",
                                  bg="#f0f0f0",
                                  font=("Segoe UI", 9))
        self.upload_status.pack(side="right")

        self.upload_progress = Progressbar(progress_frame,
                                       variable=self.upload_progress_var,
                                       maximum=100,
                                       style="Upload.Horizontal.TProgressbar")
        self.upload_progress.pack(fill="x", pady=(5, 10))

        # Current file label
        self.current_file_label = tk.Label(progress_frame,
                                       textvariable=self.current_file_var,
                                       bg="#f0f0f0",
                                       font=("Segoe UI", 9))
        self.current_file_label.pack(anchor="w")

        self.load_spreadsheets()

    def check_ffmpeg(self):
        """Check if FFmpeg is installed and available."""
        return shutil.which('ffmpeg') is not None

    def update_conversion_progress(self, value):
        """Update conversion progress bar and percentage."""
        self.conversion_progress_var.set(value)
        self.conversion_status.config(text=f"{int(value)}%")
        self.root.update_idletasks()

    def update_upload_progress(self, value, current_file=""):
        """Update upload progress bar and percentage."""
        self.upload_progress_var.set(value)
        self.upload_status.config(text=f"{int(value)}%")
        if current_file:
            self.current_file_var.set(f"Uploading: {current_file}")
        self.root.update_idletasks()

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

    def get_selected_folder_id(self):
        selected = self.folder_combobox.get()
        if selected:
            folder_id = selected.split('(')[-1].rstrip(')')
            return folder_id
        return None

    def convert_files(self):
        """Convert WAV files to MP3."""
        total_files = len(self.source_files)
        self.converted_files = []  # Store converted file paths
        
        for index, file_path in enumerate(self.source_files, 1):
            try:
                # Update current file label
                file_name = os.path.basename(file_path)
                self.current_file_var.set(f"Converting: {file_name} ({index}/{total_files})")
                
                # Get the filename without extension
                filename = os.path.splitext(os.path.basename(file_path))[0]
                output_file = os.path.join(self.output_var.get(), f"{filename}.mp3")

                # FFmpeg command with better quality settings
                try:
                    result = subprocess.run(
                        ['ffmpeg', '-y', '-i', file_path, 
                         '-codec:a', 'libmp3lame', '-qscale:a', '2',
                         output_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    raise Exception(f"FFmpeg error: {e.stderr}")

                self.converted_files.append(output_file)
                # Update progress
                progress = (index / total_files) * 100
                self.update_conversion_progress(progress)

            except Exception as e:
                messagebox.showerror("Error", f"Error converting {file_path}: {str(e)}")

        self.current_file_var.set("Conversion complete!")
        messagebox.showinfo("Success", "All files have been converted!")
        self.enable_buttons()
        self.upload_button.config(state=tk.NORMAL)  # Enable upload button

    def upload_files(self):
        """Upload MP3 files to Google Drive and update sheets."""
        if not hasattr(self, 'converted_files') or not self.converted_files:
            messagebox.showerror("Error", "No converted files found. Please convert files first.")
            return

        if not self.spreadsheet_id.get():
            messagebox.showerror("Error", "Please select a Google Sheet first.")
            return

        if not self.sheet_combobox.get():
            messagebox.showerror("Error", "Please select a sheet/tab first.")
            return

        total_files = len(self.converted_files)
        uploaded_files = []
        
        for index, file_path in enumerate(self.converted_files, 1):
            try:
                # Get filename for display
                file_name = os.path.basename(file_path)
                self.current_file_var.set(f"Uploading: {file_name} ({index}/{total_files})")

                # Upload to Google Drive with progress tracking
                folder_id = self.get_selected_folder_id()
                if folder_id:
                    def update_single_file_progress(progress):
                        # Calculate overall progress
                        overall_progress = ((index - 1) * 100 + progress) / total_files
                        self.update_upload_progress(overall_progress, file_name)
                    
                    file_id, web_link = self.google_services.upload_to_drive(
                        file_path, 
                        folder_id,
                        progress_callback=update_single_file_progress
                    )
                    
                    filename = os.path.splitext(os.path.basename(file_path))[0]
                    uploaded_files.append([filename, web_link])

            except Exception as e:
                messagebox.showerror("Error", f"Error uploading {file_path}: {str(e)}")

        # Update Google Sheets
        if uploaded_files:
            try:
                self.current_file_var.set("Updating Google Sheets...")
                print(f"Updating sheet with ID: {self.spreadsheet_id.get()}")
                print(f"Range: {self.sheet_range.get()}")
                print(f"Files: {uploaded_files}")
                
                self.google_services.update_spreadsheet(
                    self.spreadsheet_id.get(),
                    self.sheet_range.get(),
                    uploaded_files,
                    self.handle_unmatched_files
                )
            except Exception as e:
                messagebox.showerror("Error", f"Error updating Google Sheets: {str(e)}\nSpreadsheet ID: {self.spreadsheet_id.get()}\nRange: {self.sheet_range.get()}")
                return

        self.current_file_var.set("Upload complete!")
        messagebox.showinfo("Success", "All files have been uploaded and documented!")
        self.enable_buttons()

    def start_conversion(self):
        """Start the conversion process."""
        if not self.source_files:
            messagebox.showerror("Error", "Please select WAV files or a folder.")
            return

        if not self.output_var.get():
            messagebox.showerror("Error", "Please select an output folder.")
            return

        # Reset progress bars
        self.update_conversion_progress(0)
        self.update_upload_progress(0)
        
        # Disable buttons during processing
        self.disable_buttons()
        
        self.current_file_var.set("Starting conversion...")

        # Run the conversion in a separate thread
        threading.Thread(target=self.convert_files, daemon=True).start()

    def start_upload(self):
        """Start the upload process."""
        if not self.get_selected_folder_id():
            messagebox.showerror("Error", "Please select a Google Drive folder.")
            return

        if not self.spreadsheet_combobox.get():
            messagebox.showerror("Error", "Please select a Google Sheet.")
            return

        if not self.sheet_combobox.get():
            messagebox.showerror("Error", "Please select a sheet/tab.")
            return

        # Reset upload progress
        self.update_upload_progress(0)
        
        # Disable buttons during processing
        self.disable_buttons()
        
        self.current_file_var.set("Starting upload...")

        # Run the upload in a separate thread
        threading.Thread(target=self.upload_files, daemon=True).start()

    def disable_buttons(self):
        """Disable all buttons during processing."""
        for btn in [self.convert_button, self.upload_button, self.browse_files_button, 
                   self.browse_folder_button, self.browse_output_button]:
            btn.config(state=tk.DISABLED)
        self.folder_combobox.config(state="disabled")
        self.spreadsheet_combobox.config(state="disabled")
        self.sheet_combobox.config(state="disabled")

    def enable_buttons(self):
        """Enable all buttons after processing."""
        for btn in [self.convert_button, self.browse_files_button, 
                   self.browse_folder_button, self.browse_output_button]:
            btn.config(state=tk.NORMAL)
        self.folder_combobox.config(state="readonly")
        self.spreadsheet_combobox.config(state="readonly")
        self.sheet_combobox.config(state="readonly")
        # Note: upload_button state is managed separately

    def load_spreadsheets(self):
        """Load available Google Sheets documents."""
        try:
            spreadsheets = self.google_services.get_spreadsheet_list()
            self.spreadsheets = {name: id for id, name in spreadsheets}
            self.spreadsheet_combobox['values'] = list(self.spreadsheets.keys())
        except Exception as e:
            messagebox.showerror("Error", f"Error loading spreadsheets: {str(e)}")

    def on_spreadsheet_selected(self, event=None):
        """Handle spreadsheet selection."""
        selected_spreadsheet = self.spreadsheet_combobox.get()
        if selected_spreadsheet:
            try:
                spreadsheet_id = self.spreadsheets[selected_spreadsheet]
                self.spreadsheet_id.set(spreadsheet_id)
                
                # Get available sheets/tabs
                sheets = self.google_services.get_sheets_in_spreadsheet(spreadsheet_id)
                self.sheet_combobox['values'] = sheets
                if sheets:
                    self.sheet_combobox.set(sheets[0])
                    self.on_sheet_selected()
            except Exception as e:
                messagebox.showerror("Error", f"Error loading sheets: {str(e)}")

    def on_sheet_selected(self, event=None):
        """Handle sheet selection."""
        selected_sheet = self.sheet_combobox.get()
        if selected_sheet:
            self.sheet_range.set(f"{selected_sheet}!A:B")

    def handle_unmatched_files(self, unmatched_files):
        """Show dialog for unmatched files and return whether to create new entries."""
        if not unmatched_files:
            return False
            
        # Create list of unmatched filenames
        filenames = [file[0] for file in unmatched_files]
        message = "The following files don't have exact matches in the spreadsheet:\n\n"
        message += "\n".join(filenames)
        message += "\n\nWould you like to create new entries for these files?"
        
        response = messagebox.askyesno(
            "Unmatched Files Found",
            message,
            icon='warning'
        )
        
        return response

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernConverter()
    app.run()
