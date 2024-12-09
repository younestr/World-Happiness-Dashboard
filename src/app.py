import streamlit as st
import os
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go # gauge

# Define the directory where your files are stored
data_directory = r"C:\Users\hp\Downloads\DataViz M2\st-dashboard\data\cleaned"

# Get a list of CSV files in the directory
csv_files = [f for f in os.listdir(data_directory) if f.endswith('.csv')]

# Extract years from filenames (assuming filenames are in the format 'cleaned_YYYY.csv')
years = [f.split('_')[1].split('.')[0] for f in csv_files]

# Custom CSS for full dark theme styling
st.markdown("""
    <style>
    /* Dark theme for entire dashboard */
    body {
        background-color: #2e3b4e; /* Dark background */
        color: #f0f0f0; /* Light text color */
    }

    /* Styling for headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ecf0f1; /* Light color for headers */
    }

    /* Styling for the main content */
    .intro-text {
        font-size: 20px;
        font-family: 'Arial', sans-serif;
        color: #ecf0f1;
        text-align: center;
        padding: 20px;
        background-color: #34495e; /* Dark background for intro text */
        border-radius: 10px;
        margin-bottom: 10px; /* Reduced margin */
    }

    /* Footer styling */
    .footer-text {
        font-size: 14px;
        color: #bdc3c7;
        text-align: center;
        margin-top: 10px; /* Reduced margin */
    }

    /* Styling for links */
    a {
        color: #1abc9c; /* Light green for links */
        text-decoration: none;
    }
    a:hover {
        color: #16a085; /* Darker green on hover */
    }

    /* Styling for Streamlit buttons and other elements */
    .stButton>button {
        background-color: #1abc9c;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
    }

    .stButton>button:hover {
        background-color: #16a085; /* Darker green on hover */
    }
    
    /* Styling for Streamlit widgets */
    .stTextInput, .stNumberInput, .stSelectbox, .stMultiselect, .stTextArea {
        background-color: #34495e;
        color: #ecf0f1;
        border-radius: 5px;
        border: 1px solid #7f8c8d;
    }

    .stTextInput:focus, .stNumberInput:focus, .stSelectbox:focus, .stMultiselect:focus, .stTextArea:focus {
        border-color: #1abc9c;
    }

    </style>
""", unsafe_allow_html=True)

# Introduction message
st.markdown('<div class="intro-text">Welcome to the World Happiness Dashboard. This dashboard provides insights into global happiness rankings based on various factors.</div>', unsafe_allow_html=True)

# Data source as a clickable link
st.markdown('<div class="footer-text">Data source: <a href="https://www.kaggle.com/datasets/unsdsn/world-happiness/data" target="_blank">World Happiness Report Dataset</a></div>', unsafe_allow_html=True)

# Sidebar title with emoji
st.sidebar.markdown("## 🌍 World Happiness Dashboard")

# Scrollable menu to select the year in the sidebar
selected_year = st.sidebar.selectbox("Select a year:", years)

# Load the dataframe for the selected year
file_path = os.path.join(data_directory, f"cleaned_{selected_year}.csv")
df = pd.read_csv(file_path)

# Display the head of the dataframe for the selected year
st.write(f"### Data for the year {selected_year}:")
st.write(df.head())

# Display a message if required columns are missing
required_columns = ['Country', 'Happiness Score','Happiness Rank','Region','GDP per capita','Social support'
                    ,'Healthy life expectancy','Generosity','Dystopia Residual']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"The following required columns are missing in the dataset: {', '.join(missing_columns)}")
else:
    col1, col2 = st.columns([4, 2])  # Create two columns with a 4:2 width ratio

    # Create a world map heatmap based on the Happiness Score
    with col1:
        fig = px.choropleth(
            df,
            locations="Country",
            locationmode="country names",
            color="Happiness Score",
            hover_name="Country",
            hover_data={  # Adding additional data to show when hovering
                "Region": True,  # Show Region
                "Happiness Rank": True,  # Show Happiness Rank
                "Happiness Score": True,  # Show Happiness Score
                "GDP per capita": True,  # Show GDP per Capita
                "Social support": True,  # Example of other columns
                "Healthy life expectancy": True,  # Example of another column
                "Generosity": True,  # Example of another column
                "Dystopia Residual": True,  # Example of another column
            },
            title=f"World Happiness Heatmap for {selected_year}",
            color_continuous_scale=px.colors.sequential.Plasma
        )
        fig.update_geos(
            visible=True,
            resolution=50,
            showcountries=True,
            showocean=True,
            oceancolor="#0E1117",
            landcolor="#0E1117",
            lakecolor="#0E1117",
            bgcolor="#0E1117"
        )
        fig.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font_color="white",
            geo=dict(
                showframe=False,
                showcoastlines=False
            )
        )
        st.plotly_chart(fig)

    # Add space between the two columns
    st.empty()  # Empty space to avoid overlap

    # Display happiest countries with a progress bar for Happiness Score
    with col2:
        top_5_countries = df.nlargest(5, 'Happiness Score')[['Country', 'Happiness Score']]
        st.write(f"### Happiest Countries in {selected_year}")

        for _, row in top_5_countries.iterrows():
            progress = row['Happiness Score'] / 10  # Assuming the happiness score is out of 10
            st.progress(progress, text=f"{row['Country']} - {row['Happiness Score']}")

    # Secondary visualization based on GDP if available
    if 'GDP per capita' in df.columns:
        gdp_chart = px.scatter(
            df,
            x='GDP per capita',
            y='Happiness Score',
            size='Happiness Score',
            color='Region' if 'Region' in df.columns else None,
            hover_name='Country',
            title=f"GDP per capita vs Happiness Score ({selected_year})",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        gdp_chart.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font_color="white",
            xaxis_title="GDP per capita",
            yaxis_title="Happiness Score",
        )
        st.plotly_chart(gdp_chart)

    # Create a new row with 3 columns for the gauges
    col3, col4, col5 = st.columns(3)  # Three columns for the gauges

    # Happiness Score Gauge
    with col3:
        happiness_score_avg = df['Happiness Score'].mean()
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=happiness_score_avg,
            title={'text': "Average Happiness Score"},
            gauge={
                'axis': {'range': [None, 10]},
                'bar': {'color': "#1abc9c"},
                'steps': [
                    {'range': [0, 3], 'color': '#e74c3c'},
                    {'range': [3, 6], 'color': '#f39c12'},
                    {'range': [6, 10], 'color': '#2ecc71'},
                ]
            }
        ))
        fig_gauge.update_layout(paper_bgcolor="#0E1117", font_color="white")
        st.plotly_chart(fig_gauge, use_container_width=True)

    # GDP per Capita Gauge
    with col4:
        gdp_avg = df['GDP per capita'].mean()
        fig_gdp = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gdp_avg,
            title={'text': "Average GDP per capita (USD)"},
            gauge={
                'axis': {'range': [None, df['GDP per capita'].max()]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 10000], 'color': '#e74c3c'},
                    {'range': [10000, 30000], 'color': '#f39c12'},
                    {'range': [30000, df['GDP per capita'].max()], 'color': '#2ecc71'},
                ]
            }
        ))
        fig_gdp.update_layout(paper_bgcolor="#0E1117", font_color="white")
        st.plotly_chart(fig_gdp, use_container_width=True)

    # Social Support Gauge
    with col5:
        social_support_avg = df['Social support'].mean()
        fig_support = go.Figure(go.Indicator(
            mode="gauge+number",
            value=social_support_avg,
            title={'text': "Average Social Support"},
            gauge={
                'axis': {'range': [None, 1]},
                'bar': {'color': "#9b59b6"},
                'steps': [
                    {'range': [0, 0.3], 'color': '#e74c3c'},
                    {'range': [0.3, 0.6], 'color': '#f39c12'},
                    {'range': [0.6, 1], 'color': '#2ecc71'},
                ]
            }
        ))
        fig_support.update_layout(paper_bgcolor="#0E1117", font_color="white")
        st.plotly_chart(fig_support, use_container_width=True)


