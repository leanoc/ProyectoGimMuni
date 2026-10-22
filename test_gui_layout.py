import unittest

from gui.theme import center_window


class FakeWindow:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.geometry_value = None

    def update_idletasks(self):
        pass

    def winfo_screenwidth(self):
        return self.screen_width

    def winfo_screenheight(self):
        return self.screen_height

    def geometry(self, value):
        self.geometry_value = value


class FakeParentWindow:
    def update_idletasks(self):
        pass

    def winfo_rootx(self):
        return 1800

    def winfo_rooty(self):
        return 100

    def winfo_width(self):
        return 800

    def winfo_height(self):
        return 600


class FakeParent:
    def winfo_toplevel(self):
        return FakeParentWindow()


class TestCenterWindow(unittest.TestCase):
    def test_fits_window_to_small_screen_and_centers_it(self):
        window = FakeWindow(1024, 600)

        actual_size = center_window(window, 1200, 740)

        self.assertEqual(actual_size, (984, 520))
        self.assertEqual(window.geometry_value, "984x520+20+40")

    def test_keeps_requested_size_when_screen_is_large_enough(self):
        window = FakeWindow(1920, 1080)

        actual_size = center_window(window, 1200, 740)

        self.assertEqual(actual_size, (1200, 740))
        self.assertEqual(window.geometry_value, "1200x740+360+170")

    def test_centers_dialog_over_parent_without_changing_monitors(self):
        window = FakeWindow(1024, 600)

        center_window(window, 500, 400, FakeParent())

        self.assertEqual(window.geometry_value, "500x400+1950+200")


if __name__ == "__main__":
    unittest.main()
