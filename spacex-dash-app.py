# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# ---- TASK 1: Dropdown（All + 各Launch Site） ----
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',  # default to ALL
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'width': '80%', 'margin': '0 auto'}
    ),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),

    # ---- TASK 3: RangeSlider ----
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, max=max_payload, step=1000,
        value=[min_payload, max_payload],
        marks={int(m): str(int(m)) for m in
               [min_payload, (min_payload+max_payload)/4, (min_payload+max_payload)/2,
                3*(min_payload+max_payload)/4, max_payload]}
    ),

    html.Br(),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ---- TASK 2: Callback for pie chart ----
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    # 全サイト: サイト別の成功数(class=1)を集計
    if selected_site == 'ALL':
        df_all = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df_all,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # 特定サイト: 成功 vs 失敗 の件数を円グラフ
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = df_site['class'].value_counts().rename({1: 'Success', 0: 'Failed'}).reset_index()
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(
            counts, names='Outcome', values='Count',
            title=f"Success vs. Failed for site: {selected_site}"
        )
    return fig

# ---- TASK 4: Callback for scatter chart ----
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    lo, hi = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= lo) & (spacex_df['Payload Mass (kg)'] <= hi)]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    # Booster Version Category が無い環境でも落ちないようにフォールバック
    color_col = 'Booster Version Category' if 'Booster Version Category' in df.columns else 'class'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)', y='class',
        color=color_col,
        title='Correlation between Payload and Success'
              + ('' if selected_site == 'ALL' else f' — {selected_site}'),
        hover_data=['Launch Site']
    )
    # y軸を0/1に見やすく
    fig.update_yaxes(tickmode='array', tickvals=[0, 1], ticktext=['Failed(0)', 'Success(1)'])
    return fig


# Run the app
if __name__ == '__main__':
    # app.run_server(debug=True) でもOK。あなたの環境に合わせて選択。
    app.run()
