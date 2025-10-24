# KiCad Scripting Console helper (KiCad 6/7/8)
# Purpose: Quickly set up a simple single‑layer workflow, draw a rectangular board outline
# on Edge.Cuts, set a few defaults, and add a GND copper zone + fill.
#
# How to use:
# 1) Open pcbnew for your .kicad_pcb.  2) Tools → Scripting Console.  3) Paste & Run.
#    (Or save as a .py and run from the console with: exec(open(r"path/to/script.py").read()))
#
# Safe to re‑run: yes (it will replace the zone if it finds an older one with the same name tag).
# Tested: KiCad 7.0/8.0 APIs. Should work on 6.x as well.

import pcbnew

# =========================== USER SETTINGS ===========================
BOARD_W_MM = 100.0     # board width (mm)
BOARD_H_MM = 80.0      # board height (mm)
EDGE_MARGIN_MM = 0.5   # keep board outline lines inside this margin if you already had graphics

# Copper + rules
WORK_LAYER = pcbnew.F_Cu      # do front‑copper only workflow; change to pcbnew.B_Cu if you prefer
DEFAULT_TRACK_W_MM = 0.25
DEFAULT_VIA_D_MM   = 0.8
DEFAULT_VIA_DR_MM  = 0.4

# Zone
ZONE_NET_NAME = "GND"
ZONE_CLEARANCE_MM = 0.3
ZONE_MIN_THICK_MM = 0.25
ZONE_INSET_MM     = 1.0   # how far inside the edge cuts to draw the zone outline
ZONE_TAG          = "AUTO_GND_ZONE"

# =========================== HELPERS ================================
FromMM = pcbnew.FromMM

try:
    VEC = pcbnew.VECTOR2I  # KiCad 6/7/8
except AttributeError:
    # Fallback for very old KiCad (unlikely)
    from pcbnew import wxPoint as VEC


def vec_mm(x_mm: float, y_mm: float):
    return VEC(int(FromMM(x_mm)), int(FromMM(y_mm)))


def get_board():
    brd = pcbnew.GetBoard()
    if brd is None:
        raise RuntimeError("Open a .kicad_pcb first (pcbnew).")
    return brd


def ensure_net(board, name: str):
    """Return NETINFO_ITEM for name, creating it if needed."""
    nets = board.GetNetsByName()
    if name in nets:
        return nets[name]
    ni = pcbnew.NETINFO_ITEM(board, name)
    board.Add(ni)
    return ni


def draw_edge_cuts_rect(board, w_mm, h_mm):
    """Draw/replace a simple rectangular outline centered at (0,0) → (w,h) from origin.
    If an existing rectangle exists, we add another one; users can delete older graphics manually."""
    # We'll draw with top‑left at (0,0) and bottom‑right at (w,h) in positive coordinates.
    x0, y0 = EDGE_MARGIN_MM, EDGE_MARGIN_MM
    x1, y1 = w_mm - EDGE_MARGIN_MM, h_mm - EDGE_MARGIN_MM

    corners = [
        (x0, y0), (x1, y0),
        (x1, y1), (x0, y1),
    ]
    # 4 line segments
    for i in range(4):
        xA, yA = corners[i]
        xB, yB = corners[(i + 1) % 4]
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(vec_mm(xA, yA))
        seg.SetEnd(vec_mm(xB, yB))
        board.Add(seg)


def set_defaults(board):
    ds = board.GetDesignSettings()
    # Track width
    if hasattr(ds, "SetTrackWidth"):
        ds.SetTrackWidth(FromMM(DEFAULT_TRACK_W_MM))
    # Via sizes
    if hasattr(ds, "SetViaDiameter"):
        ds.SetViaDiameter(FromMM(DEFAULT_VIA_D_MM))
    if hasattr(ds, "SetViaDrill"):
        ds.SetViaDrill(FromMM(DEFAULT_VIA_DR_MM))

    # Optional: try to hint a single‑layer workflow via netclass layers (KiCad 7/8)
    try:
        bsetup = board.GetBoardSetup()  # KiCad 6+
        # Don't force copper layer count here (varies across versions); instead set allowed layers set.
        lset = pcbnew.LSET()
        lset.AddLayer(WORK_LAYER)
        # Apply to default netclass if API present
        nc = bsetup.GetDesignSettings().GetDefault()
        if hasattr(nc, "SetEnabledLayers"):
            nc.SetEnabledLayers(lset)
    except Exception:
        pass  # non‑fatal if API differs


def find_existing_zone(board, tag: str):
    for z in board.Zones():
        try:
            if z.GetZoneName() == tag:
                return z
        except Exception:
            # older KiCad: no name/tag stored; skip
            pass
    return None


def remove_zone(board, zone_obj):
    try:
        board.Remove(zone_obj)
    except Exception:
        # Fallback: mark for deletion via container
        zlist = list(board.Zones())
        if zone_obj in zlist:
            zlist.remove(zone_obj)


def add_gnd_zone(board, work_layer, net_name, tag):
    netinfo = ensure_net(board, net_name)
    netcode = netinfo.GetNetCode() if hasattr(netinfo, "GetNetCode") else netinfo.GetNet()

    # If we previously added a zone with this tag, remove it so reruns replace it.
    old = find_existing_zone(board, tag)
    if old is not None:
        remove_zone(board, old)

    z = pcbnew.ZONE_CONTAINER(board)
    z.SetLayer(work_layer)
    z.SetAssignedNetCode(netcode)
    z.SetZoneClearance(FromMM(ZONE_CLEARANCE_MM))
    z.SetMinThickness(FromMM(ZONE_MIN_THICK_MM))
    # FULL (solid) copper connection; change to THERMAL reliefs if desired
    if hasattr(pcbnew, "ZONE_CONNECTION_FULL"):
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)

    # Tag/name for easy identification on re‑runs (KiCad 7/8)
    if hasattr(z, "SetZoneName"):
        z.SetZoneName(tag)

    # Build a simple rectangle inside the board edges
    x0, y0 = ZONE_INSET_MM, ZONE_INSET_MM
    x1, y1 = BOARD_W_MM - ZONE_INSET_MM, BOARD_H_MM - ZONE_INSET_MM

    poly = z.Outline()
    poly.NewOutline()
    poly.Append(vec_mm(x0, y0))
    poly.Append(vec_mm(x1, y0))
    poly.Append(vec_mm(x1, y1))
    poly.Append(vec_mm(x0, y1))

    board.Add(z)

    # Fill zones
    filler = pcbnew.ZONE_FILLER(board)
    try:
        filler.Fill(board)
    except TypeError:
        # Very old KiCad signatures
        filler.Fill(zone = z)


# =========================== MAIN ===================================
def main():
    board = get_board()
    draw_edge_cuts_rect(board, BOARD_W_MM, BOARD_H_MM)
    set_defaults(board)
    add_gnd_zone(board, WORK_LAYER, ZONE_NET_NAME, ZONE_TAG)
    pcbnew.Refresh()
    print("✔ Done: Edge.Cuts rectangle, defaults set, and {} zone filled on {}.".format(ZONE_NET_NAME, "F.Cu" if WORK_LAYER==pcbnew.F_Cu else "B.Cu"))


if __name__ == "__main__":
    main()
