import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import os


## Loading the dataset:

# Go up one level from src to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "Dataset.csv"))

#Initializing variables:
years= df['Year'].unique().tolist()
countries= df['Country'].unique().tolist()
default_year= max(years)
default_country= 'United States'
features= ['Log GDP Per Capita', 'Social Support', 'Freedom To Make Life Choices', 'Healthy Life Expectancy At Birth', 'Life Ladder']



#Initializing an app:
app= dash.Dash(__name__)
server = app.server

app.layout=html.Div(
    children=[
        html.H1("World Happiness Dashboard", style={'textAlign': 'center', 'font-size':40}),

        dcc.Tabs(
            id='main-tab', 
            children=[
                dcc.Tab(label='Global Overview',
                        children=[
                            html.Div(
                                [
                                    dcc.Dropdown(id='input-year', options=[{'label': year, 'value': year} for year in years], value=default_year, placeholder="Select a year", style={"width": "50%", 'height':'40px'}),
                                    html.Div(
                                        id='kpi-row',
                                        style={'display': 'flex', 'width':"50%", 'padding':'8px', 'gap': '12px'})
                                ],
                                style={'display':'flex', 'justify-content': 'space-between', 'alignItems':'center'}
                            ),

                            html.Br(),

                            html.Br(),
                            html.Div(dcc.Graph(id='world-map'), style={'height':'600px'}),

                            html.Div([
                                dcc.Graph(id='top-5'),
                                dcc.Graph(id='least-5')
                            ], 
                            style={'display':'flex', 'justify-content':'space-between', 'alignItems':'center'}
                            ),
                            html.Br(),
                            html.Br()
                        ]),

                dcc.Tab(label='Country Overview',
                        children=[
                            html.Div(
                                [
                                    dcc.Dropdown(id='select-country', options=[{'label': country, 'value': country} for country in countries], value=default_country, placeholder='Enter a country', style={'height': '40px', 'width':'49%'}),
                                    html.Div(id='kpi-row2', style={'display': 'flex', 'width':'49%', 'padding':'8px', 'gap': '12px'})
                                ],
                                style={'display': 'flex', 'justify-content': 'space-between', 'alignItems': 'center'}
                            ),

                            html.Div(dcc.Graph(id='trend-line'), style={'height': '350px', 'alignItems': 'center', 'justify-content':'center'}),

                            html.Div(
                                children=[
                                    dcc.Dropdown(id='feature-list', options=[{'label': feature, 'value': feature} for feature in features], value='Healthy Life Expectancy At Birth', style={'width': '50%'}),
                                    html.Div(
                                        children=[
                                            dcc.Graph(id='factor-trend', style={'width':'50%'}),
                                            dcc.Graph(id='feature-index-scatter', style={'width':'50%'})
                                        ],
                                        style={'display':'flex', 'justify-content': 'space-between', 'alignItems': 'center'}
                                    )
                                ],
                            ),
                            html.Br(),
                            html.Br()
                ])
            ]
        )
    ]
)



#Callback functions:
@app.callback([
    Output(component_id='world-map', component_property='figure'),
    Output(component_id='top-5', component_property='figure'),
    Output(component_id='least-5', component_property='figure'),
    Output(component_id='kpi-row', component_property='children'),
],
Input(component_id="input-year", component_property="value")
)
def update_layout(selected_year):       #Plots and cards functions:
    data=df[df['Year']==selected_year]


    ##Choropleth:
    choro_fig = px.choropleth(
    data_frame=data,
    locations='Country',
    locationmode='country names',
    color='Index',
    hover_name='Country',
    labels={'Index': 'Happiness Index'},
    color_continuous_scale='Plasma'
    )


    choro_fig.update_layout(
    title={
        'text': f"World Happiness Index for {selected_year}",
        'x': 0.5,          # 0 = left, 0.5 = center, 1 = right
        'xanchor': 'center'
    }
    )

    #Rankings:
    ranked_data=data.sort_values(by='Index', ascending=True).dropna()
    
    # Top 5 happiest (highest Index values)
    top_5= px.bar(
        data_frame=ranked_data.tail(10),
        x='Country',
        y='Index'
    )
    top_5.update_layout(
    title={
        'text':f"Top 5 Happiest Countries in {selected_year}",
        'x': 0.5,
        'xanchor': 'center'
    }
)

    # Least 5 happiest (lowest Index values)
    least_5= px.bar(
        data_frame=ranked_data.head(10),
        x='Country',
        y='Index'
    )
    least_5.update_layout(
    title={
        'text': f"Least 5 Happiest Countries in {selected_year}",
        'x': 0.5,
        'xanchor': 'center'
    }
)

    #For KPIs: average, max, min, and total count for increase & decrease
    avg_score= data['Index'].mean()
    max_score= data['Index'].max()
    min_score= data['Index'].min()
    prev_year=selected_year-1
    new = df[['Index', 'Rank', 'Year', 'Country']]
    new = new[new['Year'].isin([selected_year, prev_year])]
    diff = new.sort_values(['Country', 'Year']).groupby('Country')['Index'].diff()
    inc = 0
    dec = 0
    for i in diff:
        if pd.notna(i):
            if i > 0:
                inc += 1
            elif i < 0:
                dec += 1
    compare = f"{inc} ↑ / {dec} ↓ (countries with data in both years)"
    kpi_children=[
        html.Div([
            html.H4("Global Average: ", style={'margin': '0'}),
            html.P(f"{avg_score:.2f}",style={"fontSize": "16px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "160px", "textAlign": "center"}),
        html.Div([
            html.H5("Highest: ", style={'margin': '0'}),
            html.P(f"{max_score}",style={"fontSize": "16px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "160px", "textAlign": "center", 'alignItems':'center'}),
        html.Div([
            html.H5("Lowest: ", style={'margin': '0'}),
            html.P(f"{min_score}",style={"fontSize": "16px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "160px", "textAlign": "center"}),
        html.Div([
            html.H5("Changes from Prev. Year: ", style={'margin': '0'}),
            html.P(f"{compare}",style={"fontSize": "16px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "160px", "textAlign": "center"})
    ]
    return choro_fig, top_5, least_5, kpi_children





#Callback for Country-wise overview:
@app.callback(
    [
        Output(component_id='trend-line', component_property='figure'),
        Output(component_id='factor-trend', component_property='figure'),
        Output(component_id='feature-index-scatter', component_property='figure'),
        Output(component_id='kpi-row2', component_property='children')
    ],
    [
        Input(component_id='select-country', component_property='value'),
        Input(component_id='feature-list', component_property='value')
    ]
)
def country_plots(selected_country, feature):
    data= df[df['Country']==selected_country]

    #Trendline plot:
    trend_plot= px.line(data_frame=data, x='Year', y='Index')
    trend_plot.update_layout(title= {
        'text': f"Happiness Index Trend for {selected_country}",
        'x': 0.5,
        'xanchor': 'center'
    })


    #Factor Trend Line:
    factor_trend= px.line(data_frame=data, x='Year', y=feature)
    factor_trend.update_layout(
        title={
            'text':f"{selected_country}'s {feature} Variation Over Time",
            'x': 0.5,
            'xanchor': 'center'
        }
    )

    #Feature-Index scatter:
    scatter_fig= px.scatter(data_frame=data, x=feature, y='Index')
    corr_value = data['Index'].corr(data[feature])
    scatter_fig.add_annotation(
        x=data[feature].min(),
        y=data['Index'].max(),
        text=f"r = {corr_value:.2f}",
        showarrow=False,
        font=dict(size=12, color="black")
    )
    scatter_fig.update_layout(title={
        'text': f"Variation of Happiness Index with {feature}",
        'x': 0.5,
        'xanchor': 'center'
    })

    # KPIs for country overview
    current_index = data['Index'].iloc[-1] if len(data) > 0 else 0
    avg_index = data['Index'].mean()
    trend = "↑" if len(data) > 1 and data['Index'].iloc[-1] > data['Index'].iloc[0] else "↓"
    
    kpi_children2 = [
        html.Div([
            html.H5("Current Index: ", style={'margin': '0'}),
            html.P(f"{current_index:.2f}", style={"fontSize": "16px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "140px", "textAlign": "center"}),
        html.Div([
            html.H5("Average: ", style={'margin': '0'}),
            html.P(f"{avg_index:.2f}", style={"fontSize": "16px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "140px", "textAlign": "center"}),
        html.Div([
            html.H5("Overall Trend: ", style={'margin': '0'}),
            html.P(trend, style={"fontSize": "24px", "margin": "0"})
        ], style={"padding": "10px", "border": "1px solid #ddd", "borderRadius": "6px", "width": "140px", "textAlign": "center"})
    ]

    return trend_plot, factor_trend, scatter_fig, kpi_children2



#Run app:
if __name__ == "__main__":
    app.run(debug=True)