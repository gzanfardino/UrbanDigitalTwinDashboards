from geo_utils.risk_analysis import assign_risk_zone, color_map
import overpy
from collections import defaultdict
from dash import html, dcc
import dash_leaflet as dl
from dash.exceptions import PreventUpdate
from dash import callback_context





class RiskZonePlot:
    def __init__(self, bbox=None):
        self.api = overpy.Overpass()
        self.bbox = bbox or (9.13, 45.44, 9.25, 45.51)  # west, south, east, north
        self.result = None
        self.grouped_by_risk = defaultdict(list)
        self.building_options = []
        self.default_position = [45.47, 9.19]
        self.default_zoom = 15
        self._load_data()

    def _build_query(self):
        west, south, east, north = self.bbox
        return f"""
        (
          way["building"]({south},{west},{north},{east});
          >;
        );
        out body;
        """

    # Load data
    def _load_data(self):
        self.result = self.api.query(self._build_query())
        for way in self.result.ways:
            coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
            if coords[0] != coords[-1]:
                coords.append(coords[0])

            risk = assign_risk_zone(way.tags)
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "id": way.id,
                    "tags": way.tags,
                    "risk": risk,
                    "name": way.tags.get("name", "Unnamed")
                }
            }

            self.grouped_by_risk[risk].append(feature)
            self.building_options.append({
                "label": f"ID {way.id} - Risk: {risk}",
                "value": way.id
            })

    def get_building_options(self):
        return self.building_options
    

    def to_serialized_data(self):
        return {
            "features_by_risk": self.grouped_by_risk,
            "building_options": self.building_options,
            "default_position": self.default_position
        }


    # Layers
    def get_layers(self):
        return [
            dl.GeoJSON(
                data={"type": "FeatureCollection", "features": self.grouped_by_risk.get(risk, [])},
                id=f"geojson-{risk}",
                options=dict(
                    style=dict(
                        color=color_map[risk],
                        weight=1,
                        fillOpacity=0.5
                    )
                ),
                zoomToBoundsOnClick=False,
                hoverStyle={"weight": 3, "color": "#333", "fillOpacity": 0.7},
                eventHandlers={"click": True}
            )
            for risk in color_map
        ]
    
    # Legend
    def get_legend(self):
        return [
            html.Div([
                html.H4("Risk Zones"),
                html.Div([
                    html.Span([
                        html.Span(style={
                            "display": "inline-block",
                            "width": "12px",
                            "height": "8px",
                            "backgroundColor": color_map[risk],
                            "marginRight": "5px",
                            "border": "1px solid #333"
                        }),
                    risk
                    ], style={"marginRight": "15px"})  # spacing between items
                    for risk in color_map
                ], style={"display": "flex", "flexDirection": "row", "alignItems": "center"})
            ], style={
                "position": "absolute",
                "top": "50px",
                "right": "10px",
                "backgroundColor": "white",
                "padding": "10px",
                "zIndex": "1000",
                "border": "1px solid #ccc",
                "borderRadius": "5px",
                "display": "inline-block"
            })
        ]

    # Building Dropdown
    def get_dropdown_info(self, building_id):
        if not building_id:
            return self.default_position, None, self.default_position, self.default_zoom

        for way in self.result.ways:
            if str(way.id) == str(building_id):
                lats = [float(n.lat) for n in way.nodes]
                lons = [float(n.lon) for n in way.nodes]
                centroid = [sum(lats) / len(lats), sum(lons) / len(lons)]
                tags = way.tags
                risk = assign_risk_zone(tags)
                name = tags.get("name", "Unnamed")

                return centroid, self._popup(way.id, tags, risk, name), centroid, 18

        return self.default_position, None, self.default_position, self.default_zoom

    # Click Buildings
    def get_click_info(self, *click_datas):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        risk_keys = [f"geojson-{risk}" for risk in color_map]

        if triggered_id not in risk_keys:
            raise PreventUpdate

        idx = risk_keys.index(triggered_id)
        click_data = click_datas[idx]

        if not click_data:
            raise PreventUpdate

        props = click_data.get("properties")
        geometry = click_data.get("geometry")
        if not props or not geometry:
            raise PreventUpdate

        coords = geometry.get("coordinates", [[]])[0]
        if not coords:
            raise PreventUpdate

        lons = [point[0] for point in coords]
        lats = [point[1] for point in coords]
        centroid = [sum(lats) / len(lats), sum(lons) / len(lons)]
        building_id = str(props.get("id"))
        tags = props.get("tags", {})
        name = props.get("name", "Unnamed")
        risk = props.get("risk", "Unknown")

        return centroid, self._popup(building_id, tags, risk, name)

    # PopUp
    def _popup(self, building_id, tags, risk, name):
        if str(building_id) == "4497311":
            return dl.Popup([
                html.H3("🎉 Special Building!"),
                html.P("This building is featured in a custom popup."),
                html.Ul([
                    html.Li(f"Name: {name}"),
                    html.Li("This building has historical significance."),
                    html.Li("Custom notes, links, or images can go here."),
                ]),
                dcc.Dropdown(
                    options=[
                        {"label": "History", "value": "history"},
                        {"label": "Landmarks", "value": "landmarks"},
                        {"label": "Culture", "value": "culture"}
                    ],
                    placeholder="Select a topic",
                    style={"marginTop": "10px", "width": "100%"}
                ),
                html.A("Learn more about Milan", href="https://en.wikipedia.org/wiki/Milan", target="_blank", style={
                    "display": "block",
                    "marginTop": "10px",
                    "color": "#007BFF",
                    "textDecoration": "underline"
                }),
                html.Img(
                    src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                    style={"width": "100%", "marginTop": "10px"}
                )
            ])
        else:
            return dl.Popup([
                html.H4(f"Building ID: {building_id}"),
                html.H4(name),
                html.P(f"Risk Zone: {risk}"),
                html.P(f"Type: {tags.get('building', 'Unknown')}")
            ])
        