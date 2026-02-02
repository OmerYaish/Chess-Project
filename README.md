# Synthetic-to-Real Generalization for Chessboard square and board-state Classification

This repository contains the full pipeline for **synthetic data generation**, **model training**, and **model inference** for chessboard square and board-state classification.  
This README explains **exactly how to run each component**.

---

## Project Structure

```
project_root/
│
├── DataGeneration                         
    ├──── chess_position_api_v2.py
    ├──── chess-set.blender (blender)   
    ├──── generate_dataset.py                            # Synthetic data generation script
    ├──── generate_csv_files.py                          # submission format adapter
    ├──── generate_synthetic_from_pgn.py                 # Synthetic data generation script from the given pgn images
├──── requirements.txt
├── training_notebook.ipynb                              # Training notebook (GPU required)
├── Final_model.ipynb                                    # Inference notebook (Colab)
├── best_train.pt (attached to releases)                 # Trained model checkpoint
└── README.md                                            # This file
```

---

## 1. Synthetic Dataset Generation (Local / VS Code)

This step generates **synthetic chessboard images and labels** used for training.

### Requirements
- Python 3.8+
- Required Python packages installed
- Local machine or any environment with Python support

### Steps

1. Open the project folder in **VS Code** (or any IDE).
2. Open a **terminal** in the project root directory.
3. Run:

```bash
python generate_dataset.py
```

4. The script will:
   - Generate synthetic chessboard images
   - Save images and labels to the configured output directories

---

## 2. Model Training (Jupyter Notebook + GPU)

Training is performed using a Jupyter Notebook and **requires GPU acceleration**.

### Environment
- University GPU server
- Python environment with PyTorch + CUDA
- Jupyter Notebook / JupyterLab

### Steps

1. Connect to the (university) GPU server.
2. Activate the appropriate Python environment.
3. Launch Jupyter:

```bash
jupyter notebook
```
OR:

```bash
source ~/venvs/dl/bin/activate
jupyter lab --no-browser --ip=127.0.0.1 --port=8888 \
  --ServerApp.certfile= \
  --ServerApp.keyfile=
```

4. Open:

```
training_notebook.ipynb
```

5. Verify the notebook is connected to a **GPU kernel**.
6. Upload the chess_data folder to the same directory where the .ipynb file is located, using the following structure:
   ```
        ├── chess_data                         
            ├─── highres_main                        
                 ├─── high_res_data                # Synthetic generated games
                      ├── game_0000
                      ├── game_0001
                      └── ...
            ├─── synthetic_from_pgn                  # Synthetic generated images from the given pgn images
                 ├── game_0000
                 ├── game_0001
                 └── ...
            ├─── real                                # Real images
                 ├── game0_per_frame
                 ├── game1_per_frame
                 └── ...
   ```
   Upload the folders from Drive that end with **"format1"**.
7. Run all cells **from top to bottom**.

### Output

The training process saves the best-performing models:

- `best.pt` (of exp A)
- `best.pt` (of exp B)
- `best_acc.pt` (of Exp C)
- `best_f1.pt` (of exp C)
These files are required for the inference stage.

---

## 3. Model Inference (Google Colab)

Inference is performed using **Google Colab**.

### Steps

1. Open **Google Colab**.
2. Upload and open:

```
Final_model.ipynb
```

3. Run all cells **from top to bottom**.

### File Upload Cell

Upload:
- `best_train.pt` model file - attached to the github releases. (you can use other .pt file as well however the attached one gives the best results)
- One or more chessboard images for testing

### Output

- The required tensor
- Folder "results" with the predicted board image (the model output)
  
This notebook is **ready to run** and requires no code changes.

---

## Contact
For questions regarding setup or execution, refer to the project report or contact the project author:
**Maayan Sameach** &
**Omer Yaish**
