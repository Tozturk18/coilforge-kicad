#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:       //plugin/plugins/controller/__init__.py
Date:       2026-03-14
Author:     Ozgur Tuna Ozturk
Contact:    [@Tozturk18](tunaozturk2001@hotmail.com)
Last Mod:   2026-03-15
Version:    0.1.0
License:    MIT License
Description:
    This module initializes the controller component of the CoilForge plugin.
"""

from .controller import (
    prompt_for_config,   # Backward-compatible alias
    prompt_config       # Prompt for coil configuration
)
