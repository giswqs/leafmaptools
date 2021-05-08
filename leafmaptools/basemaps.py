"""
A first prototype of some collection of tools.
"""

import copy
from typing import Iterator

import geojson
from ipywidgets import (
    link, HTML, Textarea, Button, ButtonStyle, Checkbox, Layout, ColorPicker,
    HBox, VBox, ToggleButton, IntSlider, FloatSlider, Dropdown
)
from ipyleaflet import basemaps, Layer, Map, GeoJSON, TileLayer, WidgetControl
from traitlets.utils.bunch import Bunch
import mercantile

from leafmaptools.utils import bounds


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
