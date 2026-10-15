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
BODY_PARTS = ["FOOT_RIGHT", "FOOT_LEFT", "BODY", "UNKNOWN"]
DISTANCES = [
    "LESS_THAN_ONE_METER", "ONE_METER", "TWO_METERS",
    "THREE_METERS", "FOUR_METERS", "MORE_THAN_FOUR_METERS",]

def readable(value):
    return str(value).replace("_", " ").lower()

@st.cache_data
def load_data():
    data = pd.read_csv(Path(__file__).with_name("dcfc_indy_eventdata.csv"), low_memory=False)
    data = data[data["team_name"].eq("Detroit City FC")].copy()
    data["pressure"] = pd.to_numeric(data["pressure"], errors="coerce")
    for column in ["body_part_extended", "result", "action_type"]:
        data[column] = data[column].fillna("UNKNOWN" if column != "result" else "NO RESULT")
    return data

def make_result_chart(events, player):
    counts = events.groupby(["body_part_extended", "result"]).size().reset_index(name="events")
    counts["total"] = counts.groupby("body_part_extended")["events"].transform("sum")
    counts["percentage"] = counts["events"].div(counts["total"]).mul(100)
    counts["body_part"] = counts["body_part_extended"].map(readable)
    counts["result_name"] = counts["result"].map(readable)

    extra_parts = [part for part in counts["body_part_extended"].unique() if part not in BODY_PARTS]
    body_parts = [readable(part) for part in BODY_PARTS + extra_parts]
    results = ["SUCCESS", "FAIL", "NEUTRAL", "NO RESULT"]
    results += [value for value in counts["result"].unique() if value not in results]

    chart = px.bar(
        counts,
        x="body_part",
        y="events",
        color="result_name",
        category_orders={"body_part": body_parts, "result_name": [readable(value) for value in results]},
        color_discrete_map={readable(value): COLORS.get(value, "#64748b") for value in results},
        custom_data=["total", "percentage", "result_name"],
        labels={"body_part": "Body part", "events": "Events", "result_name": "Result"},
        title=f"{player}: usage by body part",)
    chart.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "%{customdata[2]}: %{y}/%{customdata[0]}<br>"
            "Share: %{customdata[1]:.1f}%<extra></extra>"))
    totals = events["body_part_extended"].value_counts()
    successes = events[events["result"].eq("SUCCESS")]["body_part_extended"].value_counts()
    success_rates = successes.reindex(totals.index, fill_value=0).div(totals).mul(100)
    for part, rate in success_rates.items():
        chart.add_annotation(
            x=readable(part), y=totals[part], text=f"success: {rate:.1f}%",
            showarrow=False, yshift=10, font={"size": 11, "color": COLORS["SUCCESS"]})
    chart.update_layout(barmode="stack", hovermode="closest", margin={"l": 20, "r": 20, "t": 70, "b": 20})
    return chart

def show_action_pies(events, player):
    parts = [part for part in BODY_PARTS if part in events["body_part_extended"].unique()]
    parts += [part for part in events["body_part_extended"].unique() if part not in parts]
    actions = sorted(events["action_type"].unique())
    palette = px.colors.sequential.Blues[2:]
    colors = {readable(action): palette[i % len(palette)] for i, action in enumerate(actions)}
    legend = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:6px;">'
        f'<span style="color:{color};font-size:18px;">■</span>{readable(action)}</span>'
        for action, color in colors.items())
    st.write(f"**{player}: actions by body part**")
    st.markdown(
        f'<div style="display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center;">'
        f'<strong>Action types:</strong>{legend}</div>',
        unsafe_allow_html=True,)

    columns = st.columns(len(parts))
    for column, part in zip(columns, parts):
        counts = (
            events[events["body_part_extended"].eq(part)]["action_type"]
            .value_counts()
            .rename_axis("action")
            .reset_index(name="events"))
        counts["action"] = counts["action"].map(readable)
        chart = px.pie(
            counts,
            values="events",
            names="action",
            color="action",
            color_discrete_map=colors,
            title=readable(part),)
        chart.update_layout(showlegend=False)
        chart.update_traces(hovertemplate="%{label}: %{value} (%{percent})<extra></extra>")
        column.plotly_chart(chart, width="stretch")

def show_player(data, player, pressure, distance, include_missing):
    events = data[data["player_name"].eq(player)]
    pressure_filter = events["pressure"].between(*pressure)
    if include_missing:
        pressure_filter |= events["pressure"].isna()
    if distance != "All distances":
        pressure_filter &= events["distance_to_opponent"].eq(distance)
    events = events[pressure_filter]

    st.subheader(player)
    if events.empty:
        st.warning("No events match these filters.")
        return

    success = events["result"].eq("SUCCESS").sum()
    resolved = events["result"].isin(["SUCCESS", "FAIL"]).sum()
    one, two, three = st.columns(3)
    one.metric("Events", f"{len(events):,}")
    two.metric("Successes", f"{success:,}")
    three.metric("Success rate", f"{success / resolved * 100 if resolved else 0:.1f}%")

    st.plotly_chart(make_result_chart(events, player), width="stretch")
    show_action_pies(events, player)

def main():
    st.set_page_config(page_title="DCFC Player Comparison", page_icon="⚽", layout="wide")
    data = load_data()
    players = sorted(data["player_name"].dropna().unique())

    st.title("Detroit City FC player comparison")
    st.caption("Compare body-part usage under the same pressure filters.")
    with st.sidebar:
        st.header("Filters")
        pressure = st.slider("Pressure range", 0.0, 100.0, (0.0, 100.0), 1.0)
        distance = st.selectbox(
            "Distance to opponent",
            ["All distances"] + DISTANCES,
            format_func=readable,
            key="distance_filter",)
        include_missing = st.checkbox("Include missing pressure")
        compare = st.checkbox("Compare a second player")
        player_one = st.selectbox("Player", players, key="player_one")
        player_two = st.selectbox(
            "Second player", players, index=min(1, len(players) - 1), key="player_two"
        ) if compare else None

    if compare:
        left, right = st.columns(2)
        with left:
            show_player(data, player_one, pressure, distance, include_missing)
        with right:
            show_player(data, player_two, pressure, distance, include_missing)
    else:
        show_player(data, player_one, pressure, distance, include_missing)

if __name__ == "__main__":
    main()
