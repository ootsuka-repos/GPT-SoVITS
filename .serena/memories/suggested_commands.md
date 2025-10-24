# Suggested Commands
- Launch main WebUI: `python app/webui.py`
- Run FastAPI inference server: `python api/api.py`
- Standalone inference UIs: `python GPT_SoVITS/inference_webui.py` or `python GPT_SoVITS/inference_gui.py`
- Command-line inference: `python GPT_SoVITS/inference_cli.py --text "..." --ref_audio path`
- Training stage 1 / 2: `python GPT_SoVITS/s1_train.py` and `python GPT_SoVITS/s2_train.py`
- Docker workflow: `docker-compose up --build` (exposes ports 9871-9874, 9880)
- Dataset prep helpers: run scripts under `GPT_SoVITS/prepare_datasets/` via `python -s <script>` (WebUI orchestrates automatically)
- Use `rg`, `find`, `python3` for local development on macOS (Darwin host)
- Install deps locally: `pip install -r requirements.txt` (after ensuring `python3.11` and CUDA toolkits if needed)