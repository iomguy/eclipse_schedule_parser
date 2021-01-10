import schedule_parser


def interactive_parser(schedule: schedule_parser.pd.DataFrame) -> None:
    """
    infinite cycle asking to type a well name and (optional) date to print corresponding completions
    @param schedule: pandas DataFrame with rows like "<DATE>, <WellName>, <Param1>, <Param2>, ..."
    @return: None
    """
    # вообще, я против While True
    while True:
        print(f"Please type a Well name or Click 'Ctrl+C' to exit")
        well = input()

        print(f"Do you want to find completions for a certain date for well {well}?(y/n)")
        if_date = input()

        if if_date == "y":
            print("Please type Date")
            date = input()
            schedule_parser.find_schedule_well_data(schedule, well, date)
            pass

        else:
            schedule_parser.find_schedule_well_data(schedule, well)
            pass


if __name__ == "__main__":
    # TODO: эти параметры удобнее будет задавать через текстовые файлы
    keywords = ("DATES", "COMPDAT", "COMPDATL")
    parameters = ("Date", "Well name", "Local grid name", "I", "J", "K upper", "K lower", "Flag on connection",
                  "Saturation table", "Transmissibility factor", "Well bore diameter", "Effective Kh",
                  "Skin factor", "D-factor")
    input_file = "input_data/test_schedule.inc"
    clean_file = "output_data/handled_schedule.inc"
    output_csv = "output_data/schedule.csv"

    schedule_df = schedule_parser.transform_schedule(keywords, parameters, input_file, clean_file, output_csv)
    interactive_parser(schedule_df)
    # schedule_parser.find_schedule_well_data(schedule_df, "W3")
