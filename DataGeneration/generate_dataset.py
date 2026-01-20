# #& "C:\Program Files\Blender Foundation\Blender 5.0\5.0\python\bin\python.exe" generate_dataset.py
# import os, shutil, subprocess, csv, random, time
# import chess

# # ========= CONFIG (edit if needed) =========
# BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
# BLEND_FILE = "chess-set.blend"
# BLENDER_SCRIPT = "chess_position_api_v2.py"

# # Blender currently saves here (from your log):
# STAGING_RENDERS_DIR = r"C:\renders"
# # Output dataset (created next to this script)
# OUT_ROOT = "synthetic_dataset"

# NUM_GAMES = 50            # start with 50; later increase to 200-1000
# PLIES_PER_GAME = 60       # positions per game (half-moves)
# VIEWS_PER_FEN = 3         # your script outputs 3 images per fen
# VIEW = "black"
# RESOLUTION = 1024
# SAMPLES = 64              # increase later for quality (128), decrease for speed (32)
# SEED = 42

# # Safety: stop if staging dir contains unexpected stuff
# CLEAN_STAGING_EACH_TIME = True
# # ===========================================

# random.seed(SEED)

# def ensure_dir(path):
#     os.makedirs(path, exist_ok=True)

# def clean_staging():
#     ensure_dir(STAGING_RENDERS_DIR)
#     for f in os.listdir(STAGING_RENDERS_DIR):
#         p = os.path.join(STAGING_RENDERS_DIR, f)
#         if os.path.isfile(p) and f.lower().endswith((".png", ".jpg", ".jpeg")):
#             os.remove(p)

# def run_blender_render(fen: str):
#     # Call blender headless
#     cmd = [
#         BLENDER,
#         BLEND_FILE,
#         "--background",
#         "--python", BLENDER_SCRIPT,
#         "--",
#         "--fen", fen,
#         "--view", VIEW,
#         "--resolution", str(RESOLUTION),
#         "--samples", str(SAMPLES),
#     ]
#     subprocess.run(cmd, check=True)

# def wait_for_outputs(timeout_sec=120):
#     # Wait for the three expected files to appear
#     expected = ["1_overhead.png", "2_west.png", "3_east.png"]
#     t0 = time.time()
#     while time.time() - t0 < timeout_sec:
#         present = set(os.listdir(STAGING_RENDERS_DIR))
#         if all(e in present for e in expected):
#             return [os.path.join(STAGING_RENDERS_DIR, e) for e in expected]
#         time.sleep(0.25)
#     raise RuntimeError(f"Timeout waiting for renders in {STAGING_RENDERS_DIR}. Found: {os.listdir(STAGING_RENDERS_DIR)[:20]}")

# def main():
#     print(f"DEBUG: I am saving files to: {os.path.abspath(OUT_ROOT)}")
#     ensure_dir(OUT_ROOT)

#     for g in range(NUM_GAMES):
#         game_dir = os.path.join(OUT_ROOT, f"game_{g:04d}")
#         images_dir = os.path.join(game_dir, "images")
#         ensure_dir(images_dir)

#         board = chess.Board()
#         rows = []
#         frame_idx = 0

#         for ply in range(PLIES_PER_GAME):
#             fen_board = board.fen().split()[0]

#             if CLEAN_STAGING_EACH_TIME:
#                 clean_staging()

#             run_blender_render(fen_board)
#             render_paths = wait_for_outputs()

#             # Move 3 views into images/ as 3 separate frames (more data)
#             for rp in render_paths:
#                 dst = os.path.join(images_dir, f"frame_{frame_idx:06d}.png")
#                 shutil.move(rp, dst)

#                 print(f"MOVED TO: {os.path.abspath(dst)}")

#                 rows.append((frame_idx, frame_idx, fen_board))
#                 frame_idx += 1

#             # advance to next position
#             if board.is_game_over():
#                 board.reset()
#             legal = list(board.legal_moves)
#             board.push(random.choice(legal))

#         # write game.csv
#         csv_path = os.path.join(game_dir, "game.csv")
#         with open(csv_path, "w", newline="", encoding="utf-8") as f:
#             w = csv.writer(f)
#             w.writerow(["from_frame", "to_frame", "fen"])
#             w.writerows(rows)

#         print(f"[OK] {game_dir} frames={frame_idx}")

#     print("\nDONE.")
#     print(f"Dataset root: {os.path.abspath(OUT_ROOT)}")

# if __name__ == "__main__":
#     main()


import os, shutil, subprocess, csv, random, time
import chess
import re, glob

def next_game_index(out_root):
    os.makedirs(out_root, exist_ok=True)
    existing = glob.glob(os.path.join(out_root, "game_*"))
    ids = []
    for p in existing:
        m = re.search(r"game_(\d{4})$", os.path.basename(p))
        if m:
            ids.append(int(m.group(1)))
    return (max(ids) + 1) if ids else 0

# ========= CONFIG (edit if needed) =========
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
BLEND_FILE = "chess-set.blend"
BLENDER_SCRIPT = "chess_position_api_v2.py"

# Blender currently saves here (from your log):
STAGING_RENDERS_DIR = r"C:\renders"

# Output dataset (created next to this script)
OUT_ROOT = "synthetic_dataset"

NUM_GAMES = 50       # start with 10; later increase to 200-1000
RESOLUTION = 1024
SAMPLES = 16              # increase later for quality (128), decrease for speed (8/16)

SEED = 42                 # set None for full randomness
CLEAN_STAGING_EACH_TIME = True
# ===========================================

# --- Randomization knobs (per game) ---
PLIES_OPTIONS = [40, 50, 60]
VIEWS_PER_FEN_OPTIONS = [3]
VIEW_OPTIONS = ["white", "black"]

# If you want guaranteed ~50/50 over the whole dataset, set this True
ENFORCE_GLOBAL_VIEW_BALANCE = True

rng = random.Random(SEED) if SEED is not None else random.Random()

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def clean_staging():
    ensure_dir(STAGING_RENDERS_DIR)
    for f in os.listdir(STAGING_RENDERS_DIR):
        p = os.path.join(STAGING_RENDERS_DIR, f)
        if os.path.isfile(p) and f.lower().endswith((".png", ".jpg", ".jpeg")):
            os.remove(p)

def run_blender_render(fen: str, view: str):
    # Call blender headless
    cmd = [
        BLENDER,
        BLEND_FILE,
        "--background",
        "--python", BLENDER_SCRIPT,
        "--",
        "--fen", fen,
        "--view", view,  # <-- pass per-render view
        "--resolution", str(RESOLUTION),
        "--samples", str(SAMPLES),
    ]
    subprocess.run(cmd, check=True)

def wait_for_outputs(timeout_sec=120):
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        present = set(os.listdir(STAGING_RENDERS_DIR))
        if "1_overhead.png" in present:
            p2 = [f for f in present if f.startswith("2_") and f.lower().endswith(".png")]
            p3 = [f for f in present if f.startswith("3_") and f.lower().endswith(".png")]
            if p2 and p3:
                # pick the first found deterministically
                p2 = sorted(p2)[0]
                p3 = sorted(p3)[0]
                return [
                    os.path.join(STAGING_RENDERS_DIR, "1_overhead.png"),
                    os.path.join(STAGING_RENDERS_DIR, p2),
                    os.path.join(STAGING_RENDERS_DIR, p3),
                ]
        time.sleep(0.25)

    raise RuntimeError(
        f"Timeout waiting for renders in {STAGING_RENDERS_DIR}. "
        f"Found: {os.listdir(STAGING_RENDERS_DIR)[:20]}"
    )

def choose_view(game_idx: int, remaining_white: int, remaining_black: int) -> str:
    """
    Choose view for this game.
    If ENFORCE_GLOBAL_VIEW_BALANCE=True, ensures exact balance over NUM_GAMES.
    """
    if not ENFORCE_GLOBAL_VIEW_BALANCE:
        return rng.choice(VIEW_OPTIONS)

    # If one side is exhausted, take the other
    if remaining_white <= 0:
        return "black"
    if remaining_black <= 0:
        return "white"

    # Otherwise random choice
    return rng.choice(VIEW_OPTIONS)

def main():
    ensure_dir(OUT_ROOT)
    start_g = next_game_index(OUT_ROOT)

    # For exact balancing over this run:
    remaining_white = NUM_GAMES // 2
    remaining_black = NUM_GAMES - remaining_white

    for gi, g in enumerate(range(start_g, start_g + NUM_GAMES)):
        game_dir = os.path.join(OUT_ROOT, f"game_{g:04d}")
        if os.path.exists(game_dir):
            print(f"[SKIP] {game_dir} already exists")
            continue
        images_dir = os.path.join(game_dir, "images")
        ensure_dir(images_dir)

        # --- Randomize per-game settings ---
        view = choose_view(gi, remaining_white, remaining_black)
        if ENFORCE_GLOBAL_VIEW_BALANCE:
            if view == "white":
                remaining_white -= 1
            else:
                remaining_black -= 1

        plies_per_game = rng.choice(PLIES_OPTIONS)
        views_per_fen = rng.choice(VIEWS_PER_FEN_OPTIONS)

        print(
            f"[Game {g:04d}] view={view}, plies={plies_per_game}, views_per_fen={views_per_fen}, "
            f"res={RESOLUTION}, samples={SAMPLES}"
        )

        board = chess.Board()
        rows = []
        frame_idx = 0

        for ply in range(plies_per_game):
            fen_board = board.fen().split()[0]

            # Render once, then select 2 or 3 images from the 3 available angles
            if CLEAN_STAGING_EACH_TIME:
                clean_staging()

            run_blender_render(fen_board, view=view)
            render_paths = wait_for_outputs()

            # Choose subset of views (2 or 3) without changing the Blender script
            # Deterministic w.r.t. seed
            selected = render_paths if views_per_fen == 3 else rng.sample(render_paths, k=2)

            for rp in selected:
                dst = os.path.join(images_dir, f"frame_{frame_idx:06d}.png")
                shutil.move(rp, dst)

                rows.append((frame_idx, frame_idx, fen_board))
                frame_idx += 1

            # Clean leftovers if we selected only 2 (avoid pile-up in staging)
            if views_per_fen == 2:
                for rp in render_paths:
                    if os.path.exists(rp):
                        os.remove(rp)

            # Advance to next position
            if board.is_game_over():
                board.reset()

            legal = list(board.legal_moves)
            board.push(rng.choice(legal))

        # Write game.csv
        csv_path = os.path.join(game_dir, "game.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["from_frame", "to_frame", "fen"])
            w.writerows(rows)

        print(f"[OK] {game_dir} frames={frame_idx}")

    print("\nDONE.")
    print(f"Dataset root: {os.path.abspath(OUT_ROOT)}")

if __name__ == "__main__":
    main()
