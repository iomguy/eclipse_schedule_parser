import pytest
import pandas as pd
import numpy as np
from pandas.util.testing import assert_frame_equal
from lib import schedule_parser


class TestIntegrParser:
    @pytest.fixture
    def set_up(self):
        """
        Prepares info for reference input file(s)
        @return: None
        """
        self.keywords = ("DATES", "COMPDAT", "COMPDATL")
        self.parameters = ("Date", "Well name", "Local grid name", "I", "J", "K upper", "K lower", "Flag on connection",
                  "Saturation table", "Transmissibility factor", "Well bore diameter", "Effective Kh",
                  "Skin factor", "D-factor", "Dir_well_penetrates_grid_block", "Press_eq_radius")

        # TODO: с названиями стоит подумать
        self.input_file_reference = "data/test_schedule_input_reference.inc"
        self.output_csv_reference = "data/schedule_output_reference.csv"

        self.clean_file = "data/handled_schedule.inc"
        self.output_csv = "data/schedule_output.csv"

        self.schedule_reference = pd.read_csv(self.output_csv_reference, sep=";", index_col=0)

    def test_transform_schedule(self, set_up):
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
        # TODO: вроде бы, assert_frame_equal отрабатывает в PyTest. Или нет?
        # with pytest.raises(AssertionError):
        assert_frame_equal(self.schedule_reference, schedule)
