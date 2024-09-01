serve:
    @PYTHONPATH=. uv run chainlit run main.py -w
run:
    @PYTHONPATH=. uv run main.py
format:
    uv run ruff format