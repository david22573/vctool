import ttkbootstrap
from ttkbootstrap.constants import *

app = ttkbootstrap.ThemedTk(themename="darkly")

open_button = ttk.Button(app, text="Open", command=open_dialog, bootstyle=SUCCESS)