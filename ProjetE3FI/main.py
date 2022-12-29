import pandas as pd
import plotly.express as px
import json

import dash
from dash import dcc, html, Input, Output

isPrintingMapFrance = True  # Valeur modifiable pour afficher ou non la carte de France

## ===== Récupération des données depuis le site
url = "https://data.economie.gouv.fr/explore/dataset/prix-carburants-fichier-quotidien-test-ods/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"
data_prix_carburant = pd.read_csv(url, delimiter=";")

## ===== Fonction pour le graphique
def draw_histo_prix_carburant_par_nombre_and_carburant(num_bins_for_histo):
    
    fig = px.histogram(data_prix_carburant, x = "prix_valeur", color = "prix_nom", nbins = num_bins_for_histo, barmode="group", text_auto=True)#, title = "Prix du carburants sur ~70.000 stations en France")
    fig.update_xaxes(
        tickangle = 45,
        tickvals = [0, 0.5, 1, 1.5, 2, 2.5, 3],
        tickfont = dict(family = 'Rockwell', color = 'crimson', size = 14)
    )
    fig.update_yaxes(
        tickangle = 45,
        tickfont = dict(family = 'Rockwell', color = 'crimson', size = 14)
    )
    return fig

## ===== Masque pour l'ile de france
code_commune = data_prix_carburant["com_arm_code"]
nom_carburants = data_prix_carburant["prix_nom"].unique()  # Nom des carburants
nom_carburants = nom_carburants[~pd.isnull(nom_carburants)]  # Sans le nan
mask = (  ( code_commune.str.startswith('75') )    # Mask IDF
        | ( code_commune.str.startswith('77') )
        | ( code_commune.str.startswith('78') )
        | ( code_commune.str.startswith('91') )
        | ( code_commune.str.startswith('92') )
        | ( code_commune.str.startswith('93') )
        | ( code_commune.str.startswith('94') )
        | ( code_commune.str.startswith('95') ))

data_dupli_for_map_idf = data_prix_carburant[mask]
data_dupli_for_map_france = data_prix_carburant

## ===== MAP IDF

with open('idf.geojson') as response:
    ville_idf = json.load(response)

map_prix_carburant_idf = px.choropleth_mapbox(  data_dupli_for_map_idf,
                                                geojson = ville_idf,
                                                locations = "com_arm_code",
                                                color = "prix_valeur",
                                                featureidkey = "properties.code_commune",
                                                mapbox_style = "carto-positron",
                                                zoom = 4,
                                                center = {'lat': 47,'lon': 2}   )

map_prix_carburant_france = map_prix_carburant_idf  # Valeur simplement pour que la condition d'affichage de dash ne fasse pas de bug quand isPrintingMapFrance est fausse

if (isPrintingMapFrance):
    ## ===== MAP FRANCE
    with open('a-com2022.json') as response:
        ville_france = json.load(response)

    map_prix_carburant_france = px.choropleth_mapbox(   data_dupli_for_map_france,
                                                        geojson = ville_france,
                                                        locations = "com_arm_code",
                                                        color = "prix_valeur",
                                                        featureidkey = "properties.codgeo",
                                                        mapbox_style = "carto-positron",
                                                        zoom = 4,
                                                        center = {'lat': 47,'lon': 2}   )

if __name__ == '__main__':

    app = dash.Dash(__name__)

    ### ====== FIGURES DANS HTML ====== ###

    num_bins = 300

    fig = draw_histo_prix_carburant_par_nombre_and_carburant(num_bins)

    app.layout = html.Div(children=[

        html.Div(children=[
                    html.H1(
                        children = "Nombre de stations en france en fonction du prix des carburants à la vente",
                        style = {'textAlign': 'center', 'font-size': "35px", 'text-decoration': 'underline', 'color': '#2fc1fa'}
                    ),
                    html.Br(),
                    html.H1(
                        children = "(sur un total de plus de 7000 stations)",
                        style = {'textAlign': 'center', 'margin-bottom': '5%', 'margin-top': '-1.5%', 'font-size': "35px", 'text-decoration': 'underline', 'color': '#2fc1fa'}
                    ),
                ],
        ),
        
        # html.H1(children = "Nombre de stations en france en fonction du prix des carburants à la vente" + html.Br() + "(sur un total de plus de 7000 stations)",
        #         style = {'textAlign': 'center', 'margin-bottom': '5%', 'font-size': "35px", 'text-decoration': 'underline', 'color': '#2fc1fa'}),

        html.P(children = "Nombre de bins pour l'histogramme",
                style = {'margin-left': '1.5%', 'font-weight': "bold",'text-decoration': 'underline', 'font-size': "18px"}),

        dcc.Slider(
            min = 6,
            max = 600,
            step = 100,
            value = 300,
            id = "Bins_for_histo_prix_carbu"
        ),

        dcc.Graph(
            id = 'graph_histo_prix_carbu',
            figure = fig
        ),

        html.H1(children = 'Carte du prix du carburant (le plus cher) en Ile de France',
                style = {'textAlign': 'center','font-size': "35px", 'text-decoration': 'underline', 'color': '#2fc1fa'}),

        html.P(children = "Choisissez un carburant :",
                style = {'margin-left': '1.5%', 'font-weight': "bold",'text-decoration': 'underline', 'font-size': "18px"}),

        dcc.Dropdown(
            id="dropdown-carburant-idf",
            options=[{"label": c, "value": c} for c in nom_carburants],
            value="Gazole"
        ),

        dcc.Graph(
            id = "map-prix-carburant-idf",
            figure = map_prix_carburant_idf
        ),

        html.Div(children=[

            html.H1(children = 'Carte du prix du carburant (le plus cher) en France',
                    style = {'textAlign': 'center','font-size': "35px", 'text-decoration': 'underline', 'color': '#2fc1fa'}),

            html.P(children = "Choisissez un carburant :",
                    style = {'margin-left': '1.5%', 'font-weight': "bold",'text-decoration': 'underline', 'font-size': "18px"}),

            dcc.Dropdown(
                id="dropdown-carburant-france",
                options=[{"label": c, "value": c} for c in nom_carburants],
                value="Gazole"
            ),

            dcc.Graph(
                id = "map-prix-carburant-france",
                figure = map_prix_carburant_france
            )
        ], style={"display": "block" if isPrintingMapFrance else "none"})  # Affiche la carte FRANCE uniquement si la variable isPrintingMapFrance est à True
    ])

    # Graphique
    @app.callback( 
        Output('graph_histo_prix_carbu', 'figure'),
        Input('Bins_for_histo_prix_carbu', 'value')
    )
    def update_figure(value):
        fig = draw_histo_prix_carburant_par_nombre_and_carburant(value)
        return fig

    # Map IDF
    @app.callback(
        Output("map-prix-carburant-idf", "figure"),
        [Input("dropdown-carburant-idf", "value")]
    )
    def update_map(selected_carburant):
        data_dupli_for_map_idf_filtered = data_dupli_for_map_idf[
            data_dupli_for_map_idf["prix_nom"] == selected_carburant
        ]
        fig = px.choropleth_mapbox(
            data_dupli_for_map_idf_filtered,
            geojson=ville_idf,
            locations="com_arm_code",
            color="prix_valeur",
            featureidkey="properties.code_commune",
            mapbox_style="carto-positron",
            zoom=4,
            center={"lat": 47, "lon": 2},
        )
        return fig

    # Map FRANCE
    if (isPrintingMapFrance):
        @app.callback(
            Output("map-prix-carburant-france", "figure"),
            [Input("dropdown-carburant-france", "value")]
        )
        def update_map(selected_carburant):
            data_dupli_for_map_france_filtered = data_dupli_for_map_france[
                data_dupli_for_map_france["prix_nom"] == selected_carburant
            ]
            fig = px.choropleth_mapbox(
                data_dupli_for_map_france_filtered,
                geojson = ville_france,
                locations = "com_arm_code",
                color = "prix_valeur",
                featureidkey = "properties.codgeo",
                mapbox_style = "carto-positron",
                zoom = 4,
                center = {'lat': 47,'lon': 2},
            )
            return fig

    ### ====== FIN FIGURES DANS HTML ====== ###

    app.run_server(debug=True)