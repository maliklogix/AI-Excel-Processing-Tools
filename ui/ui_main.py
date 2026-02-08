import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class HitrotechUI:
    def __init__(self, root, tool_defs, action_handlers):
        self.root = root
        self.tool_defs = tool_defs
        self.action_handlers = action_handlers
        self.setup_ui()
        
    def setup_ui(self):
        # Window + Global styling
        self.root.title("Hitrotech Data Tools")
        self.root.geometry("1050x760")
        self.root.minsize(880, 640)
        self.root.configure(bg="#FFE5B4")  # full window background (light orange)

        self.style = tb.Style()
        self.style.configure("App.TFrame", background="#fff3e0")
        self.style.configure("Header.TFrame", background="#ff7a1a")
        self.style.configure("Footer.TLabel", background="#fff3e0", foreground="#666666")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("CardHeader.TLabel", font=("Segoe UI", 11, "bold"))
        self.style.configure("CardDesc.TLabel", font=("Segoe UI", 9), foreground="#6b7280")
        self.style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=(8, 6))

        # Create header
        self.create_header()
        
        # Create main content area
        self.create_main_content()
        
        # Create footer
        self.create_footer()
        
        # Build the card grid
        self.build_card_grid()

    def create_header(self):
        # Header banner with soft animation
        self.header_frame = tb.Frame(self.root, style="Header.TFrame", height=88)
        self.header_frame.pack(fill="x", pady=(0, 16))
        self.header_frame.pack_propagate(False)

        self.banner = tb.Label(
            self.header_frame,
            text="HITROTECH DATA TOOLS",
            font=("Segoe UI", 24, "bold"),
            background="#ff7a1a",
            foreground="white",
        )
        self.banner.pack(expand=True)

        self._pulse = {"i": 0, "colors": ["#ff7a1a", "#ff8c3a", "#ffa25e", "#ff7a1a"]}
        self.animate_banner()

    def animate_banner(self):
        c = self._pulse["colors"][self._pulse["i"]]
        self.banner.config(background=c)
        self.header_frame.config(style="Header.TFrame")
        self._pulse["i"] = (self._pulse["i"] + 1) % len(self._pulse["colors"])
        self.root.after(700, self.animate_banner)

    def create_main_content(self):
        # Scrollable content area
        self.main_frame = tk.Frame(self.root, bg="#FFE5B4")  # match bg
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg="#fff3e0", highlightthickness=0)
        self.scrollbar = tb.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.content = tb.Frame(self.canvas, style="App.TFrame")

        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def create_footer(self):
        # Footer
        self.footer = tb.Frame(self.root, style="App.TFrame")
        self.footer.pack(fill="x", pady=(0, 10))

        self.info = tb.Label(self.footer, text="Powered by Hitrotech", font=("Segoe UI", 10), style="Footer.TLabel")
        self.info.pack(side="bottom")

    def build_card_grid(self):
        self.card_grid = CardGrid(self.content, self.tool_defs, self.action_handlers)
        self.card_grid.pack(fill="both", expand=True, padx=8, pady=8)

    def show_loading(self, title="Processing..."):
        popup = tb.Toplevel(self.root)
        popup.title(title)
        popup.geometry("420x128")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

        tb.Label(popup, text=title, font=("Segoe UI", 12, "bold")).pack(pady=10)
        prog = tb.Progressbar(popup, mode="indeterminate", bootstyle="success-striped")
        prog.pack(fill="x", padx=20, pady=10)
        prog.start(10)
        return popup, prog

    def select_files(self, filetypes):
        return filedialog.askopenfilenames(filetypes=filetypes)

    def select_folder(self):
        return filedialog.askdirectory()

    def ask_string(self, title, prompt):
        return simpledialog.askstring(title, prompt)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)


class CardGrid(tb.Frame):
    def __init__(self, master, tools, action_handlers, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.configure(style="App.TFrame")
        self.tools_all = tools
        self.tools_visible = list(tools)
        self.action_handlers = action_handlers
        self.cards = []
        self.columns = 3  # default; adjusted on resize

        # Search/filter row
        top = tb.Frame(self, style="App.TFrame")
        top.pack(fill="x", pady=(0, 8))

        self.search_var = tk.StringVar()
        search_entry = tb.Entry(top, textvariable=self.search_var)
        search_entry.pack(side="left", padx=(0, 8))
        search_entry.insert(0, "Search tools…")

        def on_focus_in(e):
            if self.search_var.get().strip() == "Search tools…":
                self.search_var.set("")
        def on_focus_out(e):
            if not self.search_var.get().strip():
                self.search_var.set("Search tools…")
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        search_entry.bind("<KeyRelease>", lambda e: self.apply_filter())

        # Create container for cards
        self.grid_wrap = tb.Frame(self, style="App.TFrame")
        self.grid_wrap.pack(fill="both", expand=True)

        # Respond to resize for dynamic columns
        self.bind("<Configure>", self._on_resize)
        self.render_cards()

    def apply_filter(self):
        q = self.search_var.get().lower().strip()
        if not q or q == "Search tools…":
            self.tools_visible = list(self.tools_all)
        else:
            self.tools_visible = [t for t in self.tools_all if q in t['title'].lower() or q in t.get('desc', '').lower()]
        self.render_cards()

    def _on_resize(self, event):
        width = event.width
        # Determine number of columns based on width
        if width < 700:
            cols = 4
        elif width < 980:
            cols = 4
        else:
            cols = 4
        if cols != self.columns:
            self.columns = cols
            self.render_cards()

    def clear(self):
        for c in self.cards:
            c.destroy()
        self.cards.clear()

    def render_cards(self):
        self.clear()
        for i, tool in enumerate(self.tools_visible):
            card = self._make_card(self.grid_wrap, tool)
            self.cards.append(card)
            r = i // self.columns
            c = i % self.columns
            card.grid(row=r, column=c, padx=8, pady=10, sticky="nsew")
        # grid weights
        for c in range(self.columns):
            self.grid_wrap.grid_columnconfigure(c, weight=1)

    def _make_card(self, master, tool):
        card = tb.Frame(master, style="Card.TFrame", bootstyle="light")
        card.configure(padding=12)
        card['borderwidth'] = 1
        card['relief'] = 'ridge'

        # Header row: icon + title
        header = tb.Frame(card, style="Card.TFrame")
        header.pack(fill="x")

        icon_lbl = tb.Label(header, text=tool.get('icon', '🧰'), font=("Segoe UI Emoji", 20))
        icon_lbl.pack(side="left")

        title_lbl = tb.Label(header, text=tool['title'], style="CardHeader.TLabel")
        title_lbl.pack(side="left", padx=10)

        # Description
        desc = tool.get('desc') or self._auto_desc(tool['title'])
        tb.Label(card, text=desc, style="CardDesc.TLabel", wraplength=280, justify="left").pack(anchor="w", pady=(6, 10))

        # Action button
        action_handler = self.action_handlers.get(tool['key'])
        if action_handler:
            tb.Button(card, text=tool.get('action_text', 'Open'), bootstyle="warning", 
                     style="Action.TButton", command=action_handler).pack(anchor="e")
        return card

    @staticmethod
    def _auto_desc(title: str) -> str:
        # Simple auto one-liner from title
        t = title.replace('→', 'to').replace('  ', ' ').strip()
        return f"Quickly run: {t}."