import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, font, scrolledtext
from PIL import Image, ImageTk

# Galaxy color palette
DEEP_SPACE = "#0b0b1a"
NEBULA_PURPLE = "#6a4c93"
STAR_BLUE = "#4d79ff"
COSMIC_PINK = "#ff4da6"
GALAXY_GRADIENT = ["#020111", "#191621", "#2F1559", "#4d79ff", "#6a4c93"]

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

class CosmicDictionary:
    def __init__(self, root):
        self.root = root
        self.setup_database()
        self.setup_ui()
        
    def setup_database(self):
        """Initialize database connection"""
        try:
            self.conn = sqlite3.connect(resource_path("kaikki_dictionary.db"))
            self.cur = self.conn.cursor()
            self.cur.execute("SELECT lang, COUNT(*) FROM entries GROUP BY lang ORDER BY lang")
            languages = self.cur.fetchall()
            self.lang_dict = {f"{lang} ({count})": lang for lang, count in languages}
        except sqlite3.Error as e:
            tk.messagebox.showerror("Database Error", f"Failed to connect to database:\n{str(e)}")
            self.root.destroy()
            exit()

    def create_gradient(self, canvas, width, height, colors):
        """Create a vertical gradient background"""
        for i in range(height):
            ratio = i / height
            r = int((1-ratio) * int(colors[0][1:3], 16) + ratio * int(colors[-1][1:3], 16))
            g = int((1-ratio) * int(colors[0][3:5], 16) + ratio * int(colors[-1][3:5], 16))
            b = int((1-ratio) * int(colors[0][5:7], 16) + ratio * int(colors[-1][5:7], 16))
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color)

    def search(self):
        """Handle search functionality"""
        word = self.word_entry.get().strip()
        selected_lang = self.lang_dict.get(self.lang_combo.get(), None)

        if not word:
            self.display_message("🌌 Please enter a word to search the cosmos...", COSMIC_PINK)
            return

        try:
            query = "SELECT pos, ipa, definition, lang FROM entries WHERE word = ?"
            params = [word]

            if selected_lang:
                query += " AND lang = ?"
                params.append(selected_lang)

            self.cur.execute(query, params)
            results = self.cur.fetchall()

            if not results:
                self.display_message(f"🚀 No celestial definitions found for '{word}'", COSMIC_PINK)
            else:
                self.display_results(word, results)
                
        except sqlite3.Error as e:
            self.display_message(f"Database error: {str(e)}", COSMIC_PINK)

    def display_message(self, message, color=COSMIC_PINK):
        """Display a message in the output area"""
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.tag_config("center", justify="center")
        self.output.tag_config("color", foreground=color)
        self.output.insert(tk.END, message + "\n", ("center", "color"))
        self.output.config(state=tk.DISABLED)

    def display_results(self, word, results):
        """Display search results in a formatted way"""
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        
        # Configure tags for styling
        self.output.tag_config("title", foreground=STAR_BLUE, font=("Arial", 16, "bold"))
        self.output.tag_config("definition_header", foreground=COSMIC_PINK)
        self.output.tag_config("language", foreground=STAR_BLUE)
        self.output.tag_config("pos", foreground="#aaaaaa", font=("Arial", 10, "italic"))
        self.output.tag_config("ipa", foreground=STAR_BLUE)
        
        # Insert title
        self.output.insert(tk.END, f"✨ {word.capitalize()} ✨\n\n", "title")
        
        for i, (pos, ipa, definition, lang) in enumerate(results, 1):
            # Insert definition header
            stars = "⭐" * min(3, i)
            self.output.insert(tk.END, f"{stars} Definition #{i}\n", "definition_header")
            
            # Insert language and POS
            self.output.insert(tk.END, f"Language: {lang}\n", "language")
            self.output.insert(tk.END, f"{pos}\n", "pos")
            
            # Insert IPA if available
            if ipa:
                self.output.insert(tk.END, f"Pronunciation: /{ipa}/\n", "ipa")
            
            # Insert definition
            self.output.insert(tk.END, f"{definition}\n\n")
        
        self.output.config(state=tk.DISABLED)

    def setup_ui(self):
        """Set up the user interface"""
        self.root.title("Cosnary - Offline Dictionary")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set window icon
        try:
            img = Image.open(resource_path("cosnary_icon.png"))
            photo = ImageTk.PhotoImage(img)
            self.root.iconphoto(False, photo)
        except:
            print("Icon image not found. Using default icon.")

        # Main background
        self.main_canvas = tk.Canvas(self.root, bg=DEEP_SPACE, highlightthickness=0)
        self.main_canvas.pack(fill=tk.BOTH, expand=True)
        self.create_gradient(self.main_canvas, 900, 700, GALAXY_GRADIENT)

        # Header frame
        self.header_frame = tk.Frame(self.main_canvas, bg="black")
        self.header_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        # Cosmic title
        self.title_label = tk.Label(self.header_frame, 
                                  text="Offline Dictionary", 
                                  font=("Arial", 24, "bold"),
                                  fg="white",
                                  bg="black")
        self.title_label.pack(pady=10)

        self.subtitle_label = tk.Label(self.header_frame,
                                     text="Explore the universe of words",
                                     font=("Arial", 12),
                                     fg=STAR_BLUE,
                                     bg="black")
        self.subtitle_label.pack()

        # Search frame
        self.search_frame = tk.Frame(self.main_canvas, bg=DEEP_SPACE)
        self.search_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        # Word entry
        self.word_label = tk.Label(self.search_frame, 
                                 text="Celestial Word:", 
                                 font=("Arial", 10),
                                 fg="white",
                                 bg=DEEP_SPACE)
        self.word_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.word_entry = ttk.Entry(self.search_frame, width=30, font=("Arial", 10))
        self.word_entry.grid(row=0, column=1, padx=5, pady=5)

        # Language selection
        self.lang_label = tk.Label(self.search_frame,
                                 text="Planet of Origin:",
                                 font=("Arial", 10),
                                 fg="white",
                                 bg=DEEP_SPACE)
        self.lang_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.lang_combo = ttk.Combobox(self.search_frame, 
                                     width=20, 
                                     state="readonly",
                                     font=("Arial", 10))
        self.lang_combo['values'] = ["All Galaxies"] + list(self.lang_dict.keys())
        self.lang_combo.set(next((k for k in self.lang_dict if self.lang_dict[k] == "English"), "All Galaxies"))
        self.lang_combo.grid(row=0, column=3, padx=5, pady=5)

        # Search button
        self.search_button = tk.Button(self.search_frame,
                                     text="🚀 Launch Search",
                                     command=self.search,
                                     bg=NEBULA_PURPLE,
                                     fg="white",
                                     activebackground=COSMIC_PINK,
                                     activeforeground="white",
                                     font=("Arial", 10, "bold"),
                                     relief=tk.FLAT,
                                     borderwidth=0)
        self.search_button.grid(row=0, column=4, padx=10, pady=5)

        # Output frame
        self.output_frame = tk.Frame(self.main_canvas, bg=DEEP_SPACE)
        self.output_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width=800, height=400)

        # Output text widget with scrollbar
        self.output = scrolledtext.ScrolledText(self.output_frame,
                                              wrap=tk.WORD,
                                              bg=DEEP_SPACE,
                                              fg="white",
                                              insertbackground="white",
                                              font=("Arial", 10),
                                              padx=10,
                                              pady=10)
        self.output.pack(fill=tk.BOTH, expand=True)
        self.display_message("Welcome to the Cosmic Dictionary\n\nEnter a word to explore its celestial definitions", STAR_BLUE)

        # Bind Enter key to search
        self.root.bind("<Return>", lambda event: self.search())

        # Focus on word entry when app starts
        self.word_entry.focus()

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = CosmicDictionary(root)
    root.mainloop()