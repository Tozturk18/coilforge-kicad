'''
@ filename: __init__.py
@ author:   Ozgur Tuna Ozturk
@ date:     14/03/2024
@ license:  MIT License
@ description: This module initializes the CoilForge plugin for KiCad. 
    It imports the main plugin class and registers it with KiCad's plugin system.
'''

# --- IMPORTS --- #
from .plugin.plugin import CoilForgePlugin

# --- PLUGIN REGISTRATION --- #
CoilForgePlugin().register()