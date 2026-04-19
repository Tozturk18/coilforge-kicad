#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:       //plugin/plugins/__init__.py
Date:       2026-03-13
Author:     Ozgur Tuna Ozturk
Contact:    [@Tozturk18](tunaozturk2001@hotmail.com)
Last Mod:   2026-03-15
Version:    0.1.0
License:    MIT License
Description:
    This module initializes the CoilForge plugin for KiCad.
    It imports the main plugin class and registers it with KiCad's plugin system.
    KiCAD's plugin system searches the plugins directory for an __init__.py file 
    and executes it to register the plugin actions.
"""

# --- IMPORTS --- #
from .plugin.plugin import (
    CoilForgePlugin         # Main plugin class that registers the action with KiCad
)

# --- PLUGIN REGISTRATION --- #
CoilForgePlugin().register()