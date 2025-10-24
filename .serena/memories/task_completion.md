# Task Completion Checklist
- Run targeted smoke tests if you touched inference logic (e.g., `python GPT_SoVITS/inference_cli.py --text "test" --ref_audio sample.wav`).
- For UI/API changes, launch `python app/webui.py` or `python api/api.py` locally to confirm startup without runtime errors.
- Verify new scripts handle missing assets gracefully and emit clear messages for required pretrained models.
- Keep dependencies updated in `requirements.txt` if new packages are required; confirm Docker image still builds (`docker-compose build`).
- Document new environment variables or configuration knobs in comments or README-equivalent sections when applicable.