import sys
from cx_Freeze import setup, Executable

setup(
    name = "Yu-Gi-Oh! Power Of Chaos Save Handler",
    version = 1.0,
    description = "Manage YPOC save files across multiple computers.",
    executables = [Executable("ypocsh.py", base = None, icon = "icon.ico")],
    options={})