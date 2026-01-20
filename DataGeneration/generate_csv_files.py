import os
import pandas as pd
import glob

source_root = r"./synthetic_dataset" 

def generate_gt_csv_in_place():
    game_folders = glob.glob(os.path.join(source_root, "game_*"))
    print(f"Found {len(game_folders)} games. Generating gt.csv files...")
    for game_folder in game_folders:
        game_name = os.path.basename(game_folder)
        old_csv_path = os.path.join(game_folder, "game.csv")
        images_dir = os.path.join(game_folder, "images")
        new_csv_path = os.path.join(game_folder, "gt.csv")
        if not os.path.exists(old_csv_path):
            print(f"Skipping {game_name}: game.csv not found.")
            continue          
        if not os.path.exists(images_dir):
            print(f"Skipping {game_name}: images folder not found.")
            continue
        try:
            df = pd.read_csv(old_csv_path)
        except Exception as e:
            print(f"Error reading CSV for {game_name}: {e}")
            continue
        new_rows = []
        viewpoint = "white"
        if "black" in game_name.lower():
            viewpoint = "black"
        for index, row in df.iterrows():
            try:
                frame_number = int(row.iloc[0])
                raw_fen = str(row.iloc[-1])
                fen_parts = raw_fen.strip().split(' ', 1)
                if len(fen_parts) > 1 and fen_parts[0].isdigit():
                     clean_fen = fen_parts[1]
                else:
                    clean_fen = raw_fen
                pattern = os.path.join(images_dir, f"*{frame_number}.*") 
                matches = glob.glob(pattern)
                image_matches = [m for m in matches if m.lower().endswith(('.png', '.jpg', '.jpeg'))]
                if image_matches:
                    full_path = image_matches[0]
                    actual_filename = os.path.basename(full_path)  
                    new_rows.append({
                        "image_name": actual_filename, 
                        "fen": clean_fen,
                        "viewpoint": viewpoint
                    })
            except Exception as e:
                pass
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            new_df = new_df[["image_name", "fen", "viewpoint"]]            
            new_df.to_csv(new_csv_path, index=False)
            print(f"Generated gt.csv for {game_name} ({len(new_df)} rows)")
        else:
            print(f"No valid rows generated for {game_name}")
    print("Done.")
if __name__ == "__main__":
    generate_gt_csv_in_place()