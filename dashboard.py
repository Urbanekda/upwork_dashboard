import streamlit as st
import pandas as pd
import plotly.express as px
from queries import *

# Page configuration set to wide
st.set_page_config(
    page_title="UpWork Jobs",
    page_icon=":bar_chart:",
    layout="wide",
)

st.logo("./upwork_logo.png", size="large")

# Columns to be shown in the interactive dataframe
columns_to_show = [
    "Search_Keyword", 
    "Category_1", 
    "Category_2",
    "Hourly_rate", 
    "Job_Cost", 
    "Rating", 
    "Client_Country",
    "EX_level_demand",
    "Time_Limitation",
    "Enterprise_Client",
    "Payment_type"
]

# Load the cleaned dataset and cache the data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df = load_data("upwork_clean.csv")

st.html("<h1>💻 UpWork Jobs Analysis</h1>")
st.markdown('''
            This dashboard uses [data scraped](https://www.kaggle.com/datasets/ahmedmyalo/upwork-freelance-jobs-60k) from the freelancing platform [UpWork](https://upwork.com) (2023). It provides insights into **job listings**, their categories, geographical distribution, wage, and other relevant metrics.
            ''')

# Layout
# Top row - choropleth map and spending chart
st.html("<h3>Filtering<h3>")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1: selected_category = st.multiselect(
            "Select Job Categories",
            options=sorted(df['Search_Keyword'].unique()),
            default=[]
        )
with filter_col2: selected_experience = st.multiselect(
            "Select Experience Level",
            options=(df['EX_level_demand'].unique()),
            default=[]
        )

with filter_col3: selected_country = st.multiselect(
            "Select Client Country",
            options=(df['Client_Country'].unique()),
            default=[]
    )
     

# Define filtering options
filtered_df = df.copy()
if selected_category:
        filtered_df = filtered_df[filtered_df['Search_Keyword'].isin(selected_category)]
if selected_experience:
        filtered_df = filtered_df[filtered_df['EX_level_demand'].isin(selected_experience)]
if selected_country:
        filtered_df = filtered_df[filtered_df['Client_Country'].isin(selected_country)]
    
# Fulltext search
with filter_col4: search_term = st.text_input("Search in all columns", "")
if search_term:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda x: x.str.contains(search_term, case=False)
            ).any(axis=1)
        ]

col1, col2 = st.columns([6,4])

with col1:
    with st.container(height=490):
        st.plotly_chart(
            choropleth_chart(map_data(filtered_df)),
            use_container_width=True)

        # Metrics row under the map
        met1, met2, met3, met4 = st.columns(4)
        with met1:
            st.metric("📊 Total Jobs", value=filtered_df.shape[0])
        with met2:
            st.metric("🧑‍💻 Average Applicants", value=filtered_df['Applicants_Num'].mean().round(2))
        with met3:
            st.metric("💼 Categories", value=filtered_df['Category_1'].nunique())
        with met4:
            st.metric("💰 Hourly Rate (USD)", value=filtered_df["Hourly_rate"].mean().round(2))

with col2:
    with st.container(height=490):
        st.plotly_chart(
            spending_chart(spending_data(filtered_df)),
            use_container_width=True)

# Dataframe in expandable section
with st.expander("Detailed UpWork Listings Data"):
    st.dataframe(
        filtered_df[columns_to_show],
        column_config={
            "Search_Keyword": st.column_config.TextColumn(
                "🔍 Job Category",
                width="medium",
            ),
            "Category_1": st.column_config.TextColumn(
                "💼 Skill Area",
                width="medium",
            ),
            "Hourly_rate": st.column_config.NumberColumn(
                "💰 Hourly Rate",
                format="$%.2f",
                help="Hourly rate in USD",
            ),
            "Job_Cost": st.column_config.NumberColumn(
                "💵 Total Job Cost",
                format="$%.2f",
                help="Total project budget in USD",
            ),
            "Rating": st.column_config.ProgressColumn(
                "⭐ Client Rating",
                format="%.1f",
                min_value=0,
                max_value=5,
            ),
            "EX_level_demand": st.column_config.TextColumn(
                "👨‍💻 Required Expertise",
                help="Required experience level",
            ),
            "Time_Limitation": st.column_config.TextColumn(
                "⏱️ Time Limitation (months)",
                help="Expected project duration",
            ),
            "Enterprise_Client": st.column_config.TextColumn(
                "🏢 Client Type",
                help="Enterprise or Individual client",
            ),
            "Payment_type": st.column_config.TextColumn(
                "💳 Payment Type",
                help="Fixed price or hourly rate",
            ),
            "Client_Country": st.column_config.TextColumn(
                "🌍 Client Country",
                help="Country of the client",
            ),
            "Applicants_Num": st.column_config.NumberColumn(
                "👥 Number of Applicants",
                help="Number of applicants for the job",
            ),
            "Category_2": st.column_config.TextColumn(
                "🔍 Skill Subcategory",
                help="Specific job subcategory category",
            ),
        },
        hide_index=True,
        height=400,
        use_container_width=True
    )

st.html("<h3>Dynamic Configuration<h3>")

# Only categories above certain occurence will be shown (e.g. 1000 occurences will show less categories than 100)
cutoff = st.slider("Filter by the number of occurences", 1, 1000, 150)

# Bottom row - skills, job categories, wage and competition charts
col3, col4, col5 = st.columns([3,3,4])

with col3:
    with st.container(height=500):
        st.plotly_chart(sunburst_chart(sunburst_data(filtered_df, cutoff)),
                         use_container_width=True)
        

with col4:
    with st.container(height=500):
        st.plotly_chart(
            wage_chart(wage_data(filtered_df, cutoff)),
            use_container_width=True)
        
with col5:
    with st.container(height=500):
        st.plotly_chart(
            competition_chart(competition_data(filtered_df, cutoff)),
            use_container_width=True)


