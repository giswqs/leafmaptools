"""
Tests for `leafmaptools.basemaps` module.
"""


from leafmaptools.basemaps import get_basemap


def test_get_basemap():
    """Test `leafmaptools.basemaps.get_basemap`.
    """
    exp = {
        'url': 'http://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        'max_zoom': 20,
        'attribution': '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
        'name': 'CartoDB.Positron'
    }
    res = get_basemap("CartoDB.Positron")
    assert res == exp
