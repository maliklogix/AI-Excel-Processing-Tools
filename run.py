import ttkbootstrap as tb
from main.main03 import FurtherExtendedApp   # Use the further extended app

def run_app():
    root = tb.Window(themename="cosmo")
    app = FurtherExtendedApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()