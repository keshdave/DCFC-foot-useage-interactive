# Detroit City FC player usage

An interactive Streamlit dashboard for exploring Detroit City FC event usage by player, body part, result, and pressure range.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dcfc-foot-useage.streamlit.app/)

### Run locally

Prerequisite: install `uv` if you don't already have it.

```
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

1. Sync the dependencies:

   ```
   $ uv sync
   ```

2. Run the app

   ```
   $ uv run streamlit run streamlit_app.py
   ```

If you are using a regular Python environment instead of `uv`, install the dependencies first:

```
$ python -m pip install -r requirements.txt
$ streamlit run streamlit_app.py
```

Use the sidebar to select a player and pressure range. Hover over any stacked bar segment to see its event count and percentage of that body part.
