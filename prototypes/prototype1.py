"""
A first prototype of some collection of tools.
"""

import copy
from typing import Iterator, Tuple

import geojson
from ipywidgets import (
    link, HTML, Textarea, Button, ButtonStyle, Checkbox, Layout, ColorPicker,
    HBox, VBox, ToggleButton, IntSlider, FloatSlider, Dropdown
)
from ipyleaflet import basemaps, Layer, Map, GeoJSON, TileLayer, WidgetControl
from traitlets.utils.bunch import Bunch
import mercantile


def bounds(geojson_obj: dict) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Calculate the bounds of the GeoJSON object as [[south, west], [north, east]].
    """
    # Is there really no simpler/faster way to do this (without NumPy)?
    coords = list(geojson.utils.coords(geojson_obj))
    south = min(lat for lon, lat in coords)
    north = max(lat for lon, lat in coords)
    west = min(lon for lon, lat in coords)
    east = max(lon for lon, lat in coords)
    bounds = [[south, west], [north, east]]
    return bounds


def yield_basemap_dicts() -> Iterator[dict]:
    """Yield all known ipyleaflet basemaps as dicts.

    Example:
    
    >>> next(yield_basemap_dicts())
    {'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
     'max_zoom': 19,
     'attribution': 'Map data (c) <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
     'name': 'OpenStreetMap.Mapnik'}    
    """
    for bm in basemaps.values():
        if type(bm) == dict:
            yield bm
        elif type(bm) == Bunch:
            for bm1 in bm.values():
                yield bm1


def get_basemap(name: str) -> dict:
    """Get basename dict via its fully qualified name.
    
    Example:
    
    >>> get_basemap("CartoDB.Positron")
    {'url': 'http://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
     'max_zoom': 20,
     'attribution': '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
     'name': 'CartoDB.Positron'}
    """
    x = basemaps
    for n in name.split("."):
        x = getattr(x, n)
        if type(x) == dict:
            return x
        

class BasemapTool:
    """Widget for switching between different basemaps (TileLayers).
    
    This will not work in combination with `ipyleaflet.SplitMapControl`.
    """
    def __init__(self,
        description: str = "Basemap",
        position: str = "topright",
        a_map: Map = None
    ):
        options = list(yield_basemap_dicts())
        options = [opt["name"] for opt in options]
        
        current_basemap_name = [l for l in a_map.layers if type(l)==TileLayer][0].name
        start_value = current_basemap_name if current_basemap_name in options else options[0]
        
        dropdown = Dropdown(
            description=description,
            options=options,
            value=start_value,
            layout=Layout(width="250px")
        )

        close_btn = Button(
            icon="times",
            button_style="info",
            tooltip="Close the basemap widget",
            layout=Layout(width="32px"),
        )

        self.widget = HBox([dropdown, close_btn])

        def switch(basemap_name):
            if len(a_map.layers) == 1:
                a_map.layers = tuple([TileLayer(**get_basemap(basemap_name))])
            else:
                old_basemap = [l for l in a_map.layers if type(l)==TileLayer][0]
                a_map.substitute_layer(old_basemap, TileLayer(**get_basemap(basemap_name)))

        def on_click(change):
            basemap_name = change["new"]
            switch(basemap_name)

        dropdown.observe(on_click, "value")

        def close_click(change):
            if a_map.basemap_ctrl is not None and a_map.basemap_ctrl in a_map.controls:
                a_map.remove_control(a_map.basemap_ctrl)
            self.widget.close()

        close_btn.on_click(close_click)

        self.widget_control = WidgetControl(widget=self.widget, position="topright")
        a_map.add_control(self.widget_control)
        a_map.basemap_ctrl = self.widget_control
        switch(dropdown.value)


class StyleTool:
    """A tool to style another layer on a map with a simple GUI.
    """
    def __init__(self,
        position: str = "bottomleft",
        attr_name: str = "style",
        kind: str = "stroke",
        orientation: str = "horizontal",
        transparent: bool = False,
        a_map: Map = None,
        layer: Layer = None,
        place_control: bool = True
    ):
        """Add a widget to the map that allows styling some given layer.

        At the moment only the stroke color, opacity and weight can be changed
        using a color picker and sliders. Dash array might follow later.

        :param m: The map object to which to add a styling widget.
        :param layer: The layer object which is to be styled.
        :param attr_name: The layer's attribute name storing the style object.
            This is usually one of: "style", "hover_style", and "point_style"
        :param kind: The kind of style, either "stroke" or "fill".
        :param orientation: The orientation of the UI elements, either "horizontal"
            (default) or "vertical".
        :param transparent: A flag to indicate if the widget background should be
            transparent (default: ``False``). 
        :param position: The map corner where this widget will be placed. 

        TODO: The UI elements should reflect changes to the layer triggered by
              others. 
        """
        assert kind in ["stroke", "fill"]
        assert orientation in ["horizontal", "vertical"]

        def restyle(change):
            if change["type"] != "change":
                return
            owner = change["owner"]
            style_copy = copy.copy(getattr(layer, attr_name))
            attr_map = {
                p: "color" if kind == "stroke" else "fillColor",
                o: "opacity" if kind == "stroke" else "fillOpacity",
                w: "weight"
            }
            if owner in [p, o, w]:
                style_copy[attr_map[owner]] = owner.value
                setattr(layer, attr_name, style_copy)

        def close(button):
            a_map.remove_control(wc)

        attr = getattr(layer, attr_name)
        style = getattr(layer, "style")

        b = ToggleButton(description="Stroke", value=True, tooltip="Stroke or not?")
        dummy = ToggleButton(value=not b.value)
        b.layout.width = "80px"

        name = "color" if kind == "stroke" else "fillColor"
        p = ColorPicker(value=attr.get(name, style.get(name, "#3885ff")))
        p.layout.width = "100px"

        name = "opacity" if kind == "stroke" else "fillOpacity"
        o = FloatSlider(min=0, max=1, value=attr.get(name, style.get(name, 0.5)))
        o.layout.width = "200px"

        w = IntSlider(min=0, max=50, value=attr.get("weight", style.get("weight", 5)))
        w.layout.width = "200px"

        layout = Layout(width="28px", height="28px", padding="0px 0px 0px 4px")
        q = Button(tooltip="Close", icon="close", button_style="info", layout=layout)

        for el in [p, o, w] if kind == "stroke" else [p, o]:
            link((dummy, "value"), (el, "disabled"))

        p.observe(restyle)
        o.observe(restyle)
        if kind == "stroke":
            w.observe(restyle)
        else:
            w.disabled = True
        q.on_click(close)

        desc = HTML(f"{kind} {attr_name}")

        if orientation=="horizontal":
            self.widget = HBox([desc, p, w, o, q])
        elif orientation=="vertical":
            self.widget = VBox([HBox([desc, q]), p, w, o])

        wc = WidgetControl(widget=self.widget, position=position, transparent_bg=transparent)
        a_map.add_control(wc)


class TileGridTool:
    """A tool for adding a dynamic Mercator tile grid to a map.

    The grid is recalculated/adapted dynamically to the visible part of the map
    only as the user zooms and pans over it. The grid level is limited from 0
    to the current map zoom level plus 4, or there would be too many cells and
    the grid would be too dense to see anything else.
    """
    def __init__(
        self, a_map: Map, description: str = "Mercator", position: str = "topright",
    ):
        """Instantiate a tile grid tool and place it on a map.
        """
        self._max_zoom_delta = 4

        self.tile_xy = ""
        self.level = int(a_map.zoom)
        style = {"color": "#888888", "weight": 1, "fillOpacity": 0}
        hover_style = {"weight": 3, "fillOpacity": 0.1}
        self.gj = GeoJSON(
            data=geojson.Feature(),
            name=description,
            style=style,
            hover_style=hover_style
        )

        min, max = 0, int(a_map.zoom) + self._max_zoom_delta
        self.slider = IntSlider(
            description=description, min=min, max=max, value=self.level
        )
        self.ht = HTML(f"ID: {self.tile_xy} Map zoom: {int(a_map.zoom)}")
        self.close_btn = Button(
            icon="times",
            button_style="info",
            tooltip="Close the widget",
            layout=Layout(width="32px"),
        )
        self.widget = HBox([self.slider, self.ht, self.close_btn])
        def hover(event, feature, **kwargs):
            if event == "mouseover":
                self.tile_xy = feature["id"]
                self.ht.value = f"{self.tile_xy} Map zoom: {int(a_map.zoom)}"

        def slider_moved(event):
            if event["type"] == "change" and event["name"] == "value":
                self.level = event["new"]
                self.tile_xy = ""
                map_interacted({"type": "change", "name": "bounds", "owner": a_map})

        self.slider.observe(slider_moved)

        def map_interacted(event):
            if event["type"] == "change" and event["name"] == "bounds":
                self.ht.value = f"{self.tile_xy}, Map zoom: {int(a_map.zoom)}"
                self.slider.max = int(a_map.zoom) + self._max_zoom_delta
                m = event["owner"]
                ((south, west), (north, east)) = m.bounds
                
                # Attention in the order of west, south, east, north!
                tiles = mercantile.tiles(west, south, east, north, zooms=self.level)
                
                features = [mercantile.feature(t) for t in tiles]
                self.gj.data = geojson.FeatureCollection(features=features)

                # Ipyleaflet buglet: This name is updated in the GeoJSON layer,
                # but not in the LayersControl!
                self.gj.name = str(int(self.level))

                self.gj.on_hover(hover)

        def close_click(change):
            self.widget.children = []
            self.widget.close()

        self.close_btn.on_click(close_click)

        a_map += self.gj
        a_map.observe(map_interacted)
        map_interacted({"type": "change", "name": "bounds", "owner": a_map})

        self.widget_control = WidgetControl(widget=self.widget, position=position)
        a_map.add_control(self.widget_control)
