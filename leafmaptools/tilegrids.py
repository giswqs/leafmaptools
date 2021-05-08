"""
A tool for drawing tile grids over a map.
"""

from typing import Iterator, Tuple

import geojson
from ipywidgets import (
    link, HTML, Textarea, Button, ButtonStyle, Checkbox, Layout, ColorPicker,
    HBox, VBox, ToggleButton, IntSlider, FloatSlider, Dropdown
)
from ipyleaflet import basemaps, Layer, Map, GeoJSON, WidgetControl
import mercantile


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
