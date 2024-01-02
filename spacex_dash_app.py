# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', 
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),
    
    # Pie chart for Success vs Failed launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),
    
    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        value=[min_payload, max_payload],
        marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 1000)}
    ),
    
    html.Br(),
    
    # Scatter chart for Payload vs Outcome
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for Pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df, names='Launch Site', hole=0.3, title='Total Success Launches By All Sites')
    else:
        df = spacex_df.loc[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(df, names='class', hole=0.3, title=f'Total Success Launches for Site {selected_site}')
    
    return fig

# Callback for Scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title='Payload vs. Outcome')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
