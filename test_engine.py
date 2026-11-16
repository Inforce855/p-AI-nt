import tempfile
import unittest
from pathlib import Path
from PIL import Image
from paint_engine import Studio


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.s = Studio()
        self.s.new_canvas(100, 100, "#ADD8E6")
        self.s.create_layer("Cat Head")

    def test_filled_shape_and_transparency(self):
        self.s.paint("Cat Head", [{"kind": "ellipse", "points": [[20,20],[80,80]], "color": "#FF9633"}])
        self.assertEqual(self.s.composite().getpixel((50,50)), (255,150,51,255))
        self.assertEqual(self.s.composite().getpixel((0,0)), (173,216,230,255))
        self.assertEqual(self.s._layer("Cat Head")["image"].getpixel((0,0))[3], 0)

    def test_polygon_undo(self):
        self.s.paint("Cat Head", [{"kind":"polygon","points":[[20,80],[50,10],[80,80]],"color":"orange"}])
        self.assertNotEqual(self.s.composite().getpixel((50,50)), (173,216,230,255))
        self.s.undo()
        self.assertEqual(self.s.composite().getpixel((50,50)), (173,216,230,255))

    def test_bad_batch_atomic(self):
        revision = self.s.revision
        with self.assertRaises(ValueError):
            self.s.paint("Cat Head", [{"kind":"rectangle","points":[[1,1],[90,90]]},
                                      {"kind":"polygon","points":[[1,1]]}])
        self.assertEqual(self.s.revision, revision)
        self.assertEqual(self.s._layer("Cat Head")["image"].getbbox(), None)

    def test_erase(self):
        self.s.paint("Cat Head", [{"kind":"rectangle","points":[[10,10],[90,90]],"color":"orange"}])
        self.s.paint("Cat Head", [{"kind":"erase","points":[[50,50]],"width":20}])
        self.assertEqual(self.s.composite().getpixel((50,50)), (173,216,230,255))

    def test_layer_order(self):
        self.s.paint("Cat Head", [{"kind":"rectangle","points":[[10,10],[90,90]],"color":"orange"}])
        self.s.create_layer("Eyes")
        self.s.paint("Eyes", [{"kind":"ellipse","points":[[40,40],[60,60]],"color":"green"}])
        self.assertEqual(self.s.composite().getpixel((50,50)), (0,128,0,255))
        self.s.layer_control("Eyes", visible=False)
        self.assertEqual(self.s.composite().getpixel((50,50)), (255,165,0,255))

    def test_save_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.s.save(tmp, "Cat")
            self.assertTrue(Path(result["project"]).is_file())
            with Image.open(result["png"]) as image:
                self.assertEqual(image.size, (100,100))
            with self.assertRaises(ValueError):
                self.s.save(tmp, "Cat")


if __name__ == "__main__":
    unittest.main()
