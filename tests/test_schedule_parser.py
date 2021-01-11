import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal
from lib import schedule_parser

class MyTestCase(unittest.TestCase):
    """
    Test class for a parser of .inc files with information of Well completions
    """
    def setUp(self):
        """
        Prepares info for reference input file(s)
        @return: None
        """
        self.keywords = ("DATES", "COMPDAT", "COMPDATL")
        self.parameters = ("Date", "Well name", "Local grid name", "I", "J", "K upper", "K lower", "Flag on connection",
                      "Saturation table", "Transmissibility factor", "Well bore diameter", "Effective Kh",
                      "Skin factor", "D-factor")

        # TODO: с названиями стоит подумать
        self.input_file_reference = "test_schedule_input_reference.inc"
        self.output_csv_reference = "schedule_output_reference.csv"

        self.clean_file = "handled_schedule.inc"
        self.output_csv = "schedule_output.csv"

        self.schedule_reference = pd.read_csv(self.output_csv_reference, sep=";", index_col=0)

    def test_transform_schedule(self):
        """
        Test for the whole parser. Uses a reference file
        @return: None
        """
        schedule_parser.transform_schedule(self.keywords,
                                           self.parameters,
                                           self.input_file_reference,
                                           self.clean_file,
                                           self.output_csv)

        schedule = pd.read_csv(self.output_csv, sep=";", index_col=0)
        assert_frame_equal(self.schedule_reference, schedule)

        # self.assertEqual(schedule, self.schedule_ref)


if __name__ == '__main__':
    unittest.main()
