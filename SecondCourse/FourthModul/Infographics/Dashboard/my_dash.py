from dash import dcc, html, Input, Output, Dash, no_update
import plotly.express as px
import plotly.graph_objects as go

# Load data
df = px.data.gapminder()
available_countries = df['country'].unique()
available_years = sorted(df['year'].unique())
numeric_measures = ['lifeExp', 'pop', 'gdpPercap']

# Better labels for measures
measure_labels = {
    'lifeExp': 'Продолжительность жизни',
    'pop': 'Население',
    'gdpPercap': 'ВВП на душу населения'
}

# External stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap'
]

application = Dash(__name__, external_stylesheets=external_stylesheets)

# Color scheme
colors = {
    'background': '#f9f9f9',
    'text': '#333',
    'panel': '#ffffff',
    'accent': '#119DFF',
    'secondary': '#7FDBFF'
}

# Base styles
base_style = {
    'fontFamily': 'Roboto, sans-serif',
    'color': colors['text']
}

panel_style = {
    'backgroundColor': colors['panel'],
    'borderRadius': '8px',
    'padding': '15px',
    'boxShadow': '0 2px 5px rgba(0,0,0,0.1)',
    'marginBottom': '20px'
}

dropdown_style = {
    'marginBottom': '15px',
    'width': '100%'
}

# Default country
default_country = ['Costa Rica']

# Layout
application.layout = html.Div([
    # Header
    html.Div([
        html.H1("Интерактивная панель Gapminder", 
                style={'textAlign': 'center', 'color': colors['accent'], 'marginBottom': '30px'})
    ]),
    
    # Controls container
    html.Div([
        # Left controls panel
        html.Div([
            # Line chart controls
            html.Div([
                html.H4("Линейный график", style={'color': colors['accent']}),
                html.Label("Выберите страны:"),
                dcc.Dropdown(
                    id='line-country-dropdown',
                    options=[{'label': c, 'value': c} for c in available_countries],
                    multi=True,
                    placeholder="Выберите страны",
                    value=default_country,
                    style=dropdown_style
                ),
                html.Label("Выберите показатель:"),
                dcc.Dropdown(
                    id='line-yaxis-dropdown',
                    options=[{'label': measure_labels[m], 'value': m} for m in numeric_measures],
                    value='lifeExp',
                    placeholder="Выберите меру для оси Y",
                    style=dropdown_style
                )
            ], style=panel_style),
            
            # Year slider
            html.Div([
                html.H4("Временной период", style={'color': colors['accent']}),
                html.Label(f"Выберите год ({min(available_years)}-{max(available_years)}):"),
                html.Div([
                    html.Div(id='year-display', style={'textAlign': 'center', 'fontSize': '20px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.Slider(
                        id='year-slider',
                        min=min(available_years),
                        max=max(available_years),
                        step=5,
                        marks={str(year): str(year) for year in available_years},
                        value=min(available_years),
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={'padding': '10px 0'})
            ], style=panel_style),
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        # Right controls panel
        html.Div([
            # Bubble chart controls
            html.Div([
                html.H4("Настройки пузырьковой диаграммы", style={'color': colors['accent']}),
                html.Div([
                    html.Div([
                        html.Label("Ось X:"),
                        dcc.Dropdown(
                            id='bubble-x-dropdown',
                            options=[{'label': measure_labels[m], 'value': m} for m in numeric_measures],
                            value='gdpPercap',
                            style=dropdown_style
                        )
                    ], style={'width': '33%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    html.Div([
                        html.Label("Ось Y:"),
                        dcc.Dropdown(
                            id='bubble-y-dropdown',
                            options=[{'label': measure_labels[m], 'value': m} for m in numeric_measures],
                            value='lifeExp',
                            style=dropdown_style
                        )
                    ], style={'width': '33%', 'display': 'inline-block', 'paddingRight': '10px'}),
                    html.Div([
                        html.Label("Размер пузырька:"),
                        dcc.Dropdown(
                            id='bubble-size-dropdown',
                            options=[{'label': measure_labels[m], 'value': m} for m in numeric_measures],
                            value='pop',
                            style=dropdown_style
                        )
                    ], style={'width': '33%', 'display': 'inline-block'})
                ])
            ], style=panel_style),
            
            # Additional controls can be added here
            html.Div([
                html.H4("Визуальные настройки", style={'color': colors['accent']}),
                html.Div([
                    html.Div([
                        html.Label("Тема графиков:"),
                        dcc.RadioItems(
                            id='theme-selector',
                            options=[
                                {'label': 'Светлая', 'value': 'light'},
                                {'label': 'Темная', 'value': 'dark'},
                                {'label': 'Цветная', 'value': 'colorful'}
                            ],
                            value='light',
                            labelStyle={'display': 'inline-block', 'marginRight': '15px'}
                        )
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label("Показать легенду:"),
                        dcc.Checklist(
                            id='show-legend',
                            options=[{'label': 'Вкл', 'value': 'show'}],
                            value=['show']
                        )
                    ], style={'width': '50%', 'display': 'inline-block'})
                ])
            ], style=panel_style)
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
    ], style={'marginBottom': '20px'}),
    
    # Charts container - заменяем ResponsiveGridLayout на обычную сетку для надежности
    html.Div([
        # Верхний ряд графиков
        html.Div([
            # Пузырьковая диаграмма
            html.Div([
                html.Div("Пузырьковая диаграмма", className='chart-title'),
                dcc.Graph(id='bubble-chart', className='dash-graph', style={'height': '400px'})
            ], className='chart-container', style={'width': '50%', 'display': 'inline-block', 'padding': '10px'}),
            
            # Линейный график
            html.Div([
                html.Div("Линейный график", className='chart-title'),
                dcc.Graph(id='line-chart', className='dash-graph', style={'height': '400px'})
            ], className='chart-container', style={'width': '50%', 'display': 'inline-block', 'padding': '10px'})
        ]),
        
        # Нижний ряд графиков
        html.Div([
            # Топ-15 стран
            html.Div([
                html.Div("Топ-15 стран по населению", className='chart-title'),
                dcc.Graph(id='top15-chart', className='dash-graph', style={'height': '400px'})
            ], className='chart-container', style={'width': '65%', 'display': 'inline-block', 'padding': '10px'}),
            
            # Круговая диаграмма
            html.Div([
                html.Div("Распределение населения по континентам", className='chart-title'),
                dcc.Graph(id='pie-chart', className='dash-graph', style={'height': '400px'})
            ], className='chart-container', style={'width': '35%', 'display': 'inline-block', 'padding': '10px'})
        ])
    ]),
    
    # Footer
    html.Footer([
        html.Hr(),
        html.P("Данные предоставлены проектом Gapminder", style={'textAlign': 'center'})
    ])
], style={'padding': '20px', 'backgroundColor': colors['background'], **base_style})

# Add custom CSS
application.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Gapminder Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            .chart-container {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 10px;
                overflow: hidden;
            }
            .chart-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #119DFF;
            }
            .dash-graph {
                width: 100%;
            }
            .dash-dropdown .Select-control {
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            .dash-dropdown .Select-control:hover {
                border-color: #119DFF;
            }
            .dash-slider .rc-slider-track {
                background-color: #119DFF;
            }
            .dash-slider .rc-slider-handle {
                border-color: #119DFF;
            }
            .dash-slider .rc-slider-handle:hover {
                border-color: #007ACC;
            }
            .dash-slider .rc-slider-handle:active {
                border-color: #007ACC;
                box-shadow: 0 0 5px #119DFF;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callbacks
@application.callback(
    Output('year-display', 'children'),
    Input('year-slider', 'value')
)
def update_year_display(year):
    return f"Выбранный год: {year}"

@application.callback(
    Output('line-chart', 'figure'),
    Input('line-country-dropdown', 'value'),
    Input('line-yaxis-dropdown', 'value'),
    Input('theme-selector', 'value'),
    Input('show-legend', 'value')
)
def update_line_chart(selected_countries, y_measure, theme, show_legend):
    if not selected_countries:
        # Return empty figure if no countries selected
        fig = go.Figure()
        fig.update_layout(title="Выберите страны для отображения данных")
        return fig
    
    filtered_df = df[df['country'].isin(selected_countries)]
    
    # Create figure
    fig = px.line(filtered_df, x='year', y=y_measure, color='country',
                  title=f"{measure_labels.get(y_measure, y_measure)} по годам")
    
    # Apply styling based on theme
    template = get_theme_template(theme)
    fig.update_layout(template=template)
    
    # Show/hide legend
    fig.update_layout(showlegend='show' in show_legend)
    
    # Enhance traces
    fig.update_traces(mode='lines+markers', 
                      marker=dict(size=8, opacity=0.8),
                      line=dict(width=2))
    
    # Improve layout
    fig.update_layout(
        xaxis_title="Год",
        yaxis_title=measure_labels.get(y_measure, y_measure),
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

@application.callback(
    Output('year-slider', 'value'),
    Input('line-chart', 'clickData')
)
def update_slider_on_click(clickData):
    if clickData:
        return clickData['points'][0]['x']
    return no_update

@application.callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-x-dropdown', 'value'),
    Input('bubble-y-dropdown', 'value'),
    Input('bubble-size-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('theme-selector', 'value'),
    Input('show-legend', 'value')
)
def update_bubble_chart(x_measure, y_measure, size_measure, year, theme, show_legend):
    filtered_df = df[df['year'] == year]
    
    # Create bubble chart
    fig = px.scatter(filtered_df, 
                     x=x_measure, 
                     y=y_measure, 
                     size=size_measure, 
                     color='continent',
                     hover_name='country',
                     log_x=x_measure == 'gdpPercap',  # Use log scale for GDP
                     size_max=45,
                     opacity=0.7,
                     title=f"Пузырьковая диаграмма ({year})")
    
    # Apply styling based on theme
    template = get_theme_template(theme)
    fig.update_layout(template=template)
    
    # Show/hide legend
    fig.update_layout(showlegend='show' in show_legend)
    
    # Improve layout
    fig.update_layout(
        xaxis_title=measure_labels.get(x_measure, x_measure),
        yaxis_title=measure_labels.get(y_measure, y_measure),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add trendline
    if len(filtered_df) > 1:
        fig.update_layout(
            shapes=[
                dict(
                    type='line',
                    xref='x', yref='y',
                    x0=filtered_df[x_measure].min(),
                    y0=filtered_df[y_measure].min(),
                    x1=filtered_df[x_measure].max(),
                    y1=filtered_df[y_measure].max(),
                    opacity=0.2,
                    line=dict(color='black', width=1)
                )
            ]
        )
    
    return fig

@application.callback(
    Output('top15-chart', 'figure'),
    Input('year-slider', 'value'),
    Input('theme-selector', 'value'),
    Input('show-legend', 'value')
)
def update_top15_chart(year, theme, show_legend):
    filtered_df = df[df['year'] == year].sort_values(by='pop', ascending=False).head(15)
    
    # Create figure
    fig = px.bar(filtered_df, 
                 x='country', 
                 y='pop', 
                 color='continent',
                 title=f"Топ-15 стран по населению ({year})")
    
    # Apply styling based on theme
    template = get_theme_template(theme)
    fig.update_layout(template=template)
    
    # Show/hide legend
    fig.update_layout(showlegend='show' in show_legend)
    
    # Improve layout
    fig.update_layout(
        xaxis_title="Страна",
        yaxis_title="Население",
        xaxis={'categoryorder': 'total descending'},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Format y-axis to show billions/millions
    fig.update_yaxes(
        ticksuffix="",
        tickformat=".2s",
        showgrid=True
    )
    
    # Add value labels on top of bars
    fig.update_traces(
        texttemplate='%{y:.2s}',
        textposition='outside'
    )
    
    return fig

@application.callback(
    Output('pie-chart', 'figure'),
    Input('year-slider', 'value'),
    Input('theme-selector', 'value'),
    Input('show-legend', 'value')
)
def update_pie_chart(year, theme, show_legend):
    filtered_df = df[df['year'] == year]
    pop_by_continent = filtered_df.groupby('continent', as_index=False).agg(
        population=('pop', 'sum'),
        countries=('country', 'nunique')
    )
    
    # Create pie chart
    fig = px.pie(pop_by_continent, 
                 names='continent', 
                 values='population',
                 title=f"Распределение населения по континентам ({year})",
                 hover_data=['countries'])
    
    # Apply styling based on theme
    template = get_theme_template(theme)
    fig.update_layout(template=template)
    
    # Show/hide legend
    fig.update_layout(showlegend='show' in show_legend)
    
    # Improve layout
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Add percentage and values in hover
    fig.update_traces(
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        textfont_size=12,
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    return fig

def get_theme_template(theme):
    """Return the appropriate plotly template based on theme selection"""
    if theme == 'dark':
        return 'plotly_dark'
    elif theme == 'colorful':
        return 'ggplot2'  # Более безопасный и стабильный цветной шаблон
    else:  # light theme
        return 'plotly_white'

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=10000)