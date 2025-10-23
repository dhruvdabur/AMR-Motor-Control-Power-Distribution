# KiCad pcbnew combined script: make a 160x120 mm outline and place corner mounting holes
import pcbnew

# ======================== User settings =========================
BOARD_W_MM = 160.0
BOARD_H_MM = 120.0
EDGE_WIDTH_MM = 0.1

CENTER_AT_ORIGIN = False        # False → lower-left at (0,0); True → center at (0,0)
CLEAR_OLD_EDGES  = False        # True to remove existing Edge.Cuts first

# Mounting hole settings
MOUNT_LIB   = "MountingHole"
MOUNT_NAME  = "MountingHole_3.2mm_M3"  # NPTH for M3 screw (3.2 mm)
INSET_MM    = 4.0                      # distance from board edge to hole center
REF_PREFIX  = "MH"
LOCK_PLACED = True
# ================================================================

brd = pcbnew.GetBoard()
mm  = pcbnew.FromMM

def edge_shapes(board):
    # Yield all Edge.Cuts shapes to optionally clear them
    for d in board.GetDrawings():
        if isinstance(d, pcbnew.PCB_SHAPE) and d.GetLayer() == pcbnew.Edge_Cuts:
            yield d

def clear_edge_cuts(board):
    to_del = list(edge_shapes(board))
    for d in to_del:
        board.Remove(d)

def add_edge_seg(board, xa, ya, xb, yb, width_mm=0.1):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T.S_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(int(xa), int(ya)))
    seg.SetEnd(  pcbnew.VECTOR2I(int(xb), int(yb)))
    seg.SetWidth(mm(width_mm))
    board.Add(seg)

def draw_rect_outline(board, w_mm, h_mm, centered=False, width_mm=0.1):
    W = mm(w_mm); H = mm(h_mm)
    if centered:
        x0, y0 = -W//2, -H//2
        x1, y1 =  W//2,  H//2
    else:
        x0, y0 = 0, 0
        x1, y1 = W, H
    add_edge_seg(board, x0,y0, x1,y0, width_mm)  # bottom
    add_edge_seg(board, x1,y0, x1,y1, width_mm)  # right
    add_edge_seg(board, x1,y1, x0,y1, width_mm)  # top
    add_edge_seg(board, x0,y1, x0,y0, width_mm)  # left
    return (x0,y0,x1,y1)

def load_footprint(lib, name):
    # Raises if library/name not found
    return pcbnew.FootprintLoad(lib, name)

def get_or_create_mount(board, ref, pos_vec):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        fp = load_footprint(MOUNT_LIB, MOUNT_NAME)
        fp.SetReference(ref)
        board.Add(fp)
    fp.SetPosition(pos_vec)
    fp.SetOrientationDegrees(0)
    if LOCK_PLACED:
        fp.SetLocked(True)
    return fp

def place_mounts_at_corners(board, inset_mm):
    bbox = board.GetBoardEdgesBoundingBox()
    if not bbox or bbox.GetWidth() == 0 or bbox.GetHeight() == 0:
        raise RuntimeError("No Edge.Cuts outline found (cannot compute corners). Create outline first.")

    inset = mm(inset_mm)
    # KiCad bbox: origin at top-left logically; use getters for clarity
    xL, yT = bbox.GetX(),       bbox.GetY()
    xR, yB = bbox.GetRight(),   bbox.GetBottom()

    # Inset from edges to hole centers
    TL = pcbnew.VECTOR2I(int(xL + inset), int(yT + inset))
    TR = pcbnew.VECTOR2I(int(xR - inset), int(yT + inset))
    BR = pcbnew.VECTOR2I(int(xR - inset), int(yB - inset))
    BL = pcbnew.VECTOR2I(int(xL + inset), int(yB - inset))

    corners = [TL, TR, BR, BL]  # MH1..MH4 clockwise from top-left
    for idx, vec in enumerate(corners, start=1):
        get_or_create_mount(board, f"{REF_PREFIX}{idx}", vec)

# -------------------- Run the combined flow ---------------------
if CLEAR_OLD_EDGES:
    clear_edge_cuts(brd)

draw_rect_outline(
    brd,
    w_mm=BOARD_W_MM,
    h_mm=BOARD_H_MM,
    centered=CENTER_AT_ORIGIN,
    width_mm=EDGE_WIDTH_MM
)

place_mounts_at_corners(brd, inset_mm=INSET_MM)

pcbnew.Refresh()
try:
    pcbnew.SaveBoard(brd.GetFileName(), brd)
    print(f"Saved board: {brd.GetFileName()}")
except Exception as e:
    print("Board not saved automatically (you can Save manually). Reason:", e)

print(f"Done: Outline {BOARD_W_MM} x {BOARD_H_MM} mm "
      f"(centered={CENTER_AT_ORIGIN}) + four {MOUNT_LIB}:{MOUNT_NAME} at {INSET_MM} mm inset. Locked={LOCK_PLACED}")
