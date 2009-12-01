"""Module for testing the pp.image module.
"""

import unittest
import pp.geo_image.image as image
import numpy as np


class TestEmptyImage(unittest.TestCase):
    """Class for testing the pp.image module
    """
    def setUp(self):
        """Setup the test.
        """
        self.img = image.Image()
        self.modes = ["L", "LA", "RGB", "RGBA", "YCbCr", "YCbCrA", "P", "PA"]


    def random_string(self, choices, length):
        """Generates a random string with elements from *set* of the specified
        *length*.
        """
        import random
        return "".join([random.choice(choices)
                        for i in
                        range(length)])
    
    def test_shape(self):
        """Shape of an empty image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.assertEqual(self.img.shape, (0, 0))
        self.img.convert(oldmode)
        
    def test_clip(self):
        """Clip an empty image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.assertEqual(self.img.channels, [])
        self.img.convert(oldmode)
        
    def test_convert(self):
        """Convert an empty image.
        """
        import random
        import string
        for mode1 in self.modes:
            for mode2 in self.modes:
                self.img.convert(mode1)
                self.assertEqual(self.img.mode, mode1)
                self.assertEqual(self.img.channels, [])
                self.img.convert(mode2)
                self.assertEqual(self.img.mode, mode2)
                self.assertEqual(self.img.channels, [])
        while True:
            randstr = self.random_string(string.letters,
                                         random.choice(range(1,7)))
            if randstr not in self.modes:
                break
        self.assertRaises(ValueError, self.img.convert, randstr)

    def test_stretch(self):
        """Stretch an empty image
        """
        import string
        import random
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.img.stretch()
            self.assertEqual(self.img.channels, [])
            self.img.stretch("linear")
            self.assertEqual(self.img.channels, [])
            self.img.stretch("histogram")
            self.assertEqual(self.img.channels, [])
            self.img.stretch("crude")
            self.assertEqual(self.img.channels, [])
            self.img.stretch((0.05, 0.05))
            self.assertEqual(self.img.channels, [])
            self.assertRaises(ValueError, self.img.stretch, (0.05, 0.05, 0.05))

            # Generate a random string
            while True:
                testmode = self.random_string(string.letters,
                                              random.choice(range(1,7)))
                if testmode not in self.modes:
                    break
            
            self.assertRaises(ValueError, self.img.stretch, testmode)
            self.assertRaises(TypeError, self.img.stretch, 1)
        self.img.convert(oldmode)
        
    def test_gamma(self):
        """Gamma correction on an empty image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            # input a single value
            self.img.gamma()
            self.assertEqual(self.img.channels, [])
            self.img.gamma(0.5)
            self.assertEqual(self.img.channels, [])
            self.img.gamma(1)
            self.assertEqual(self.img.channels, [])
            self.img.gamma(1.5)
            self.assertEqual(self.img.channels, [])

            # input a tuple
            self.img.gamma(range(10))
            self.assertEqual(self.img.channels, [])
            self.img.gamma((0.2, 3.5))
            self.assertEqual(self.img.channels, [])
            self.img.gamma(("blue", "white"))
            self.assertEqual(self.img.channels, [])

            # input a negative value
            self.assertRaises(ValueError, self.img.gamma, -0.5)
            self.assertRaises(ValueError, self.img.gamma, -1)
            self.assertRaises(ValueError, self.img.gamma, -3.8)
            self.assertRaises(TypeError, self.img.gamma, "blue")
        self.img.convert(oldmode)
        
    def test_invert(self):
        """Invert an empty image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.img.invert()
            self.assertEqual(self.img.channels, [])
            self.img.invert(True)
            self.assertEqual(self.img.channels, [])
            self.img.invert([True, False])
            self.assertEqual(self.img.channels, [])
            self.img.invert([True, False, True, False,
                             True, False, True, False])
            self.assertEqual(self.img.channels, [])
        self.img.convert(oldmode)
        
    def test_pil_image(self):
        """Return an empty PIL image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            if mode == "YCbCrA":
                self.assertRaises(ValueError, self.img.pil_image)
            else:
                pilimg = self.img.pil_image()
                self.assertEqual(pilimg.size, (0, 0))
        self.img.convert(oldmode)
        
    def test_putalpha(self):
        """Add an alpha channel.
        """
        # Putting alpha channel to an empty image should not do anything except
        # change the mode if necessary.
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.img.putalpha(np.array([]))
            self.assertEqual(self.img.channels, [])
            if mode.endswith("A"):
                self.assertEqual(self.img.mode, mode)
            else:
                self.assertEqual(self.img.mode, mode + "A")

            self.img.convert(oldmode)

            self.img.convert(mode)
            self.img.putalpha(np.array([]))
            self.img.putalpha(np.random.rand(3, 2))
            if mode.endswith("A"):
                self.assertEqual(self.img.mode, mode)
            else:
                self.assertEqual(self.img.mode, mode + "A")

        self.img.convert(oldmode)

    def test_save(self):
        """Save an empty image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.assertRaises(IOError, self.img.save,"test.png")

        self.img.convert(oldmode)

    def test_replace_luminance(self):
        """Replace luminance in an empty image.
        """
        oldmode = self.img.mode
        for mode in self.modes:
            self.img.convert(mode)
            self.img.replace_luminance([])
            self.assertEqual(self.img.mode, mode)
            self.assertEqual(self.img.channels, [])
            self.assertEqual(self.img.shape, (0, 0))
        self.img.convert(oldmode)

    def test_merge(self):
        """Merging of an empty image with another.
        """
        pass



if __name__ == '__main__':
    unittest.main()
