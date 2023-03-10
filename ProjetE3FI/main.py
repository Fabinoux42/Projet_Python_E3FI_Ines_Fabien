import pandas as pd
import plotly.express as px
import json
import numpy as np
import importlib

import dash
from dash import dcc, html, Input, Output

isPrintingMapFrance = True  # Valeur modifiable pour afficher ou non la carte de France

name_missing_pack = {"pandas", "plotly.express", "importlib", "dash", "numpy"}  # Vérification des packages manquants
for name_pack in name_missing_pack:
    spec = importlib.util.find_spec(name_pack)
    if spec is None:
        print(f"Can't find {name_pack!r} package\n")

## ===== Récupération des données depuis le site
url = "https://data.economie.gouv.fr/explore/dataset/prix-carburants-fichier-quotidien-test-ods/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true"
data_prix_carburant = pd.read_csv(url, delimiter=";")

max_price = np.max(data_prix_carburant["prix_valeur"])
max_price = np.ceil(max_price * 2) / 2  # Arrondi au demi entier supérieur

## ===== Fonction pour le graphique
def draw_histo_prix_carburant_par_nombre_and_carburant(num_bins_for_histo):
    """
        Défini l'histogramme avec le nombre de bins voulu

        Args :
            num_bins_for_histo (int): Nombre de bins pour l'histogramme

        Returns:
            plotly.express.histogram: Retourne l'histogramme prêt à être injecté dans le dashboard
    """
    fig = px.histogram(data_prix_carburant, x = "prix_valeur", color = "prix_nom", nbins = num_bins_for_histo, barmode="group", text_auto=True)#, title = "Prix du carburants sur ~70.000 stations en France")
    fig.update_xaxes(
        tickangle = 45,
        tickvals = [i / 2 for i in range(0, (int)(max_price + 1) * 2)],  # Défini l'échelle en x pour l'histogramme en fonction de la plus haute valeur de carburant par pas de 0.5 euros
        tickfont = dict(family = 'Rockwell', color = 'crimson', size = 14)
    )
    fig.update_yaxes(
        tickangle = 45,
        tickfont = dict(family = 'Rockwell', color = 'crimson', size = 14)
    )
    fig.update_layout(
        xaxis_title = "Prix des carburants par tranches",
        yaxis_title = "Nombre de stations par tranches de prix",
        legend_title = "Carburants"
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
data_dupli_for_map_france = data_prix_carburant  # Uniquement pour ne pas que la carte de France pose problème au niveau terminal si isPrintingMapFrance est à False

## ===== MAP IDF

with open('Fichiers_Statiques/idf.geojson') as response:
    ville_idf = json.load(response)

map_prix_carburant_idf = px.choropleth_mapbox(  data_dupli_for_map_idf,
                                                geojson = ville_idf,
                                                locations = "com_arm_code",
                                                color = "prix_valeur",
                                                featureidkey = "properties.code_commune",
                                                mapbox_style = "carto-positron",
                                                zoom = 4,
                                                center = {'lat': 47,'lon': 2},  )

map_prix_carburant_idf.update_layout(
    legend_title = 'Prix du carburant' 
)

map_prix_carburant_france = map_prix_carburant_idf  # Valeur simplement pour que la condition d'affichage de dash ne fasse pas de bug quand isPrintingMapFrance est fausse

if (isPrintingMapFrance):
    ## ===== MAP FRANCE
    with open('Fichiers_Statiques/a-com2022.json') as response:
        ville_france = json.load(response)

    map_prix_carburant_france = px.choropleth_mapbox(   data_dupli_for_map_france,
                                                        geojson = ville_france,
                                                        locations = "com_arm_code",
                                                        color = "prix_valeur",
                                                        featureidkey = "properties.codgeo",
                                                        mapbox_style = "carto-positron",
                                                        zoom = 4,
                                                        center = {'lat': 47,'lon': 2}   )
    map_prix_carburant_france.update_layout(
        legend_title = 'Prix du carburant' 
    )            

if __name__ == '__main__':

    app = dash.Dash(__name__)

    ### ====== FIGURES DANS HTML ====== ###

    num_bins = 6

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

        html.P(children = "Nombre de bins pour l'histogramme :",
                style = {'margin-left': '1.5%', 'font-weight': "bold",'text-decoration': 'underline', 'font-size': "18px"}),

        dcc.Slider(
            min = 6,
            max = 600,
            step = 100,
            value = num_bins,
            id = "Bins_for_histo_prix_carbu"
        ),

        dcc.Graph(
            id = 'graph_histo_prix_carbu',
            figure = fig
        ),

        html.H1(children = 'Carte du prix du carburant (le plus cher) en Ile de France par communes',
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

            html.H1(children = 'Carte du prix du carburant (le plus cher) en France par communes',
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
        ], style={"display": "block" if isPrintingMapFrance else "none"}),  # Affiche la carte FRANCE uniquement si la variable isPrintingMapFrance est à True

        html.Div(children=[
            html.H4(
                children = 'Crédits :',
                style = {'margin-left': '1.5%', 'margin-top': '5%', 'font-weight': "bold", 'text-decoration': 'underline', 'font-size': "16px"}
            ),
            html.A(
                children = 'Inès Dakkak',
                style = {'margin-left': '1.5%', 'margin-top': '2%', 'font-weight': "bold", 'font-size': "16px"}
            ),
            html.Br(),
            html.A(
                children = 'Fabien Varoteaux-Lavigne',
                style = {'margin-left': '1.5%', 'font-weight': "bold", 'font-size': "16px"}
            )
        ])
        
    ])

    # Graphique
    @app.callback( 
        Output('graph_histo_prix_carbu', 'figure'),
        Input('Bins_for_histo_prix_carbu', 'value')
    )
    def update_figure(value):
        """
            Met à jour l'histogramme avec le nombre de bins voulu

            Args :
                value (int): Nombre de bins pour l'histogramme

            Returns:
                plotly.express.histogram: Retourne l'histogramme prêt à être mis à jour sur le dashboard
        """
        fig = draw_histo_prix_carburant_par_nombre_and_carburant(value)
        return fig

    # Map IDF
    @app.callback(
        Output("map-prix-carburant-idf", "figure"),
        [Input("dropdown-carburant-idf", "value")]
    )
    def update_map_idf(selected_carburant):
        """
            Met à jour la carte d'Ile de France avec le carburant choisi

            Args :
                selected_carburant (str): Carburant choisi

            Returns:
                plotly.express.choropleth_mapbox: Retourne la carte d'Ile de France prête à être mise à jour sur le dashboard
        """
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
        fig.update_layout(
            legend_title = 'Prix du carburant' 
        )
        return fig

    # Map FRANCE
    if (isPrintingMapFrance):
        @app.callback(
            Output("map-prix-carburant-france", "figure"),
            [Input("dropdown-carburant-france", "value")]
        )
        def update_map_france(selected_carburant):
            """
                Met à jour la carte de France avec le carburant choisi

                Args :
                    selected_carburant (str): Carburant choisi

                Returns:
                    plotly.express.choropleth_mapbox: Retourne la carte de France prête à être mise à jour sur le dashboard
            """
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
            fig.update_layout(
                legend_title = 'Prix du carburant' 
            )
            return fig

    ### ====== FIN FIGURES DANS HTML ====== ###

    app.run_server(debug=True)