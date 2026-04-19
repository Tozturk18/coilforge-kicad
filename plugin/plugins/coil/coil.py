#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File:       //plugin/plugins/coil/coil.py
Date:       2026-03-15
Author:     Ozgur Tuna Ozturk
Contact:    [@Tozturk18](tunaozturk2001@hotmail.com)
Last Mod:   2026-03-28
Version:    0.1.0
License:    MIT License
Description:
    Helpers for converting CoilForge node lists into KiCad PCB objects
    and grouping them so they can be moved as a single coil.
"""

# === IMPORTS === #
from __future__ import annotations

import pcbnew                   # KiCad's Python API for PCB manipulation

# === INTERNAL MODULES === #
from ..settings.settings import (
    COILFORGE_GROUP_PREFIX      # Prefix for group names
)

# === FUNCTIONS === #
def _group_name(coil_id: str) -> str:
    '''
    Generate a unique group name for a coil based on its ID.

    Args:   [str]: The unique identifier for the coil configuration.

    Return: [str]: A stable group name for use in KiCad's PCB objects.
    '''
    return f"{COILFORGE_GROUP_PREFIX}{coil_id}"


def _verify_name(group_name: str) -> bool:
    '''
    Return True when a group name uses the CoilForge naming convention.

    Args:   [str]: The group name to check.

    Return: [bool]: True if the name is a CoilForge group, False otherwise.
    '''
    return isinstance(group_name, str) and group_name.startswith(COILFORGE_GROUP_PREFIX)


def _extract_id(group_name: str) -> str | None:
    '''
    Extract the coil ID from a CoilForge group name.

    Args:   [str]: The group name to extract the ID from.

    Return: [str | None]: The extracted coil ID, or None if the name is not valid.
    '''
    if _verify_name(group_name):
        return group_name[len(COILFORGE_GROUP_PREFIX):].strip()
    return None


def _yield_groups(selection):
    '''
        Yield selected items from KiCad selection containers across API variants.

        Args:   selection: A selection object from KiCad's API, which may have different methods for accessing items depending on the version.

        Yields: Individual items from the selection
    '''
    # If selection is None, yield nothing
    if selection is None:
        return

    # Handle API with GetCount/GetItem methods (older KiCad versions)
    if hasattr(selection, "GetCount") and hasattr(selection, "GetItem"):
        for i in range(selection.GetCount()):
            yield selection.GetItem(i)
        return

    # Handle API with Size/Item methods (newer KiCad versions)
    if hasattr(selection, "Size") and hasattr(selection, "Item"):
        for i in range(selection.Size()):
            yield selection.Item(i)
        return

    # If selection has no recognized item access methods, try to iterate directly
    try:
        for item in selection:
            yield item
    except TypeError:
        return


def _get_selections(board: pcbnew.BOARD) -> tuple[pcbnew.SelectionContainer, ...]:
    '''
    Get all selection containers from the board, handling API differences.

    Args:   board: The pcbnew.BOARD object to retrieve selections from.

    Return: A tuple of selection containers found on the board.
    '''
    # If board is None, return an empty tuple
    if board is None:
        return ()
    
    selection = None

    # Try to get selections using BOARD GetSelections (newer API)
    if hasattr(board, "GetCurrentSelection"):
        selection = board.GetCurrentSelection()

    # Try to get selections using PCBNEW GetSelection (older API)
    elif hasattr(pcbnew, "GetCurrentSelection"):
        selection = pcbnew.GetCurrentSelection()

    # Return/Yield the selection(s) as a tuple
    return _yield_groups(selection)


def _get_groups(board: pcbnew.BOARD = None) -> list[tuple[object, str]]:
    '''
    Return selected CoilForge groups as (group_obj, coil_id), preserving selection order.

    Args:   board: The pcbnew.BOARD object to search for groups.

    Return: A list of tuples containing the group object and its associated coil ID.
    '''
    # If bord argument is None, find the board
    if board is None:
        board = pcbnew.GetBoard()

    # Use a dictionary to preserve order and uniqueness of groups
    groups : dict[int, tuple[object, str]] = {}

    # Iterate through all selected items
    for item in _get_selections(board):

        # Determine if the item is a group or has a parent group, and get the group object
        if isinstance(item, pcbnew.PCB_GROUP):
            group = item
        elif hasattr(item, "GetParentGroup") and callable(getattr(item, "GetParentGroup")):
            group = item.GetParentGroup()
        else:
            continue
        
        # No group found, skip
        if group is None:
            continue

        # Use the group object's id as a key
        group_key = id(group)
        # Skip if already processed
        if group_key in groups:
            continue

        # Extract the group name and coil ID
        group_name = group.GetName() if hasattr(group, "GetName") else ""
        coil_id = _extract_id(group_name)
        # Skip if group_id is not valid
        if coil_id is None:
            continue

        # Store the group and coil_id in the dictionary
        groups[group_key] = (group, coil_id)

    # Return the list of unique groups and their coil IDs
    return list(groups.values())


def _yield_items(group: object):
    '''
    Yield items from a group object, handling API differences.

    Args:   group: A group object from which to yield items.

    Yields: Individual items contained in the group.
    '''
    # If group is None, yield nothing
    if group is None:
        return

    # Handle API with GetItems method (older KiCad versions)
    if hasattr(group, "GetItems") and callable(getattr(group, "GetItems")):
        for item in group.GetItems():
            yield item
        return

    # Handle API with Items method (newer KiCad versions)
    if hasattr(group, "Items") and callable(getattr(group, "Items")):
        for item in group.Items():
            yield item
        return

    # If group has no recognized item access methods, try to iterate directly
    try:
        for item in group:
            yield item
    except TypeError:
        return


def _remove_item(board: pcbnew.BOARD, item: object) -> None:
    '''
    Remove an item from the board, handling API differences.

    Args:   board: The pcbnew.BOARD object from which to remove the item.
            item: The item to be removed from the board.

    Returns: None
    '''
    # If board or item is None, do nothing
    if board is None or item is None:
        return

    # Try to remove using BOARD Remove method (newer API)
    if hasattr(board, "RemoveNative") and callable(getattr(board, "RemoveNative")):
        board.RemoveNative(item)
        return

    # Try to remove using PCBNEW Remove method (older API)
    if hasattr(pcbnew, "Remove") and callable(getattr(pcbnew, "Remove")):
        pcbnew.Remove(item)
        return

    board.Remove(item)
    return


def _remove_group(board: pcbnew.BOARD, group: object) -> None:
    '''
    Remove a group and all its items from the board.

    Args:   board: The pcbnew.BOARD object from which to remove the group.
            group: The group object to be removed from the board.

    Returns: None
    '''
    # If board or group is None, do nothing
    if board is None or group is None:
        return

    # Remove all items in the group
    for item in _yield_items(group):
        _remove_item(board, item)

    # Finally, remove the group itself
    _remove_item(board, group)

