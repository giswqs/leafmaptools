"""
A styling tool...
"""

import copy
import json
from typing import Iterator, Tuple

from ipywidgets import (
    link, HTML, Textarea, Button, ButtonStyle, Checkbox, Layout, ColorPicker,
    HBox, VBox, ToggleButton, IntSlider, FloatSlider, Dropdown
)
from ipyleaflet import Layer, Map, WidgetControl

from leafmaptools.utils import is_valid_json


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


class StyleTextTool:
    """A textual tool to style another layer on a map with a text-based GUI.

    :param m: The map object to which to add a styling widget.
    :param layer: The layer object which is to be styled.
    :param attr_name: The layer's attribute name storing the style object.
        This is usually one of: "style", "hover_style", and "point_style"
    :param position: The map corner where this widget will be placed.
    
    TODO: The JSON textarea should reflect changes to the layer triggered by
          others. 
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
        def updated(change):
            """Called after each single-letter edit of the JSON in the textarea.
            """
            if change["type"] != "change":
                return
            value = change["owner"].value
            if not is_valid_json(value):
                return
            else:
                layer.style = json.loads(value)

        def close(button):
            a_map.remove_control(wc)

        layout = Layout(width="28px", height="28px", padding="0px 0px 0px 4px")
        btn = Button(tooltip="Close", icon="close", layout=layout)
        btn.on_click(close)
        ta = Textarea(value=json.dumps(getattr(layer, attr_name), indent=2))
        ta.layout.width = "200px"
        ta.observe(updated)
        header = HBox([HTML(f"<i>{attr_name} (JSON)</i>"), btn])
        ui = VBox([header, ta])
        wc = WidgetControl(widget=ui, position=position, transparent_bg=True)
        a_map.add_control(wc)
