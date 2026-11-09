"""
SoundScope - Music Mood, Energy & Popularity Analytics Platform
Module: visualizations.py
Description: Interactive charting engine using Plotly and Streamlit layouts.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict
from data_processor import MoodClassifier


class Visualizer:
    """
    Encapsulates all visualization logic with consistent styling, interactive hover data,
    axis labels, legends, and domain-specific color palettes.
    """

    DARK_THEME_LAYOUT = dict(
        paper_bgcolor='rgba(15, 23, 42, 0.6)',
        plot_bgcolor='rgba(15, 23, 42, 0.4)',
        font=dict(color="#E2E8F0", family="Segoe UI, sans-serif"),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0.7)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            borderwidth=1
        )
    )

    @staticmethod
    def create_mood_bar_chart(df: pd.DataFrame) -> go.Figure:
        """
        Bar Chart: Categorical distribution of songs across mood categories.
        """
        mood_counts = df['mood'].value_counts().reset_index()
        mood_counts.columns = ['Mood', 'Count']
        total = mood_counts['Count'].sum()
        mood_counts['Percentage'] = ((mood_counts['Count'] / total) * 100).round(1)

        colors = [MoodClassifier.MOOD_COLORS.get(m, '#94A3B8') for m in mood_counts['Mood']]

        fig = go.Figure(data=[
            go.Bar(
                x=mood_counts['Mood'],
                y=mood_counts['Count'],
                text=[f"{c} ({p}%)" for c, p in zip(mood_counts['Count'], mood_counts['Percentage'])],
                textposition='outside',
                marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.2)', width=1.5)),
                hovertemplate="<b>Mood:</b> %{x}<br><b>Tracks:</b> %{y}<br><b>Share:</b> %{text}<extra></extra>"
            )
        ])

        fig.update_layout(
            title="<b>Distribution of Tracks Across Mood Categories</b>",
            xaxis_title="SoundScope Mood Quadrant",
            yaxis_title="Total Track Count",
            **Visualizer.DARK_THEME_LAYOUT
        )
        fig.update_xaxes(showgrid=False, linecolor="rgba(255,255,255,0.2)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", linecolor="rgba(255,255,255,0.2)")
        return fig

    @staticmethod
    def create_artist_bar_chart(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """
        Bar Chart: Top artists by track count and average popularity.
        """
        artist_summary = df.groupby('artist_name').agg(
            Count=('track_name', 'count'),
            Avg_Pop=('popularity', 'mean')
        ).reset_index().sort_values(by='Count', ascending=True).tail(top_n)

        artist_summary['Avg_Pop'] = artist_summary['Avg_Pop'].round(1)

        fig = go.Figure(go.Bar(
            y=artist_summary['artist_name'],
            x=artist_summary['Count'],
            orientation='h',
            marker=dict(
                color=artist_summary['Avg_Pop'],
                colorscale='Viridis',
                colorbar=dict(title="Avg Popularity"),
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            text=[f"{c} tracks (Pop: {p})" for c, p in zip(artist_summary['Count'], artist_summary['Avg_Pop'])],
            textposition='inside',
            hovertemplate="<b>Artist:</b> %{y}<br><b>Tracks:</b> %{x}<br><b>Avg Pop:</b> %{marker.color}<extra></extra>"
        ))

        fig.update_layout(
            title=f"<b>Top {top_n} Artists by Catalog Volume & Popularity</b>",
            xaxis_title="Number of Tracks",
            yaxis_title="Artist Name",
            **Visualizer.DARK_THEME_LAYOUT
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
        fig.update_yaxes(showgrid=False)
        return fig

    @staticmethod
    def create_tempo_trend_line_chart(df: pd.DataFrame) -> go.Figure:
        """
        Line Chart: Illustrates trends in Popularity, Energy, and Danceability across Tempo intervals.
        """
        df_copy = df.copy()
        # Create tempo bins
        bins = [0, 80, 100, 120, 140, 160, 220]
        labels = ['< 80 (Slow)', '80-100 (Chill)', '100-120 (Groove)', '120-140 (Upbeat)', '140-160 (Fast)', '160+ (Very Fast)']
        df_copy['tempo_bin'] = pd.cut(df_copy['tempo'], bins=bins, labels=labels, include_lowest=True)

        trend = df_copy.groupby('tempo_bin', observed=False).agg(
            Avg_Energy=('energy', 'mean'),
            Avg_Danceability=('danceability', 'mean'),
            Avg_Valence=('valence', 'mean'),
            Avg_Popularity=('popularity', 'mean'),
            Track_Count=('track_name', 'count')
        ).reset_index()

        fig = go.Figure()

        # Add traces
        fig.add_trace(go.Scatter(
            x=trend['tempo_bin'],
            y=trend['Avg_Energy'],
            mode='lines+markers',
            name='Average Energy',
            line=dict(color='#FF4B4B', width=3),
            marker=dict(size=8),
            hovertemplate="<b>Tempo:</b> %{x}<br><b>Energy:</b> %{y:.2f}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=trend['tempo_bin'],
            y=trend['Avg_Danceability'],
            mode='lines+markers',
            name='Average Danceability',
            line=dict(color='#00C49F', width=3, dash='dash'),
            marker=dict(size=8),
            hovertemplate="<b>Tempo:</b> %{x}<br><b>Danceability:</b> %{y:.2f}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=trend['tempo_bin'],
            y=trend['Avg_Valence'],
            mode='lines+markers',
            name='Average Valence (Positivity)',
            line=dict(color='#FFAA00', width=3, dash='dot'),
            marker=dict(size=8),
            hovertemplate="<b>Tempo:</b> %{x}<br><b>Valence:</b> %{y:.2f}<extra></extra>"
        ))

        fig.update_layout(
            title="<b>Audio Feature Dynamics Across Tempo (BPM) Intervals</b>",
            xaxis_title="Tempo Range (BPM)",
            yaxis_title="Normalized Attribute Level (0.0 - 1.0)",
            **Visualizer.DARK_THEME_LAYOUT
        )
        fig.update_xaxes(showgrid=False, linecolor="rgba(255,255,255,0.2)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)", range=[0, 1.05])
        return fig

    @staticmethod
    def create_mood_scatter_plot(df: pd.DataFrame) -> go.Figure:
        """
        Scatter Plot: Valence vs Energy (SoundScope 2D Mood Quadrant Matrix).
        With mood color coding, track metadata in hover, and quadrant threshold lines at 0.5.
        """
        fig = px.scatter(
            df,
            x='valence',
            y='energy',
            color='mood',
            color_discrete_map=MoodClassifier.MOOD_COLORS,
            hover_name='track_name',
            hover_data={
                'artist_name': True,
                'popularity': True,
                'tempo': ':.1f',
                'valence': ':.3f',
                'energy': ':.3f',
                'mood': True
            },
            size='popularity',
            size_max=14,
            opacity=0.85
        )

        # Quadrant dividing lines at 0.5
        fig.add_shape(
            type="line", x0=0.5, y0=0, x1=0.5, y1=1.0,
            line=dict(color="rgba(255, 255, 255, 0.35)", width=1.5, dash="dash")
        )
        fig.add_shape(
            type="line", x0=0, y0=0.5, x1=1.0, y1=0.5,
            line=dict(color="rgba(255, 255, 255, 0.35)", width=1.5, dash="dash")
        )

        # Quadrant Labels
        fig.add_annotation(x=0.82, y=0.96, text="<b>HAPPY / UPBEAT</b>", showarrow=False,
                           font=dict(color="#1DB954", size=11))
        fig.add_annotation(x=0.18, y=0.96, text="<b>INTENSE / TURBULENT</b>", showarrow=False,
                           font=dict(color="#FF4B4B", size=11))
        fig.add_annotation(x=0.82, y=0.08, text="<b>CALM / PEACEFUL</b>", showarrow=False,
                           font=dict(color="#00C49F", size=11))
        fig.add_annotation(x=0.18, y=0.08, text="<b>MELANCHOLIC / SAD</b>", showarrow=False,
                           font=dict(color="#5E72E4", size=11))

        fig.update_layout(
            title="<b>SoundScope 2D Mood Matrix: Valence vs Energy</b>",
            xaxis_title="Valence (Musical Positivity & Cheerfulness)",
            yaxis_title="Energy (Arousal, Intensity & Activity)",
            **Visualizer.DARK_THEME_LAYOUT
        )
        fig.update_xaxes(range=[-0.02, 1.02], showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(range=[-0.02, 1.02], showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        return fig

    @staticmethod
    def create_loudness_energy_scatter(df: pd.DataFrame) -> go.Figure:
        """
        Scatter Plot: Loudness (dB) vs Energy with Popularity color mapping.
        """
        fig = px.scatter(
            df,
            x='loudness',
            y='energy',
            color='popularity',
            color_continuous_scale='Turbo',
            hover_name='track_name',
            hover_data=['artist_name', 'loudness', 'energy', 'popularity', 'danceability'],
            opacity=0.8
        )

        fig.update_layout(
            title="<b>Relationship: Acoustic Loudness (dB) vs Perceived Energy</b>",
            xaxis_title="Loudness (dB)",
            yaxis_title="Energy (0.0 - 1.0)",
            **Visualizer.DARK_THEME_LAYOUT
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
        return fig

    @staticmethod
    def create_radar_profile(track_series: pd.Series) -> go.Figure:
        """
        Radar chart profiling an individual track's key audio dimensions.
        """
        features = ['energy', 'danceability', 'valence', 'acousticness', 'liveness', 'speechiness']
        values = [track_series.get(f, 0.0) for f in features]
        # Close the polygon loop
        features_closed = features + [features[0]]
        values_closed = values + [values[0]]

        fig = go.Figure(data=go.Scatterpolar(
            r=values_closed,
            theta=[f.capitalize() for f in features_closed],
            fill='toself',
            fillcolor='rgba(29, 185, 84, 0.35)',
            line=dict(color='#1DB954', width=2),
            name=str(track_series.get('track_name', 'Track'))
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1.0], color="#94A3B8"),
                bgcolor='rgba(15, 23, 42, 0.5)'
            ),
            showlegend=False,
            margin=dict(l=30, r=30, t=30, b=30),
            paper_bgcolor='rgba(15, 23, 42, 0.0)',
            font=dict(color="#E2E8F0")
        )
        return fig
