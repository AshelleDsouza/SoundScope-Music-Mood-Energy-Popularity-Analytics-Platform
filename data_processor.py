"""
SoundScope - Music Mood, Energy & Popularity Analytics Platform
Module: data_processor.py
Description: Data processing, mood classification engine, and KPI computations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List, Optional


class MoodClassifier:
    """
    Classifies musical tracks into mood quadrants based on Valence (Musical Positiveness)
    and Energy (Intensity & Activity) using the Russell Circumplex Model of Affect.
    """

    MOOD_HAPPY = "Happy / Upbeat"
    MOOD_INTENSE = "Intense"
    MOOD_CALM = "Calm / Positive"
    MOOD_MELANCHOLIC = "Melancholic"
    MOOD_BALANCED = "Balanced"

    MOOD_COLORS = {
        MOOD_HAPPY: "#1DB954",       # Vibrant Spotify Green
        MOOD_INTENSE: "#FF4B4B",     # Energetic Coral Red
        MOOD_CALM: "#00C49F",        # Soothing Teal
        MOOD_MELANCHOLIC: "#5E72E4", # Deep Blue
        MOOD_BALANCED: "#FFAA00"     # Warm Amber
    }

    @classmethod
    def assign_mood(cls, valence: float, energy: float) -> str:
        """Categorize an individual track given its valence and energy."""
        # Balanced zone: songs near the center threshold
        if 0.40 <= valence <= 0.60 and 0.40 <= energy <= 0.60:
            return cls.MOOD_BALANCED
        if valence >= 0.5 and energy >= 0.5:
            return cls.MOOD_HAPPY
        elif valence < 0.5 and energy >= 0.5:
            return cls.MOOD_INTENSE
        elif valence >= 0.5 and energy < 0.5:
            return cls.MOOD_CALM
        else:
            return cls.MOOD_MELANCHOLIC

    @classmethod
    def classify_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Vectorized classification for high performance on large datasets."""
        if 'valence' not in df.columns or 'energy' not in df.columns:
            raise ValueError("Dataframe must contain 'valence' and 'energy' columns.")

        v = df['valence']
        e = df['energy']

        # Vectorized conditions
        cond_balanced = (v >= 0.40) & (v <= 0.60) & (e >= 0.40) & (e <= 0.60)
        cond_happy = (v >= 0.5) & (e >= 0.5)
        cond_intense = (v < 0.5) & (e >= 0.5)
        cond_calm = (v >= 0.5) & (e < 0.5)

        choices = [
            cls.MOOD_BALANCED,
            cls.MOOD_HAPPY,
            cls.MOOD_INTENSE,
            cls.MOOD_CALM
        ]
        conditions = [
            cond_balanced,
            cond_happy & ~cond_balanced,
            cond_intense & ~cond_balanced,
            cond_calm & ~cond_balanced
        ]

        df['mood'] = np.select(conditions, choices, default=cls.MOOD_MELANCHOLIC)
        return df


class SoundScopeAnalytics:
    """
    Object-oriented analytics engine providing data loading, KPI computation,
    group-by aggregations, and multi-parameter filtering.
    """

    EXPECTED_COLUMNS = [
        'artist_name', 'track_name', 'popularity', 'energy', 'danceability',
        'valence', 'tempo', 'acousticness', 'loudness', 'duration_ms'
    ]

    def __init__(self, data_source: Optional[Any] = None):
        self.raw_df: pd.DataFrame = pd.DataFrame()
        self.processed_df: pd.DataFrame = pd.DataFrame()
        if data_source is not None:
            self.load_data(data_source)

    def load_data(self, data_source: Any) -> pd.DataFrame:
        """
        Loads CSV dataset from filepath or file-like buffer with error handling.
        """
        try:
            if isinstance(data_source, pd.DataFrame):
                df = data_source.copy()
            else:
                df = pd.read_csv(data_source)

            # Strip whitespace from column names
            df.columns = df.columns.str.strip()

            # Handle column name variations if present
            rename_map = {
                'artists': 'artist_name',
                'name': 'track_name',
                'id': 'track_id'
            }
            for k, v in rename_map.items():
                if k in df.columns and v not in df.columns:
                    df = df.rename(columns={k: v})

            # Check essential columns
            for col in ['energy', 'valence']:
                if col not in df.columns:
                    raise KeyError(f"Required audio feature column '{col}' missing from dataset.")

            # Coerce numerical attributes
            numeric_cols = [
                'popularity', 'danceability', 'energy', 'valence', 'tempo',
                'acousticness', 'loudness', 'duration_ms', 'speechiness',
                'instrumentalness', 'liveness'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Drop rows with NaN in critical features
            df = df.dropna(subset=['energy', 'valence']).copy()

            # Assign Mood
            df = MoodClassifier.classify_dataframe(df)

            # Helper duration in minutes
            if 'duration_ms' in df.columns:
                df['duration_min'] = (df['duration_ms'] / 60000).round(2)
            else:
                df['duration_min'] = 0.0

            self.raw_df = df
            self.processed_df = df.copy()
            return self.processed_df

        except Exception as e:
            raise RuntimeError(f"Error processing music dataset: {str(e)}")

    def calculate_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes Key Performance Indicators (KPIs) conforming to Lab 6:
        - Total observations
        - Sums of numerical metrics (Total Duration, Total Popularity Points)
        - Averages of relevant numerical attributes (Popularity, Danceability, Energy, Valence, Tempo)
        """
        if df.empty:
            return {
                'total_records': 0,
                'avg_popularity': 0.0,
                'avg_energy': 0.0,
                'avg_danceability': 0.0,
                'avg_valence': 0.0,
                'avg_tempo': 0.0,
                'total_duration_hours': 0.0,
                'total_duration_minutes': 0.0,
                'unique_artists': 0
            }

        total_records = len(df)
        total_duration_ms = df['duration_ms'].sum() if 'duration_ms' in df.columns else 0
        total_duration_hours = round(total_duration_ms / (1000 * 60 * 60), 2)
        total_duration_minutes = round(total_duration_ms / (1000 * 60), 1)

        kpis = {
            'total_records': total_records,
            'avg_popularity': round(float(df['popularity'].mean()), 1) if 'popularity' in df.columns else 0.0,
            'avg_energy': round(float(df['energy'].mean()), 3) if 'energy' in df.columns else 0.0,
            'avg_danceability': round(float(df['danceability'].mean()), 3) if 'danceability' in df.columns else 0.0,
            'avg_valence': round(float(df['valence'].mean()), 3) if 'valence' in df.columns else 0.0,
            'avg_tempo': round(float(df['tempo'].mean()), 1) if 'tempo' in df.columns else 0.0,
            'total_duration_hours': total_duration_hours,
            'total_duration_minutes': total_duration_minutes,
            'unique_artists': int(df['artist_name'].nunique()) if 'artist_name' in df.columns else 0
        }
        return kpis

    def get_category_counts(self, df: pd.DataFrame, category_col: str = 'mood') -> pd.DataFrame:
        """
        Computes category-wise record counts and percentages using group-by operations.
        """
        if df.empty or category_col not in df.columns:
            return pd.DataFrame(columns=[category_col, 'Count', 'Percentage'])

        counts = df[category_col].value_counts().reset_index()
        counts.columns = [category_col, 'Count']
        total = counts['Count'].sum()
        counts['Percentage'] = ((counts['Count'] / total) * 100).round(1)
        return counts

    def get_artist_summary(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """Group-by artist for track count and mean popularity."""
        if df.empty or 'artist_name' not in df.columns:
            return pd.DataFrame()

        summary = df.groupby('artist_name').agg(
            Track_Count=('track_name', 'count'),
            Avg_Popularity=('popularity', 'mean'),
            Avg_Energy=('energy', 'mean'),
            Avg_Valence=('valence', 'mean')
        ).reset_index()

        summary['Avg_Popularity'] = summary['Avg_Popularity'].round(1)
        summary['Avg_Energy'] = summary['Avg_Energy'].round(2)
        summary['Avg_Valence'] = summary['Avg_Valence'].round(2)
        return summary.sort_values(by='Track_Count', ascending=False).head(top_n)

    def filter_dataset(
        self,
        df: pd.DataFrame,
        search_query: str = "",
        selected_moods: Optional[List[str]] = None,
        selected_artists: Optional[List[str]] = None,
        popularity_range: Tuple[int, int] = (0, 100),
        energy_range: Tuple[float, float] = (0.0, 1.0),
        danceability_range: Tuple[float, float] = (0.0, 1.0)
    ) -> pd.DataFrame:
        """
        Multi-dimensional dynamic filter pipeline with regex search and numeric boundaries.
        """
        if df.empty:
            return df

        filtered = df.copy()

        # Text search (Artist name or Track title)
        if search_query.strip():
            query = search_query.strip()
            mask = (
                filtered['track_name'].str.contains(query, case=False, na=False) |
                filtered['artist_name'].str.contains(query, case=False, na=False)
            )
            filtered = filtered[mask]

        # Mood Filter
        if selected_moods and len(selected_moods) > 0:
            filtered = filtered[filtered['mood'].isin(selected_moods)]

        # Artist Filter
        if selected_artists and len(selected_artists) > 0:
            filtered = filtered[filtered['artist_name'].isin(selected_artists)]

        # Numeric Range Filters
        if 'popularity' in filtered.columns:
            filtered = filtered[
                (filtered['popularity'] >= popularity_range[0]) &
                (filtered['popularity'] <= popularity_range[1])
            ]

        if 'energy' in filtered.columns:
            filtered = filtered[
                (filtered['energy'] >= energy_range[0]) &
                (filtered['energy'] <= energy_range[1])
            ]

        if 'danceability' in filtered.columns:
            filtered = filtered[
                (filtered['danceability'] >= danceability_range[0]) &
                (filtered['danceability'] <= danceability_range[1])
            ]

        return filtered
