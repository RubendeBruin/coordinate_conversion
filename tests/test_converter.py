import unittest

from converter import ParsedPoint, convert_text, parse_coordinate_pair, parse_points, to_relative_xy


class ConverterTests(unittest.TestCase):
    def test_decimal_parsing_and_relative_output(self):
        raw = """
        Origin: 3.8163243, 52.7022056
        P1 3.826240, 52.704478
        P2 3.818058, 52.695705
        """

        output = convert_text(raw, coord_format="decimal", lon_positive="E", lat_positive="N")

        lines = output.splitlines()
        self.assertEqual(lines[0], "Name\tX\tY")
        self.assertTrue(lines[1].startswith("P1\t"))
        self.assertTrue(lines[2].startswith("P2\t"))

    def test_degrees_minutes_parsing(self):
        lon, lat = parse_coordinate_pair("3 48.974 52 42.132", "dm", "E", "N")
        self.assertAlmostEqual(lon, 3 + 48.974 / 60.0, places=7)
        self.assertAlmostEqual(lat, 52 + 42.132 / 60.0, places=7)

    def test_west_positive_setting(self):
        lon, _ = parse_coordinate_pair("3.8163243, 52.7022056", "decimal", "W", "N")
        self.assertLess(lon, 0)

    def test_origin_required(self):
        with self.assertRaises(ValueError):
            parse_points("P1 3.82, 52.70", "decimal", "E", "N")

    def test_relative_values_have_east_north_signs(self):
        origin = ParsedPoint("Origin", 3.0, 52.0)
        p_east_north = ParsedPoint("A", 3.001, 52.001)
        p_west_south = ParsedPoint("B", 2.999, 51.999)

        result = to_relative_xy(origin, [p_east_north, p_west_south])
        self.assertGreater(result[0][1], 0)
        self.assertGreater(result[0][2], 0)
        self.assertLess(result[1][1], 0)
        self.assertLess(result[1][2], 0)


if __name__ == "__main__":
    unittest.main()
