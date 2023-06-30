import tkinter as tk
from tkinter import ttk


class Window:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("GUI")
        self.master.geometry("200x200")

        button = tk.Button(self.master, text="Click me!")
        button.pack(padx=5, pady=5)

        checkbutton = tk.Checkbutton(self.master, text="Check me!")
        checkbutton.pack(padx=5, pady=5)

        radiobutton = tk.Radiobutton(self.master, text="Radiobutton")
        radiobutton.pack(padx=5, pady=5)

        scale = tk.Scale(self.master, from_=0, to=10)
        scale.pack(padx=5, pady=5)


root = tk.Tk()
Window = Window(root)
root.mainloop()
