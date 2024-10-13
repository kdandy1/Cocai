serve-all:
    tmuxinator start -p tmuxinator.yaml
serve:
    # This is for development. For production, use `serve-all`, which uses command in `tmuxinator.yaml`.
    uv run uvicorn server:app --reload
run:
    uv run main.py
format:
    uv run ruff format
