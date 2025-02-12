# main.py

import tkinter as tk
from gui import TaskManagerGUI

def main():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
