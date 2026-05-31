# 🔢 Sudoku App

A Streamlit-based Sudoku game with 6×6, 9×9, and 16×16 grids, auto-generated puzzles, and full gameplay features.

## Features
- **Grid sizes**: 6×6, 9×9, 16×16
- **Difficulties**: Easy, Medium, Hard, Expert
- **Hint system** — reveals one empty cell
- **Timer** — live countdown per session
- **Mistake counter** — validate your board anytime
- **Undo / Redo** — full move history
- **Session state** — progress saved within your browser session

## Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this folder to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **New app** → select your repo
4. Set **Main file path** to `app.py`
5. Click **Deploy** — you'll get a free URL like `yourname-sudoku.streamlit.app`

## Project Structure

```
sudoku_app/
├── app.py          # Main Streamlit UI
├── generator.py    # Puzzle generation for all grid sizes
├── validator.py    # Move validation, mistake counting
├── requirements.txt
└── README.md
```
