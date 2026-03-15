"""
Helpers for converting CoilForge node lists into KiCad PCB arc objects
and grouping them so they can be moved as a single coil.
"""

from __future__ import annotations

import time

import pcbnew


COILFORGE_GROUP_PREFIX = "CoilForge:"


def make_coilforge_group_name(coil_id: str) -> str:
    """Build a stable CoilForge group name for the provided coil id."""
    return f"{COILFORGE_GROUP_PREFIX}{coil_id}"


def is_coilforge_group_name(group_name: str) -> bool:
    """Return True when a group name uses the CoilForge naming convention."""
    return isinstance(group_name, str) and group_name.startswith(COILFORGE_GROUP_PREFIX)


def coil_id_from_group_name(group_name: str) -> str | None:
    """Extract the coil id from a CoilForge group name."""
    if not is_coilforge_group_name(group_name):
        return None

    coil_id = group_name[len(COILFORGE_GROUP_PREFIX):].strip()
    return coil_id or None


def _iter_selection_items(selection):
    """Yield selected items from KiCad selection containers across API variants."""
    if selection is None:
        return

    if hasattr(selection, "GetCount") and hasattr(selection, "GetItem"):
        for i in range(selection.GetCount()):
            yield selection.GetItem(i)
        return

    if hasattr(selection, "Size") and hasattr(selection, "Item"):
        for i in range(selection.Size()):
            yield selection.Item(i)
        return

    try:
        for item in selection:
            yield item
    except TypeError:
        return


def _get_selected_items(board) -> list:
    """Get currently selected board items, or an empty list."""
    if board is None:
        return []

    selection = None
    if hasattr(board, "GetCurrentSelection"):
        selection = board.GetCurrentSelection()
    elif hasattr(pcbnew, "GetCurrentSelection"):
        selection = pcbnew.GetCurrentSelection()

    return list(_iter_selection_items(selection))


def get_selected_coilforge_groups(board=None) -> list[tuple[object, str]]:
    """
    Return selected CoilForge groups as (group_obj, coil_id), preserving selection order.
    """
    if board is None:
        board = pcbnew.GetBoard()

    selected_groups: list[tuple[object, str]] = []
    seen_groups: set[int] = set()

    for item in _get_selected_items(board):
        group = item if isinstance(item, pcbnew.PCB_GROUP) else None

        if group is None and hasattr(item, "GetParentGroup"):
            group = item.GetParentGroup()

        if group is None:
            continue

        group_key = id(group)
        if group_key in seen_groups:
            continue

        group_name = group.GetName() if hasattr(group, "GetName") else ""
        coil_id = coil_id_from_group_name(group_name)
        if coil_id is None:
            continue

        seen_groups.add(group_key)
        selected_groups.append((group, coil_id))

    return selected_groups


def _iter_group_items(group):
    """Yield items belonging to a PCB_GROUP across KiCad API variants."""
    if group is None:
        return

    if hasattr(group, "GetItems"):
        items = group.GetItems()
        try:
            for item in items:
                yield item
            return
        except TypeError:
            pass

    if hasattr(group, "GetItemCount") and hasattr(group, "GetItem"):
        for i in range(group.GetItemCount()):
            yield group.GetItem(i)


def _remove_board_item(board, item) -> None:
    """Remove a board item using the API available in the current KiCad build."""
    if hasattr(board, "RemoveNative"):
        board.RemoveNative(item)
    else:
        board.Remove(item)


def delete_group_and_items(board, group) -> None:
    """Delete a PCB group and all currently attached child items from the board."""
    if board is None or group is None:
        return

    for item in list(_iter_group_items(group)):
        _remove_board_item(board, item)

    _remove_board_item(board, group)


def group_nodes_into_arcs(
    nodes: list[tuple[float, float]]
) -> list[tuple[tuple[float, float], tuple[float, float], tuple[float, float]]]:
    """
    Convert an ordered node list into overlapping arc triplets.

    Expected node pattern:
        n0, n1, n2, n3, n4, ...
    Arc triplets become:
        (n0, n1, n2), (n2, n3, n4), ...

    This works for both:
    - full arcs
    - a final fractional arc, because the last two nodes are appended as:
      midpoint, endpoint

    Args:
        nodes: List of (x_mm, y_mm) tuples.

    Returns:
        List of arc triplets: [(start, mid, end), ...]
    """
    if len(nodes) < 3:
        return []

    if (len(nodes) - 1) % 2 != 0:
        raise ValueError(
            f"Invalid node count for arc grouping: {len(nodes)}. "
            "Expected node_count = 2*N + 1."
        )

    arcs = []
    for i in range(0, len(nodes) - 2, 2):
        arcs.append((nodes[i], nodes[i + 1], nodes[i + 2]))

    return arcs


def _to_iu_point(x_mm: float, y_mm: float):
    """
    Convert millimeter coordinates to a KiCad point in internal units.
    """
    x_iu = int(round(pcbnew.FromMM(x_mm)))
    y_iu = int(round(pcbnew.FromMM(y_mm)))

    if hasattr(pcbnew, "VECTOR2I"):
        return pcbnew.VECTOR2I(x_iu, y_iu)

    return pcbnew.wxPoint(x_iu, y_iu)


def build_pcb_arc(
    board,
    start_mm: tuple[float, float],
    mid_mm: tuple[float, float],
    end_mm: tuple[float, float],
    width_mm: float,
    layer_name: str = "F.Cu",
    net_name: str | None = None,
):
    """
    Build a single KiCad PCB_ARC object from one arc triplet.

    Args:
        board: Current pcbnew.BOARD object.
        start_mm: (x, y) in mm
        mid_mm: (x, y) in mm
        end_mm: (x, y) in mm
        width_mm: copper width in mm
        layer_name: e.g. "F.Cu", "B.Cu"
        net_name: optional net name

    Returns:
        pcbnew.PCB_ARC
    """
    arc = pcbnew.PCB_ARC(board)

    arc.SetStart(_to_iu_point(*start_mm))
    arc.SetMid(_to_iu_point(*mid_mm))
    arc.SetEnd(_to_iu_point(*end_mm))
    arc.SetWidth(int(round(pcbnew.FromMM(width_mm))))

    layer_id = board.GetLayerID(layer_name)
    arc.SetLayer(layer_id)

    if net_name:
        netinfo = board.FindNet(net_name)
        if netinfo is not None:
            arc.SetNet(netinfo)

    return arc


def build_pcb_arcs_from_nodes(
    board,
    nodes: list[tuple[float, float]],
    width_mm: float,
    layer_name: str = "F.Cu",
    net_name: str | None = None,
):
    """
    Convert a CoilForge node list into a list of pcbnew.PCB_ARC objects.
    """
    triplets = group_nodes_into_arcs(nodes)

    arcs = []
    for start_mm, mid_mm, end_mm in triplets:
        arc = build_pcb_arc(
            board=board,
            start_mm=start_mm,
            mid_mm=mid_mm,
            end_mm=end_mm,
            width_mm=width_mm,
            layer_name=layer_name,
            net_name=net_name,
        )
        arcs.append(arc)

    return arcs


def create_pcb_group(board, group_name: str | None = None):
    """
    Create a new PCB group on the board.

    Args:
        board: Current pcbnew.BOARD object.
        group_name: Optional name for the group.

    Returns:
        pcbnew.PCB_GROUP
    """
    group = pcbnew.PCB_GROUP(board)
    board.Add(group)

    if group_name and hasattr(group, "SetName"):
        group.SetName(group_name)

    return group


def add_items_to_group(group, items):
    """
    Add existing board items to a PCB group.

    Args:
        group: pcbnew.PCB_GROUP
        items: Iterable of board items already added to the board
    """
    for item in items:
        result = group.AddItem(item)
        # KiCad API variants differ here: some return bool, others return None.
        if result is False:
            raise RuntimeError(f"Failed to add item to group: {item}")


def build_grouped_pcb_arcs_from_nodes(
    board,
    nodes: list[tuple[float, float]],
    width_mm: float,
    layer_name: str = "F.Cu",
    net_name: str | None = None,
    group_name: str | None = None,
):
    """
    Convert a CoilForge node list into KiCad PCB arcs, add them to the board,
    and place them into a PCB group.

    Args:
        board: Current pcbnew.BOARD object.
        nodes: List of (x_mm, y_mm) tuples.
        width_mm: Arc width in mm.
        layer_name: KiCad layer name.
        net_name: Optional net name.
        group_name: Optional group name.

    Returns:
        (group, arcs)
        group: pcbnew.PCB_GROUP
        arcs: list of pcbnew.PCB_ARC
    """
    arcs = build_pcb_arcs_from_nodes(
        board=board,
        nodes=nodes,
        width_mm=width_mm,
        layer_name=layer_name,
        net_name=net_name,
    )

    for arc in arcs:
        board.Add(arc)

    if group_name is None:
        group_name = make_coilforge_group_name(str(int(time.time())))

    group = create_pcb_group(board, group_name=group_name)
    add_items_to_group(group, arcs)

    return group, arcs


def add_arcs_to_current_board(
    nodes: list[tuple[float, float]],
    width_mm: float,
    layer_name: str = "F.Cu",
    net_name: str | None = None,
    group_name: str | None = None,
    save_board: bool = False,
):
    """
    Build PCB_ARC objects from a node list, add them to the current board,
    group them so they move together, refresh the UI, and optionally save.

    Args:
        nodes: List of (x_mm, y_mm) tuples.
        width_mm: Arc width in mm.
        layer_name: KiCad layer name.
        net_name: Optional net name.
        group_name: Optional group name.
        save_board: If True, save the board after adding the grouped coil.

    Returns:
        (group, arcs)
        group: pcbnew.PCB_GROUP
        arcs: list of added pcbnew.PCB_ARC objects
    """
    board = pcbnew.GetBoard()
    if board is None:
        raise RuntimeError("No active board is open in KiCad.")

    group, arcs = build_grouped_pcb_arcs_from_nodes(
        board=board,
        nodes=nodes,
        width_mm=width_mm,
        layer_name=layer_name,
        net_name=net_name,
        group_name=group_name,
    )

    pcbnew.Refresh()

    if save_board:
        board_file = board.GetFileName()
        if board_file:
            ok = pcbnew.SaveBoard(board_file, board)
            if not ok:
                raise RuntimeError(f"Failed to save board to: {board_file}")

    return group, arcs
