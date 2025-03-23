import tkinter as tk
from tkinter import ttk, scrolledtext
from test import VideoNotesBot
import threading

class VideoNotesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Notes Buddy - Your Smart Study Companion")
        self.root.geometry("1000x700")  # Increased window size
        
        # Initialize the bot
        self.bot = VideoNotesBot()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weight to make it responsive
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Title Label with larger font
        title_label = ttk.Label(self.main_frame, 
                              text="Video Notes Buddy",
                              font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # URL Entry
        ttk.Label(self.main_frame, text="YouTube URL:").grid(row=1, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(self.main_frame, width=80)  # Increased width
        self.url_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Model Selection
        ttk.Label(self.main_frame, text="Select Model:").grid(row=2, column=0, sticky=tk.W)
        self.model_var = tk.StringVar(value="bart")
        self.model_combo = ttk.Combobox(self.main_frame, 
                                      textvariable=self.model_var,
                                      values=list(self.bot.available_models.keys()))
        self.model_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Generate Button
        self.generate_btn = ttk.Button(self.main_frame, text="Generate Summary", 
                                     command=self.generate_summary)
        self.generate_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Progress Frame
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='indeterminate')
        self.progress.grid(row=0, column=0, padx=(0, 10))
        
        # Progress Percentage
        self.progress_var = tk.StringVar(value="0%")
        self.progress_label = ttk.Label(progress_frame, 
                                      textvariable=self.progress_var,
                                      font=('Helvetica', 10, 'bold'))
        self.progress_label.grid(row=0, column=1)
        
        # Output Text Area (enlarged)
        self.output_text = scrolledtext.ScrolledText(self.main_frame, 
                                                   wrap=tk.WORD, 
                                                   width=90,  # Increased width
                                                   height=25, # Increased height
                                                   font=('Arial', 11))
        self.output_text.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_bar.grid(row=6, column=0, columnspan=2, sticky=tk.W)
        
    def generate_summary(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_var.set("Please enter a valid YouTube URL")
            return
            
        # Disable button and show progress
        self.generate_btn.state(['disabled'])
        self.progress.start()
        self.status_var.set("Generating summary...")
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set("0%")
        
        # Change model if needed
        selected_model = self.model_var.get()
        if selected_model:
            self.bot.change_model(selected_model)
        
        # Run processing in a separate thread
        def process():
            try:
                # Simulate progress updates
                for i in range(0, 101, 10):
                    self.root.after(i * 100, 
                                  lambda p=i: self.progress_var.set(f"{p}%"))
                
                summary = self.bot.process_video(url)
                self.root.after(0, self.update_output, summary)
            except Exception as e:
                self.root.after(0, self.update_output, f"Error: {str(e)}")
            finally:
                self.root.after(0, self.process_complete)
        
        threading.Thread(target=process, daemon=True).start()
    
    def update_output(self, text):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
    
    def process_complete(self):
        self.progress.stop()
        self.generate_btn.state(['!disabled'])
        self.status_var.set("Summary generation complete!")
        self.progress_var.set("100%")

def main():
    root = tk.Tk()
    app = VideoNotesGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 