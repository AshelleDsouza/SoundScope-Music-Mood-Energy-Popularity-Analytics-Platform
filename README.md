# SoundScope – Music Mood, Energy & Popularity Analytics Platform
### Python Streamlit Web Application • Lab 6: Exploring Different Graphs Using Layouts
**Department of Computer Science • Christ (Deemed to be University)**

---

## 🎵 1. Project Domain Overview
**SoundScope** is an interactive web-based music analytics platform designed to analyze songs based on their acoustic characteristics, popularity scores, and musical moods. Built with Python and **Streamlit**, the application transforms raw Spotify audio features into structured, actionable insights using modern interactive layouts.

### Key Audio Features Analyzed:
- **Valence**: Musical positiveness, cheerfulness, and euphoria (scale `0.0` to `1.0`).
- **Energy**: Perceptual intensity, loudness, and activity (scale `0.0` to `1.0`).
- **Danceability**: Suitability for dancing based on tempo, rhythm stability, and beat regularity (scale `0.0` to `1.0`).
- **Tempo**: Estimated track tempo in beats per minute (BPM).
- **Popularity**: Spotify track popularity score (scale `0` to `100`).
- **Loudness**: Overall loudness in decibels (dB).

---

## 🎭 2. SoundScope Mood Classification Architecture
SoundScope implements the psychological **Circumplex Model of Affect (Russell's Model)** to map songs into 5 distinct emotional zones based on Valence and Energy:
1. 🟢 **Happy / Upbeat**: High Valence ($\ge 0.5$) & High Energy ($\ge 0.5$). Euphoric, cheerful, dance-pop, EDM.
2. 🔴 **Intense**: Low Valence ($< 0.5$) & High Energy ($\ge 0.5$). Aggressive, turbulent, hard rock, dark electronic.
3. 🔵 **Calm / Positive**: High Valence ($\ge 0.5$) & Low Energy ($< 0.5$). Relaxed, peaceful, acoustic, chillhop, gentle lo-fi.
4. 🟣 **Melancholic**: Low Valence ($< 0.5$) & Low Energy ($< 0.5$). Sad, introspective, ambient, acoustic ballads.
5. 🟡 **Balanced**: Threshold center zone ($0.40 \le \text{Valence} \le 0.60$ and $0.40 \le \text{Energy} \le 0.60$). Tracks with balanced mood dynamics.

---

## 📌 3. Lab 6 Requirement Mapping

| Lab 6 Component | Implementation in SoundScope |
| :--- | :--- |
| **1a. Key Performance Indicators (KPIs)** | Displays Total Tracks, Total Duration (Minutes & Hours), Avg Popularity, Avg Energy, Avg Danceability, and Avg Valence using `st.metric`. Includes Group-By categorical counts for Mood and Artists. |
| **1b. Streamlit Input Widgets** | `st.text_input` (Search), `st.multiselect` (Moods & Artists), `st.slider` (Popularity, Energy, Danceability), `st.selectbox` (Top N, Scatter metrics), `st.radio` (Data source selector), and `st.button` (Reset filters). |
| **1c. Filter-Responsive KPIs** | All KPIs, charts, dataframes, and calculations update dynamically upon interacting with any filter. |
| **2a. Bar Chart** | 1. Categorical distribution of songs across Mood Quadrants with percentage badges.<br>2. Horizontal Bar Chart of Top Artists ranked by catalog volume and colored by average popularity. |
| **2b. Line Chart** | Multidimensional line chart tracking changes in Average Energy, Danceability, and Valence across Tempo (BPM) intervals (`< 80`, `80-100`, `100-120`, `120-140`, `140-160`, `160+`). |
| **2c. Scatter Plot** | 1. **Core 2D Mood Quadrant Scatter**: Valence vs. Energy with mood color mapping, reference lines at `0.5`, and hover metadata.<br>2. **Loudness (dB) vs. Energy Scatter**: Highlights acoustic density correlation. |
| **2d. Interpretations & Labels** | Detailed chart titles, axes labels, legends, and university-grade analytical interpretations (`<div class="insight-box">`) beneath every visualization. |
| **3a. Sidebar Navigation** | Dataset selector, CSV file uploader, real-time search, multiselects, range sliders, and reset button. |
| **3b. Columns Layout** | Arranged 6-column KPI summary dashboard and side-by-side comparative visualization grids (`st.columns`). |
| **3c. Containers & Expanders** | `st.expander` sections for Raw Dataset Inspector (with column selector and CSV export), Descriptive Statistics (`df.describe()`), Audio Glossary, and Methodology. |
| **3d. Tabs Layout** | 4 structured tabs: `📊 Dataset Overview & KPIs`, `📈 Exploratory Visualizations`, `🎭 Mood Classification Matrix`, and `🎵 Track Search & Audio Profiler`. |
| **4. Cloud Deployment** | Preconfigured `requirements.txt`, `.streamlit/config.toml`, and step-by-step instructions for Streamlit Community Cloud. |

---

## 📂 4. Project Directory Structure
```
LAB6/
├── app.py                      # Main Streamlit web application
├── data_processor.py           # OOP Data processing, MoodClassifier & SoundScopeAnalytics engine
├── visualizations.py           # Plotly visualization classes with custom styling and themes
├── spotify_tracks.csv          # Pre-loaded Spotify dataset
├── requirements.txt            # Python package dependencies
├── .streamlit/
│   └── config.toml             # Custom SoundScope dark theme & server configurations
└── README.md                   # Complete documentation and deployment guide
```

---

## 🚀 5. How to Run Locally

### Prerequisites:
Ensure Python 3.9+ is installed on your machine.

1. **Open Terminal / Command Prompt** in the `LAB6` folder:
   ```bash
   cd "C:\Users\Ashelle Dsouza\Desktop\CHRIST UNIVERSITY\SEM 2\PYTHON\LAB6"
   ```

2. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit Web Application**:
   ```bash
   streamlit run app.py
   ```

4. The application will open automatically in your browser at `http://localhost:8501`.

---

## 🌐 6. How to Deploy to Streamlit Community Cloud

As required by **Lab 6 (Section 4)**:

1. **Initialize Git & Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Complete SoundScope Streamlit Analytics Platform for Lab 6"
   git branch -M main
   git remote add origin https://github.com/<your-username>/soundscope-analytics.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
   - Click **"New app"**.
   - Select your repository (`soundscope-analytics`), Branch (`main`), and Main file path (`app.py`).
   - Click **"Deploy!"**.
   - Within 1–2 minutes, your web application will be live at a public URL (e.g. `https://soundscope-music-analytics.streamlit.app`).
