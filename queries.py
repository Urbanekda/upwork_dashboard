# This module includes function definitions to query data and build charts
import plotly.express as px
import numpy as np


# Map data for the choropleth visualization
def map_data(df):
    # Create a map of the number of jobs per country
    map = df.groupby('ISO_Code').size().reset_index(name="Count")
    map['Count'] = map['Count'].astype(int)

    conditions = [
        (map['Count'] >= 1000),
        (map['Count'] >= 500) & (map['Count'] < 1000),
        (map['Count'] >= 100) & (map['Count'] < 500),
        (map['Count'] >= 50) & (map['Count'] < 100),
        (map['Count'] < 50)
    ]

    values = ['1000+', '500-999', '100-499', '50-99', '1-49']
    default = "Data Missing"

    map['Count_Category'] = np.select(conditions, values, default=default)
    
    return map

def choropleth_chart(data):
    # Create a choropleth chart
    fig = px.choropleth(data, 
                        locations="ISO_Code", 
                        locationmode='ISO-3', 
                        color="Count_Category", 
                        hover_name="ISO_Code",
                        height=350,
                        hover_data=["Count"],
                        color_discrete_sequence=px.colors.sequential.YlOrRd_r,
                        category_orders={"Count_Category": ['1000+', '500-999', '100-499', '50-99', '1-49']},
                        labels={'Count_Category': 'Number of Jobs',
                               'Count': 'Exact Count'}
                        )
    fig.update_geos(projection_type="natural earth", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig
# Average spending by country
def spending_data(df):
    # Calculate the average spending by country
    average_spending = df.groupby('Client_Country').agg({
        'Spent($)': ['count', 'mean']
    }).reset_index()

    average_spending.columns = ['Client_Country', 'Job_Count', 'Average_Spent']
    average_spending['Average_Spent'] = average_spending['Average_Spent'].round(2)
    average_spending['Job_Count'] = average_spending['Job_Count'].astype(int)

    # Filter countries with at least 30 jobs
    average_spending = average_spending[average_spending['Job_Count'] >= 30].sort_values(by='Average_Spent')
    return average_spending

def spending_chart(data):
    fig = px.treemap(data, 
                     path=[px.Constant("world"), 'Client_Country'], 
                     values='Average_Spent',
                     color='Average_Spent',
                     color_continuous_scale='rdbu_r',
                     labels={'Average_Spent': 'Average Spending ($)'})
    
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    fig.update_traces(textinfo='label', textfont=dict(size=14))
    
    return fig
    
# Data for the skill category sunburst visualization
def sunburst_data(df, cutoff):
    # Query sunburst data
    sunburst = df[["Search_Keyword", "Category_1"]]
    sunburst["Count"] = 1
    sunburst.dropna(inplace=True)
    
    category_keyword_counts = sunburst.groupby(['Search_Keyword', 'Category_1']).size().reset_index(name='Count')

    # Filter to keep only combinations with at least x number of occurencies
    filtered_categories = category_keyword_counts[category_keyword_counts['Count'] >= cutoff]

    # Filter the original dataframe to keep only the valid combinations
    sunburst = sunburst.merge(
        filtered_categories[['Search_Keyword', 'Category_1']], 
        on=['Search_Keyword', 'Category_1'],
        how='inner'
    )

    # Recompute the counts after filtering
    sunburst['Count'] = 1

    return sunburst

def sunburst_chart(data):
    fig = px.sunburst(
    data,
    path=['Search_Keyword', 'Category_1'],
    values='Count',
    color='Category_1',
    color_discrete_sequence=px.colors.qualitative.Set1,
    )

    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),)

    return fig

# Data for the best paying job skills
def wage_data(df, cutoff):
    # Group data
    wage = df.groupby(['Category_1', 'Search_Keyword']).agg({
    'Hourly_rate': ['mean', 'count']
    }).reset_index()

    wage.drop(wage[wage['Hourly_rate']['count'] < cutoff].index, inplace=True)

    # Flatten column names
    wage.columns = ['Category_1', 'Search_Keyword', 'Hourly_rate_mean', 'Job_Count']

    # Sort by hourly rate in descending order
    wage = wage.sort_values(by='Hourly_rate_mean', ascending=True)
    return wage

def wage_chart(data):
    bar = px.bar(data,
       x='Hourly_rate_mean',
       y='Category_1',
       color='Search_Keyword',
       orientation='h',
       color_discrete_sequence=px.colors.qualitative.Set1,
    )

    bar.update_layout(
    xaxis_title="Average Hourly Rate (USD)",
    yaxis_title=None,
    showlegend=True,
    legend_title="Job Category",
    margin=dict(t=0, l=0, r=0, b=0),
    )
    return bar
# Data for the competition bubble chart
def competition_data(df, cutoff):
    competition = df.groupby("Category_1").agg({
        'Applicants_Num': ["mean", "count"]
    }).reset_index()

    competition.columns = ['Category_1', 'Avg_Applicants_Num', 'Job_Count']
    competition = competition[competition["Job_Count"] > cutoff]

    competition["Opportunity Index"] = 1/(competition["Avg_Applicants_Num"] / competition["Job_Count"])

    # Normalize the competition index
    competition["Opportunity Index"] = (competition["Opportunity Index"] - competition["Opportunity Index"].min()) / (competition["Opportunity Index"].max() - competition["Opportunity Index"].min())

    return competition

def competition_chart(data):
    fig = px.scatter(
    data,
    x="Job_Count",
    y="Avg_Applicants_Num",
    size="Opportunity Index",
    color="Opportunity Index",
    labels={
        "Opportunity Index": "Opportunity",},
    hover_name="Category_1",
    size_max=60,
    color_continuous_scale=px.colors.sequential.Viridis,
    )
    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=2, color='DarkSlateGrey')))
    fig.update_layout(
    xaxis_title="Number of Jobs",
    yaxis_title="Average Number of Applicants",
    xaxis_type="log",
    yaxis_type="log",
    )

    return fig