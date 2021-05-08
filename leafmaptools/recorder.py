import json
import time
import os

from ipyfilechooser import FileChooser
from ipyleaflet import basemaps, Map, WidgetControl
from ipywidgets import Button, HBox, Layout


class MapRecorder:
    """A very experimental "recorder" for map events.
    
    For now this can record simple (zoom and pan) changes on the map. Recordings
    made with the widget can only be saved using the widget, but not loaded. They
    can be loaded using the ``path`` parameter in the contructor, though.
    
    Recordings are lists of such "events", and can be saved in a file with one JSON
    record per line, similar to asciinema.org:
    
      {"ts": 1617811104.3057659, "center": [0, 0], "zoom": 1.0}
      {"ts": 1617811105.2518709, "center": [20.6327, 59.0389], "zoom": 1.0}
      ...
    """
    def __init__(self, a_map: Map, path: str = ""):
        """Constructor.
        
        :param a_map: The map for which to record events.
        :param path: The path of a JSON records file containing a map recording.
        """
        self.recording = []
        if os.path.exists(path):
            with open(path) as f:
                self.recording = [json.loads(line) for line in f.read().splitlines()]
        self.a_map = a_map

        layout = Layout(width="30px")
        self.start = Button(tooltip="Start/Stop", icon="video-camera", layout=layout)
        self.start.on_click(self.toggle_rec)
        disabled = len(self.recording) == 0
        self.play = Button(tooltip="Play", icon="play", disabled=disabled, layout=layout)
        self.play.on_click(self.play_rec)
        self.save = Button(tooltip="Save", icon="floppy-o", disabled=disabled, layout=layout)
        self.save.on_click(self.save_rec)
        self.fc = FileChooser(os.getcwd())
        self.widget = HBox([self.start, self.play, self.save])

    def toggle_rec(self, btn):
        """Start/stop recording.
        
        We listen only for changes in the map's ``bounds``. There are these
        other event names, but these provide essentially the same information:

        zoom, center, bounds, bounds_polygon, north, south, east, west,
        pixel_bounds, top, bottom, right, left
        """
        if btn.button_style == "":
            btn.button_style = "danger"  # red
            self.play.disabled = True
            self.play.save = True
            self.recording = []
            self.a_map.observe(self.map_interacted, names="bounds", type="change")
            self.map_interacted({"name": "bounds", "type": "change", "owner": self.a_map})
        elif btn.button_style == "danger":
            btn.button_style = ""
            self.play.disabled = False
            self.save.disabled = False
            self.a_map.unobserve(self.map_interacted, names="bounds", type="change")

    def save_rec(self, btn):
        """Save recording to a local file using a pop-up selection panel.
        """
        def selected(obj):
            path = obj.get_interact_value()
            if path:
                with open(path, "w") as f:
                    for event in self.recording:
                        f.write(json.dumps(event) + "\n")
                self.widget.children = tuple(list(self.widget.children[:-1]))            
        if self.widget.children[-1] == self.fc:
            self.widget.children = tuple(list(self.widget.children[:-1]))            
        else:
            self.fc.register_callback(selected)
            self.widget.children = tuple(list(self.widget.children) + [self.fc])
    
    def play_rec(self, btn):
        """Play back recording.
        """
        self.start.disabled = True
        self.play.disabled = True
        self.save.disabled = True
        m = self.a_map
        for i, event in enumerate(self.recording):
            ts = event["ts"]
            center = event["center"]
            zoom = event["zoom"]
            if m.zoom != zoom:
                m.zoom = zoom
            if m.center != center:
                m.center = center
            if i < len(self.recording) - 1:
                time.sleep(self.recording[i + 1]["ts"] - ts)
        self.start.disabled = False
        self.play.disabled = False
        self.save.disabled = False

    def map_interacted(self, event):
        """Callback for changes in map object.
        """
        m = event["owner"]
        entry = {"ts": time.time(), "center": m.center, "zoom": m.zoom}
        self.recording.append(entry)
