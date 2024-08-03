# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for selecting launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'}
        ] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # Pie chart to show success rates
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # Scatter plot to show payload vs. success rate
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for updating the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        pie_data = spacex_df['class'].value_counts().reset_index()
        pie_data.columns = ['Success', 'Count']
        fig = px.pie(pie_data, names='Success', values='Count', title='Total Success Rate for All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        pie_data = filtered_df['class'].value_counts().reset_index()
        pie_data.columns = ['Success', 'Count']
        fig = px.pie(pie_data, names='Success', values='Count', title=f'Success Rate for {selected_site}')
    
    return fig

# Callback for updating the scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_plot(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
    
    filtered_df = filtered_df[
        (filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
        (filtered_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    scatter_fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Success vs. Payload Mass for {selected_site}',
        labels={'class': 'Launch Success'},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
