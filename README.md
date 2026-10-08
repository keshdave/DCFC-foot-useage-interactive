# Detroit City FC player comparison

An interactive Streamlit dashboard for comparing Detroit City FC players by body-part usage, event result, pressure, and distance to the opponent.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dcfc-foot-useage.streamlit.app/)

------------------------------------------------

### Dashboard features

- Compare two players using separate bar charts shown side by side.
- Use the shared `Pressure range` slider to filter events from 0 to 100.
- Use the `Distance to opponent` filter to choose all distances or a specific distance category:
   - Less than one meter
   - One meter
   - Two meters
   - Three meters
   - Four meters
   - More than four meters
- Include events with missing pressure values when needed.
- View events, successes, and success rate for each selected player.
- Compare stacked results by body part, ordered as foot right, foot left, body, and unknown.
- Hover over any bar segment to see the result count out of the body-part total, such as `success: 10/30`, along with its percentage.

Both player charts use the same pressure and distance filters, making their results easier to compare.

-------------------------------------------

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