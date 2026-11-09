"""
================================================================================
SoundScope – Music Mood, Energy & Popularity Analytics Platform
Interactive Python Streamlit Web Application
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from data_processor import SoundScopeAnalytics, MoodClassifier
from visualizations import Visualizer

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SoundScope | Music Mood & Popularity Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern visual aesthetics and high readability
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetric"]:hover {
        border-color: #1DB954;
        transition: border-color 0.3s ease;
    }
    
    /* Headers & Dividers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
    
    /* Badges */
    .mood-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
    }
    
    /* Interpretations container */
    .insight-box {
        background-color: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #1DB954;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 0.92rem;
        color: #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. DATA INITIALIZATION & CACHING
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_and_preprocess_data(file_source):
    analytics = SoundScopeAnalytics()
    df = analytics.load_data(file_source)
    return df, analytics


# -----------------------------------------------------------------------------
# 3. SIDEBAR: DATASET SOURCE & DYNAMIC FILTERS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🎵 SoundScope")
    st.caption("Music Mood, Energy & Popularity Platform")
    st.markdown("---")

    # Dataset Selection
    st.subheader("📁 Data Source")
    data_option = st.radio(
        "Choose Dataset:",
        options=["Bundled Spotify Sample", "Upload Custom CSV"],
        index=0,
        help="Select between the default pre-loaded Spotify dataset or upload your own 114k tracks CSV."
    )

    df_raw = None
    analytics_engine = SoundScopeAnalytics()

    if data_option == "Bundled Spotify Sample":
        local_csv_path = os.path.join(os.path.dirname(__file__), "spotify_tracks.csv")
        if os.path.exists(local_csv_path):
            df_raw, analytics_engine = load_and_preprocess_data(local_csv_path)
        else:
            st.error("Default `spotify_tracks.csv` not found in workspace.")
            st.stop()
    else:
        uploaded_file = st.file_uploader("Upload Spotify CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df_raw, analytics_engine = load_and_preprocess_data(uploaded_file)
                st.success(f"Loaded {len(df_raw):,} tracks successfully!")
            except Exception as ex:
                st.error(f"Error parsing uploaded file: {ex}")
                st.stop()
        else:
            st.info("Awaiting CSV file upload. Reverting to bundled sample for preview...")
            local_csv_path = os.path.join(os.path.dirname(__file__), "spotify_tracks.csv")
            if os.path.exists(local_csv_path):
                df_raw, analytics_engine = load_and_preprocess_data(local_csv_path)
            else:
                st.stop()

    st.markdown("---")
    st.subheader("🎛️ Interactive Filter Controls")

    # Filter 1: Search Query
    search_query = st.text_input(
        "🔍 Search Track or Artist",
        value="",
        placeholder="e.g. Armin, Big Bank, Xavier...",
        help="Filters the dataset dynamically matching song title or artist name."
    )

    # Filter 2: Mood Categories Multiselect
    all_moods = [
        MoodClassifier.MOOD_HAPPY,
        MoodClassifier.MOOD_INTENSE,
        MoodClassifier.MOOD_CALM,
        MoodClassifier.MOOD_MELANCHOLIC,
        MoodClassifier.MOOD_BALANCED
    ]
    selected_moods = st.multiselect(
        "🎭 Filter by Mood Category",
        options=all_moods,
        default=all_moods,
        help="Categorization derived from Valence and Energy thresholds."
    )

    # Filter 3: Artist Multiselect
    all_artists = sorted(df_raw['artist_name'].dropna().unique().tolist())
    selected_artists = st.multiselect(
        "🎤 Filter by Artist(s)",
        options=all_artists,
        default=[],
        placeholder="All Artists (or pick specific)"
    )

    # Filter 4: Sliders for Numerical Attributes
    st.markdown("##### 🎚️ Audio & Popularity Thresholds")

    min_pop, max_pop = int(df_raw['popularity'].min()), int(df_raw['popularity'].max())
    pop_range = st.slider(
        "Popularity Range",
        min_value=min_pop,
        max_value=max(max_pop, 100),
        value=(min_pop, max_pop),
        step=1
    )

    energy_range = st.slider(
        "Energy Level",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.05
    )

    dance_range = st.slider(
        "Danceability Level",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.05
    )

    # Filter Reset Action
    if st.button("🔄 Reset All Filters", use_container_width=True):
        st.rerun()


# -----------------------------------------------------------------------------
# 4. FILTER EXECUTION & DYNAMIC STATE
# -----------------------------------------------------------------------------
df_filtered = analytics_engine.filter_dataset(
    df=df_raw,
    search_query=search_query,
    selected_moods=selected_moods,
    selected_artists=selected_artists,
    popularity_range=pop_range,
    energy_range=energy_range,
    danceability_range=dance_range
)

kpis = analytics_engine.calculate_kpis(df_filtered)


# -----------------------------------------------------------------------------
# 5. MAIN APPLICATION HEADER & BANNER
# -----------------------------------------------------------------------------
st.title("SoundScope – Music Mood, Energy & Popularity Analytics")
st.markdown(
    "An interactive web analytics platform to explore audio characteristics, mood quadrants, "
    "and popularity patterns across curated tracks."
)

# Top KPI Dashboard Columns (Side-by-side using st.columns)
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)

with kpi_col1:
    st.metric(
        label="Total Tracks",
        value=f"{kpis['total_records']:,}",
        delta=f"{kpis['total_records'] - len(df_raw):,}" if kpis['total_records'] != len(df_raw) else "All Selected"
    )

with kpi_col2:
    st.metric(
        label="Total Duration",
        value=f"{kpis['total_duration_minutes']} min",
        help=f"Sum of duration: ~{kpis['total_duration_hours']} hours."
    )

with kpi_col3:
    st.metric(
        label="Avg Popularity",
        value=f"{kpis['avg_popularity']} / 100",
        help="Mean popularity score across currently filtered songs."
    )

with kpi_col4:
    st.metric(
        label="Avg Energy",
        value=f"{kpis['avg_energy']}",
        help="Intensity, activity and perceptual loudness (0.0 - 1.0)."
    )

with kpi_col5:
    st.metric(
        label="Avg Danceability",
        value=f"{kpis['avg_danceability']}",
        help="Suitability for dancing based on tempo, rhythm stability and beat strength."
    )

with kpi_col6:
    st.metric(
        label="Avg Valence",
        value=f"{kpis['avg_valence']}",
        help="Musical positiveness, happiness and cheerfulness (0.0 - 1.0)."
    )

st.markdown("---")

# Edge case: If no tracks match filters
if df_filtered.empty:
    st.warning("⚠️ No tracks match the currently selected filter criteria. Please adjust or reset the sidebar filters.")
    st.stop()


# -----------------------------------------------------------------------------
# 6. TABBED NAVIGATION LAYOUT
# -----------------------------------------------------------------------------
tab_overview, tab_visualizations, tab_mood, tab_explorer = st.tabs([
    "📊 Dataset Overview & KPIs",
    "📈 Exploratory Visualizations",
    "🎭 Mood Classification Matrix",
    "🔍 Track Explorer & Audio Profiler"
])


# =============================================================================
# TAB 1: DATASET OVERVIEW & SUMMARY STATISTICS
# =============================================================================
with tab_overview:
    st.subheader("📋 Dataset Overview & Key Performance Indicators")
    st.markdown(
        "Explore summary metrics, category-wise group-by distributions, "
        "and inspect raw data records using interactive layout containers."
    )

    overview_col1, overview_col2 = st.columns([1, 1])

    with overview_col1:
        st.markdown("#### 🎭 Category-Wise Record Counts (Mood Classification)")
        mood_counts_df = analytics_engine.get_category_counts(df_filtered, 'mood')
        st.dataframe(
            mood_counts_df.style.format({'Percentage': '{:.1f}%'}),
            use_container_width=True,
            hide_index=True
        )

        st.markdown(f"""
        <div class="insight-box">
            <b>💡 Group-By KPI Summary:</b><br>
            • The dominant mood category in the current subset is 
            <b>{mood_counts_df.iloc[0]['mood'] if not mood_counts_df.empty else 'N/A'}</b> 
            representing <b>{mood_counts_df.iloc[0]['Percentage'] if not mood_counts_df.empty else 0}%</b> of tracks.<br>
            • Group-by aggregation partitions {kpis['total_records']} tracks across 
            <b>{len(mood_counts_df)}</b> distinct emotional quadrants.
        </div>
        """, unsafe_allow_html=True)

    with overview_col2:
        st.markdown("#### 🎤 Top Artists Summary (Group-By Aggregation)")
        artist_summary_df = analytics_engine.get_artist_summary(df_filtered, top_n=6)
        st.dataframe(
            artist_summary_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown(f"""
        <div class="insight-box">
            <b>💡 Catalog Distribution:</b><br>
            • Unique artists in active subset: <b>{kpis['unique_artists']}</b>.<br>
            • Leading artist by catalog count: 
            <b>{artist_summary_df.iloc[0]['artist_name'] if not artist_summary_df.empty else 'N/A'}</b> 
            with <b>{artist_summary_df.iloc[0]['Track_Count'] if not artist_summary_df.empty else 0}</b> tracks.
        </div>
        """, unsafe_allow_html=True)

    # Expandable Sections
    with st.expander("🔍 Inspect Filtered Records & Column Selector", expanded=False):
        st.markdown("Filter, sort, and download the active dataset subset.")
        default_cols = ['track_name', 'artist_name', 'mood', 'popularity', 'energy', 'danceability', 'valence', 'tempo', 'duration_min']
        available_cols = [c for c in df_filtered.columns if c not in default_cols]
        chosen_cols = st.multiselect("Select Columns to Display:", options=df_filtered.columns.tolist(), default=default_cols)
        st.dataframe(df_filtered[chosen_cols], use_container_width=True)

        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="soundscope_filtered_tracks.csv",
            mime="text/csv"
        )

    with st.expander("📈 Descriptive Statistical Summary (`df.describe()`)", expanded=False):
        st.markdown("Mathematical distribution (Mean, Std, Min, 25%, 50%, 75%, Max) of key numerical attributes:")
        num_cols = ['popularity', 'energy', 'danceability', 'valence', 'tempo', 'loudness', 'acousticness']
        existing_num_cols = [c for c in num_cols if c in df_filtered.columns]
        st.dataframe(df_filtered[existing_num_cols].describe().round(3), use_container_width=True)

    with st.expander("📐 Audio Features Glossary & Theory", expanded=False):
        st.markdown("""
        - **Valence**: Measures musical positiveness (0.0 to 1.0). High valence sounds happy, cheerful, euphoric; low valence sounds sad, depressed, angry.
        - **Energy**: Perceptual measure of intensity and activity (0.0 to 1.0). Typically, energetic tracks feel fast, loud, and noisy.
        - **Danceability**: Describes how suitable a track is for dancing based on tempo, rhythm stability, beat strength, and overall regularity.
        - **Tempo**: Estimated overall tempo of a track in beats per minute (BPM).
        - **Popularity**: Spotify popularity algorithm (0 to 100) based on total number and recency of plays.
        """)


# =============================================================================
# TAB 2: EXPLORATORY VISUALIZATIONS (BAR, LINE, SCATTER)
# =============================================================================
with tab_visualizations:
    st.subheader("📈 Exploratory Data Analysis & Visualizations")
    st.markdown(
        "Comprehensive visual exploration featuring categorical bar charts, "
        "numerical trend line charts, and multidimensional scatter plots."
    )

    # 1. BAR CHARTS ROW
    st.markdown("### 1. Categorical Bar Charts")
    bar_col1, bar_col2 = st.columns(2)

    with bar_col1:
        fig_mood_bar = Visualizer.create_mood_bar_chart(df_filtered)
        st.plotly_chart(fig_mood_bar, use_container_width=True, key="bar_mood_distribution")
        st.markdown("""
        <div class="insight-box">
            <b>Interpretation (Mood Distribution Bar Chart):</b><br>
            Visualizes the distribution of songs across SoundScope mood quadrants. 
            High proportions in <i>Intense</i> or <i>Happy / Upbeat</i> indicate higher average energy 
            and danceability in the active collection.
        </div>
        """, unsafe_allow_html=True)

    with bar_col2:
        top_n_artists = st.selectbox("Select Top N Artists:", options=[5, 8, 10, 15], index=1)
        fig_artist_bar = Visualizer.create_artist_bar_chart(df_filtered, top_n=top_n_artists)
        st.plotly_chart(fig_artist_bar, use_container_width=True, key="bar_top_artists")
        st.markdown(f"""
        <div class="insight-box">
            <b>Interpretation (Artist Catalog Bar Chart):</b><br>
            Ranks the top {top_n_artists} artists by track count, with color-mapping representing 
            their average track popularity. This highlights both prolific artists and high-impact performers.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. LINE CHART
    st.markdown("### 2. Numerical Trend Line Chart")
    fig_line = Visualizer.create_tempo_trend_line_chart(df_filtered)
    st.plotly_chart(fig_line, use_container_width=True, key="line_tempo_trends")
    st.markdown("""
    <div class="insight-box">
        <b>Interpretation (Audio Features vs Tempo Bins Line Chart):</b><br>
        Illustrates how musical features vary systematically across Tempo (BPM) intervals. 
        Tracks with faster tempos (> 120 BPM) generally exhibit elevated <i>Energy</i> and 
        <i>Danceability</i>, whereas slower tempos (< 80 BPM) correlate with calmer acoustic profiles.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. SCATTER PLOTS
    st.markdown("### 3. Numerical Relationship Scatter Plots")
    scatter_mode = st.radio(
        "Choose Scatter Relationship:",
        options=[
            "Valence vs Energy (Core Mood Scatter)",
            "Loudness (dB) vs Energy (Acoustic Density)"
        ],
        horizontal=True
    )

    if scatter_mode == "Valence vs Energy (Core Mood Scatter)":
        fig_scatter = Visualizer.create_mood_scatter_plot(df_filtered)
        st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_valence_energy")
        st.markdown("""
        <div class="insight-box">
            <b>Interpretation (Valence vs Energy Scatter Plot):</b><br>
            Demonstrates the 2D emotional mapping of tracks. Crosshair dashed lines at 0.5 divide 
            songs into four psychological quadrants (Happy, Intense, Calm, Melancholic), while marker 
            size encodes song popularity. Outliers near the extremes reveal unique acoustic signatures.
        </div>
        """, unsafe_allow_html=True)
    else:
        fig_scatter_loud = Visualizer.create_loudness_energy_scatter(df_filtered)
        st.plotly_chart(fig_scatter_loud, use_container_width=True, key="scatter_loudness_energy")
        st.markdown("""
        <div class="insight-box">
            <b>Interpretation (Loudness vs Energy Scatter Plot):</b><br>
            Examines the strong positive non-linear correlation between acoustic loudness (decibels) 
            and perceived track energy. Highly compressed, louder tracks (-5 dB to 0 dB) consistently score 
            above 0.70 in energy.
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# TAB 3: MOOD CLASSIFICATION MATRIX
# =============================================================================
with tab_mood:
    st.subheader("🎭 SoundScope 2D Mood Classification Matrix")
    st.markdown(
        "Songs are categorized using audio feature vectors, primarily **Valence** (musical positiveness) "
        "and **Energy** (intensity & arousal) based on the psychological Circumplex Model of Affect."
    )

    mood_col_left, mood_col_right = st.columns([1.6, 1.0])

    with mood_col_left:
        fig_quadrant = Visualizer.create_mood_scatter_plot(df_filtered)
        st.plotly_chart(fig_quadrant, use_container_width=True, key="scatter_mood_quadrant_matrix")

    with mood_col_right:
        st.markdown("#### 🎯 Quadrant Definitions")
        st.markdown("""
        - 🟢 **Happy / Upbeat** (`Valence >= 0.5`, `Energy >= 0.5`)
          *Energetic, cheerful, feel-good anthems, dance-pop, EDM.*
        - 🔴 **Intense** (`Valence < 0.5`, `Energy >= 0.5`)
          *Aggressive, high-tempo, turbulent, heavy bass, dark electronic, hard rock.*
        - 🔵 **Calm / Positive** (`Valence >= 0.5`, `Energy < 0.5`)
          *Relaxed, peaceful, acoustic, warm melodies, chillhop, gentle lo-fi.*
        - 🟣 **Melancholic** (`Valence < 0.5`, `Energy < 0.5`)
          *Introspective, somber, sad, ambient, acoustic ballads.*
        - 🟡 **Balanced** (Center threshold `0.40 - 0.60`)
          *Nuanced tracks balancing melodic optimism and rhythmic drive.*
        """)

        st.markdown("---")
        st.markdown("#### 📊 Filtered Mood Share")
        mood_stats = analytics_engine.get_category_counts(df_filtered, 'mood')
        for _, row in mood_stats.iterrows():
            st.write(f"**{row['mood']}**: {row['Count']} tracks ({row['Percentage']}%)")


# =============================================================================
# TAB 4: TRACK SEARCH & AUDIO PROFILER
# =============================================================================
with tab_explorer:
    st.subheader("🎵 Track Inspector & Audio Radar Profiler")
    st.markdown("Select an individual song to inspect its comprehensive audio profile radar and metrics.")

    track_list = df_filtered[['track_name', 'artist_name']].drop_duplicates()
    track_options = [f"{r['track_name']} — {r['artist_name']}" for _, r in track_list.iterrows()]

    if track_options:
        selected_track_str = st.selectbox("Select Track to Inspect:", options=track_options)
        selected_track_title = selected_track_str.split(" — ")[0]
        track_row = df_filtered[df_filtered['track_name'] == selected_track_title].iloc[0]

        prof_col1, prof_col2 = st.columns([1, 1])

        with prof_col1:
            st.markdown(f"### 🎧 {track_row['track_name']}")
            st.markdown(f"**Artist:** {track_row['artist_name']}")
            st.markdown(f"**SoundScope Mood:** `{track_row['mood']}`")

            m1, m2, m3 = st.columns(3)
            m1.metric("Popularity", f"{int(track_row.get('popularity', 0))}/100")
            m2.metric("Tempo", f"{track_row.get('tempo', 0.0):.1f} BPM")
            m3.metric("Duration", f"{track_row.get('duration_min', 0.0):.2f} min")

            m4, m5, m6 = st.columns(3)
            m4.metric("Energy", f"{track_row.get('energy', 0.0):.3f}")
            m5.metric("Danceability", f"{track_row.get('danceability', 0.0):.3f}")
            m6.metric("Valence", f"{track_row.get('valence', 0.0):.3f}")

        with prof_col2:
            st.markdown("#### 🕸️ Audio Feature Radar")
            fig_radar = Visualizer.create_radar_profile(track_row)
            st.plotly_chart(fig_radar, use_container_width=True, key="radar_audio_profiler")

    else:
        st.info("No tracks available under current filters.")
