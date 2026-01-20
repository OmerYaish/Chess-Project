import os, shutil, subprocess, csv, random, time, glob, re

# ========= CONFIG =========
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
BLEND_FILE = "chess-set.blend"
BLENDER_SCRIPT = "chess_position_api_v2.py"

STAGING_RENDERS_DIR = r"C:\renders"

OUT_ROOT = "synthetic_from_pgn"    # <<< OUTPUT DATASET
FENS_FILE = r"G:\My Drive\chess_data\pgn_fens.txt"  # <<< CHANGE THIS

NUM_GAMES = 1
POSITIONS_PER_GAME = 120
RESOLUTION = 768
SAMPLES = 16

VIEWS_PER_FEN_OPTIONS = [2, 3]
VIEW_OPTIONS = ["white", "black"]
SEED = 42
CLEAN_STAGING_EACH_TIME = True
ENFORCE_GLOBAL_VIEW_BALANCE = True
# =========================

rng = random.Random(SEED)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def next_game_index(out_root):
    ensure_dir(out_root)
    existing = glob.glob(os.path.join(out_root, "game_*"))
    ids = []
    for p in existing:
        m = re.search(r"game_(\d{4})$", os.path.basename(p))
        if m:
            ids.append(int(m.group(1)))
    return (max(ids) + 1) if ids else 0

def clean_staging():
    ensure_dir(STAGING_RENDERS_DIR)
    for f in os.listdir(STAGING_RENDERS_DIR):
        p = os.path.join(STAGING_RENDERS_DIR, f)
        if os.path.isfile(p) and f.lower().endswith(".png"):
            os.remove(p)

def run_blender_render(fen: str, view: str):
    cmd = [
        BLENDER,
        BLEND_FILE,
        "--background",
        "--python", BLENDER_SCRIPT,
        "--",
        "--fen", fen,
        "--view", view,
        "--resolution", str(RESOLUTION),
        "--samples", str(SAMPLES),
    ]
    subprocess.run(cmd, check=True)

def wait_for_outputs(timeout_sec=120):
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        files = os.listdir(STAGING_RENDERS_DIR)
        if "1_overhead.png" in files:
            p2 = sorted([f for f in files if f.startswith("2_")])
            p3 = sorted([f for f in files if f.startswith("3_")])
            if p2 and p3:
                return [
                    os.path.join(STAGING_RENDERS_DIR, "1_overhead.png"),
                    os.path.join(STAGING_RENDERS_DIR, p2[0]),
                    os.path.join(STAGING_RENDERS_DIR, p3[0]),
                ]
        time.sleep(0.25)
    raise RuntimeError("Timeout waiting for Blender renders")

def choose_view(rem_white, rem_black):
    if not ENFORCE_GLOBAL_VIEW_BALANCE:
        return rng.choice(VIEW_OPTIONS)
    if rem_white <= 0:
        return "black"
    if rem_black <= 0:
        return "white"
    return rng.choice(VIEW_OPTIONS)

def load_fens(path):
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip().split()[0] for l in f if l.strip()]

def main():
    ensure_dir(OUT_ROOT)
    fens = load_fens(FENS_FILE)
    print("Loaded FENs:", len(fens))

    rem_white = NUM_GAMES // 2
    rem_black = NUM_GAMES - rem_white

    fen_cursor = 0
    start_g = next_game_index(OUT_ROOT)

    for g in range(start_g, start_g + NUM_GAMES):
        game_dir = os.path.join(OUT_ROOT, f"game_{g:04d}")
        images_dir = os.path.join(game_dir, "images")
        ensure_dir(images_dir)

        view = choose_view(rem_white, rem_black)
        if ENFORCE_GLOBAL_VIEW_BALANCE:
            if view == "white": rem_white -= 1
            else: rem_black -= 1

        views_per_fen = rng.choice(VIEWS_PER_FEN_OPTIONS)
        rows = []
        frame_idx = 0

        print(f"[Game {g:04d}] view={view}, positions={POSITIONS_PER_GAME}")

        for _ in range(POSITIONS_PER_GAME):
            fen = fens[fen_cursor % len(fens)]
            fen_cursor += 1

            if CLEAN_STAGING_EACH_TIME:
                clean_staging()

            run_blender_render(fen, view=view)
            render_paths = wait_for_outputs()

            selected = render_paths if views_per_fen == 3 else rng.sample(render_paths, k=2)

            for rp in selected:
                dst = os.path.join(images_dir, f"frame_{frame_idx:06d}.png")
                shutil.move(rp, dst)
                rows.append((frame_idx, frame_idx, fen))
                frame_idx += 1

            if views_per_fen == 2:
                for rp in render_paths:
                    if os.path.exists(rp):
                        os.remove(rp)

        with open(os.path.join(game_dir, "game.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["from_frame", "to_frame", "fen"])
            w.writerows(rows)

        print(f"[OK] {game_dir} frames={frame_idx}")

    print("DONE:", os.path.abspath(OUT_ROOT))

if __name__ == "__main__":
    main()
