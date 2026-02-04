# Synthetic-to-Real Generalization for Chessboard square and board-state Classification

This repository contains the full pipeline for **synthetic data generation**, **model training**, and **model inference** for chessboard square and board-state classification.  
This README explains **exactly how to run each component**.

---

## Project Structure

```
project_root/
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

## Environment & Dependencies (Reproducibility)

This project was developed and tested using the following environment:

- Python version: **3.9.21**
- Python environment: **venv**
- Platform: Linux (University GPU server)
- GPU: NVIDIA GeForce GTX 1080
- PyTorch: 2.7.1 with CUDA 11.8

The Python environment used during development was activated using:
```bash
source ~/venvs/dl/bin/activate

### Required Python Packages

All required Python packages are explicitly installed inside the notebooks using `pip install` cells.  
For clarity and reproducibility, the complete list of required packages is provided below.

Core dependencies:
- torch (tested with version 2.7.1 + CUDA 11.8)
- torchvision
- numpy
- pandas
- scikit-learn
- matplotlib
- tqdm
- pillow
- opencv-python
- albumentations (2.0.8)
- chess (1.11.2)

Jupyter environment packages:
- jupyter
- notebook
- ipykernel
- jupyterlab

Manual installation (optional):
```bash
pip install torch torchvision numpy pandas scikit-learn matplotlib tqdm pillow opencv-python albumentations chess jupyter notebook ipykernel jupyterlab
```

---

## 1. Synthetic Dataset Generation (Local / VS Code)

This step generates **synthetic chessboard images and labels** used for training.

### Requirements
- Python 3.9.21
- venv environment activated
- Blender installed locally

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
- Python 3.9.21
- venv (activated via `source ~/venvs/dl/bin/activate`)
- NVIDIA GeForce GTX 1080
- PyTorch 2.7.1 + CUDA 11.8

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
                 ├── high_res_data                   # Synthetic generated games
                      ├── game_0000
                      ├── game_0001
                      └── ...
            ├─── synthetic_from_pgn                  # Synthetic generated images from the given pgn images
                 ├── game_0000
                 └── game_0001
            ├─── real                                # Real images
                 ├── game2_per_frame
                 ├── game4_per_frame
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
