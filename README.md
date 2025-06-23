# Visual Analysis of Datasets of Mountain Tracks
#### Author: Xavier Rosinach Capell

---

This project is based on the development of an interactive web application for the visual analysis of mountain trail datasets, focusing on three of the most iconic mountain regions in Catalonia: **Canigó**, **Matagalls**, and **Vall Ferrera**.

Using GPS data extracted from **Wikiloc**, the application allows users to explore, compare, and analyze trail usage patterns, as well as access detailed information about individual routes.

The project is built on a data processing and visualization pipeline using Python libraries such as:

- `pandas`
- `altair`
- `folium`
- `streamlit`

The application enables spatial and temporal exploration of:

- Trail popularity
- Difficulty
- Elevation profiles
- User behavior under different weather conditions

Through interactive visualizations, users can:

- Identify popular paths
- Analyze trends over time
- Examine relationships between difficulty and quantitative metrics
- Assess the impact of weather on hiking activity

Each route can also be explored individually through specific visualizations. The project offers a practical and user-friendly tool for hikers and supports future expansion to other mountain areas.

**Keywords**: path, track, Wikiloc, Matagalls, Canigó, Vall Ferrera, map matching, stacionariety, average pace, elevation, points of interest

---

## How to Use the Interactive Web Application

Follow these steps to run the application locally:

### 1. Create a project directory

```bash
mkdir "Interactive Web Application"
cd "Interactive Web Application"
```

### 2. Clone the repository

```bash
git clone https://github.com/xavierrosinach/Visual-Analysis-of-Datasets-of-Mountain-Tracks.git
```

This will create a folder named `Visual-Analysis-of-Datasets-of-Mountain-Tracks`.

### 3. Create a `Data` folder

```bash
mkdir Data
```

### 4. Download and unzip the data

Download the dataset from the provided link and unzip it into the `Data` directory.

After unzipping, you should have the following structure:

```
Data/
├── Processing-Data/
└── Streamlit-Data/
```

### 5. Install required Python libraries (if needed)

If you don't already have the necessary libraries installed, you can install them using `pip`:

```bash
pip install streamlit pandas altair
```

### 6. Run the application

Navigate to the Streamlit directory and run the application:

```bash
cd Visual-Analysis-of-Datasets-of-Mountain-Tracks/Streamlit
streamlit run final_application.py
```

---