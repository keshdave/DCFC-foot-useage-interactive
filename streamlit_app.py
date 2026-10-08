from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

COLORS = {
    "SUCCESS": "#17824b",
    "FAIL": "#d64b4b",
    "NEUTRAL": "#e2a93b",
    "NO RESULT": "#9aa3ad",
}
BODY_PART_ORDER = ["FOOT_RIGHT", "FOOT_LEFT", "BODY", "UNKNOWN"]
DISTANCE_ORDER = [
    "LESS_THAN_ONE_METER",
    "ONE_METER",
    "TWO_METERS",
    "THREE_METERS",
    "FOUR_METERS",
    "MORE_THAN_FOUR_METERS",
]

def readable(value):
    return str(value).replace("_", " ").lower()

@st.cache_data
def load_data():
    data = pd.read_csv(Path(__file__).with_name("dcfc_indy_eventdata.csv"), low_memory=False)
    data = data[data["team_name"].eq("Detroit City FC")].copy()
    data["pressure"] = pd.to_numeric(data["pressure"], errors="coerce")
    data["body_part_extended"] = data["body_part_extended"].fillna("UNKNOWN")
    data["result"] = data["result"].fillna("NO RESULT")
    return data

def make_chart(events, player):
    counts = events.groupby(["body_part_extended", "result"]).size().reset_index(name="events")
    counts["total"] = counts.groupby("body_part_extended")["events"].transform("sum")
    counts["percentage"] = counts["events"].div(counts["total"]).mul(100)
    counts["body_part"] = counts["body_part_extended"].map(readable)
    counts["result_name"] = counts["result"].map(readable)
    extra_parts = [part for part in counts["body_part_extended"].unique() if part not in BODY_PART_ORDER]
    body_parts = [readable(part) for part in BODY_PART_ORDER + extra_parts]
    results = ["SUCCESS", "FAIL", "NEUTRAL", "NO RESULT"]
    results += [result for result in counts["result"].unique() if result not in results]
    result_labels = [readable(result) for result in results]
    chart = px.bar(
        counts,
        x="body_part",
        y="events",
        color="result_name",
        category_orders={"body_part": body_parts, "result_name": result_labels},
        color_discrete_map={readable(result): COLORS.get(result, "#64748b") for result in results},
        custom_data=["total", "percentage", "result_name"],
        labels={"body_part": "Body part", "events": "Events", "result_name": "Result"},
        title=f"{player}: usage by body part",
    )
    chart.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{customdata[2]}: %{y}/%{customdata[0]}<br>"
            "Share: %{customdata[1]:.1f}%<extra></extra>"
        )
    )
    chart.update_layout(barmode="stack", hovermode="closest", margin={"l": 20, "r": 20, "t": 70, "b": 20})
    return chart

def show_player(data, player, pressure, distance, include_missing):
    events = data[data["player_name"].eq(player)]
    pressure_filter = events["pressure"].between(*pressure)
    if include_missing:
        pressure_filter |= events["pressure"].isna()
    distance_filter = events["distance_to_opponent"].eq(distance) if distance != "All distances" else True
    events = events[pressure_filter & distance_filter]
    st.subheader(player)
    if events.empty:
        st.warning("No events match these filters.")
        return
    success = events["result"].eq("SUCCESS").sum()
    resolved = events["result"].isin(["SUCCESS", "FAIL"]).sum()
    success_rate = success / resolved * 100 if resolved else 0

    one, two, three = st.columns(3)
    one.metric("Events", f"{len(events):,}")
    two.metric("Successes", f"{success:,}")
    three.metric("Success rate", f"{success_rate:.1f}%")
    st.plotly_chart(make_chart(events, player), width="stretch")

def main():
    st.set_page_config(page_title="DCFC Player Comparison", page_icon="⚽", layout="wide")
    data = load_data()
    players = sorted(data["player_name"].dropna().unique())

    st.title("Detroit City FC player comparison")
    st.caption("Compare body-part usage under the same pressure filters.")
    with st.sidebar:
        st.header("Filters")
        pressure = st.slider("Pressure range", 0.0, 100.0, (0.0, 100.0), 1.0)
        distances = ["All distances"] + DISTANCE_ORDER
        distance = st.selectbox(
            "Distance to opponent", distances, format_func=readable, key="distance_filter"
        )
        include_missing = st.checkbox("Include missing pressure", False)
    left, right = st.columns(2)
    with left:
        player_one = st.selectbox("First player", players, key="player_one")
        show_player(data, player_one, pressure, distance, include_missing)
    with right:
        player_two = st.selectbox(
            "Second player", players, index=min(1, len(players) - 1), key="player_two"
        )
        show_player(data, player_two, pressure, distance, include_missing)

if __name__ == "__main__":
    main()