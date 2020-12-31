# -*- coding: utf-8 -*-
import re
import pandas as pd
# TODO: regex использовать os.linesep вместо \n (Eclipse может работать на Линуксе). Но почему-то у меня это не работает


def transform_schedule(keywords, parameters, input_file, clean_file, output_csv=""):
    """
    reads an input .inc file forming an output PanDas dataframe and writing output .inc and .csv files
    @param keywords: Eclipse keywords to be parsed
    @param parameters: list of columns in output .csv file
    @param input_file: path to input .inc file
    @param clean_file: path to output .inc file without comments and extra spaces/newlines
    @param output_csv: path to output .csv file (optional)
    @return: dataframe with dates and corresponding wells and another keywords parameters
    """
    schedule_text = read_schedule(path=input_file, mode="r", enc="utf-8")
    if inspect_schedule(schedule_text):
        cleaned_text = clean_schedule(schedule_text)
        schedule = parse_schedule(cleaned_text, keywords)

        with open(clean_file, "w", encoding="utf-8") as handled_file:
            handled_file.write(cleaned_text)
        schedule_df = results_to_csv(schedule, output_csv, columns=parameters)
    return schedule_df


def read_schedule(path, mode, enc):
    """
    reads the input .inc file forming a string of text
    @param path: path to the input .inc file
    @param mode: reading mode
    @param enc: encoding
    @return: string of input text
    """
    # TODO: добавить проверки на кодировку, объём файла, формат файла .inc
    with open(path, mode, encoding=enc) as file:
        text = file.read()

    return text


def inspect_schedule(text):
    """
    inspects schedule syntax
    @param text: input text from .inc file
    @return: inspected input text from .inc file
    """
    # TODO: проверить, не пустой ли файл, есть ли закрывающая / в конце и т.д.
    text_accuracy = True

    return text_accuracy


def clean_schedule(text):
    """
    cleans '-- ' comments
    @param text: inspected input text from .inc file
    @return: cleaned input text from .inc file
    """
    cleaned_from_comments_text = re.sub(r"--.+\n", r"\n", text)
    cleaned_from_newlines_and_extra_spaces_text = re.sub(r"\s*\n+", "\n", cleaned_from_comments_text)

    return cleaned_from_newlines_and_extra_spaces_text


def parse_schedule(text, keywords_tuple):
    """
    returns keywords text blocks ending with a newline "/"
    @param text: cleaned input text from .inc file
    @param keywords_tuple: a tuple of keywords we are interested in (DATES, COMPDAT, COMPDATL, etc.)
    @return: keywords text blocks ending with a newline "/"
    """
    # keyword_regex = re.compile(r"(DATES|COMPDAT|COMPDATL)\n(.*?)^/$", re.MULTILINE | re.DOTALL)
    keyword_template = "|".join(keywords_tuple)
    # TODO: если в конце блока с командой не будет стоять "\n'\'", блок просто проигнорируется. Нужно кидать warning
    keyword_regex = re.compile(rf"({keyword_template})\n(.*?)^/$", re.MULTILINE | re.DOTALL)

    # first well completion data may have no date
    curr_date = "NaN"
    keyword_lines = "NaN"

    schedule_list = []
    block_list = []

    keyword_blocks = keyword_regex.findall(text)
    if keyword_blocks:
        for keyword_block in keyword_blocks:
            keyword, keyword_lines = extract_lines_from_keyword_block(keyword_block)
            curr_date, schedule_list, block_list =\
                parse_keyword_block(keyword, keyword_lines, curr_date, schedule_list, block_list)

        keyword = "END"
        curr_date, schedule_list, block_list = \
            parse_keyword_block(keyword, keyword_lines, curr_date, schedule_list, block_list)
    else:
        raise Exception("No keywords found in file")

    return schedule_list


def extract_lines_from_keyword_block(block):
    """
    extracts the main keyword and corresponding lines from a certain block from the input file
    @param block: a block of the input text related to the some keyword (DATA, COMPDAT, etc.)
    @return:
        - keyword - DATA, COMPDAT, etc.
        - lines - lines of the input text related to the current keyword
    """
    try:
        keyword = block[0]
        lines = block[1].split("\n")[:-1]

    except Exception as e:
        print("No keyword or no data corresponds to a keyword")
        raise e

    return keyword, lines


def parse_keyword_block(keyword, keyword_lines, current_date, schedule_list, block_list):
    """
    parses a block of the input text related to the current keyword (DATA, COMPDAT, etc.)
    @param keyword: DATA, COMPDAT, etc.
    @param keyword_lines: lines of the input text related to the current keyword
    @param current_date: the last parsed DATE. The first DATE is NaN if not specified
    @param schedule_list: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...]
    @param block_list: schedule_list but for the current keyword
    @return:
        - current_date - current DATE value which might be changed if keyword DATES appears
        - schedule_list - updated schedule_list
        - block_list - updated block_list
    """
    # TODO: чтобы не писать вермишель if-else-ов, можно сделать через eval и перенести весь функционал в парсеры кл.слов
    # eval(f"{keyword}_parser({date},{keyword},{schedule_list})")
    if keyword == "DATES" or keyword == "END":
        for current_date_line in keyword_lines:
            if block_list:
                schedule_list.extend(block_list)
                block_list = []
            else:
                schedule_list.append([current_date, "NaN"])
            current_date = parse_keyword_DATE_line(current_date_line)

    elif keyword == "COMPDAT":
        for well_comp_line in keyword_lines:
            well_comp_data = parse_keyword_COMPDAT_line(well_comp_line)
            # insert current date into list with well completion data
            well_comp_data.insert(0, current_date)
            block_list.append(well_comp_data)

    elif keyword == "COMPDATL":
        for well_comp_line in keyword_lines:
            well_comp_data = parse_keyword_COMPDATL_line(well_comp_line)
            # insert current date into list with well completion data
            well_comp_data.insert(0, current_date)
            block_list.append(well_comp_data)

    return current_date, schedule_list, block_list


def parse_keyword_DATE_line(current_date_line):
    """
    parses a line related to a current DATA keyword block
    @param current_date_line: line related to a current DATA keyword block
    @return: list of parameters in a DATE line
    """
    date = re.sub(r"\s+/$", "", current_date_line)
    return date


def parse_keyword_COMPDAT_line(well_comp_line):
    """
    parses a line related to a current COMPDAT keyword block
    @param well_comp_line: line related to a current COMPDAT keyword block
    @return: list of parameters (+ NaN Loc. grid. parameter) in a COMPDAT line
    """
    # TODO: добавить учёт того, что могут задаваться не все параметры - нужно дополнять + существуют дефолтные параметры
    well_comp_line = re.sub(r"'|(\s+/$)", "", well_comp_line)
    well_comp_line = re.split(r"\s+", well_comp_line)
    well_comp_line.insert(1, 'NaN')
    return well_comp_line


def parse_keyword_COMPDATL_line(well_comp_line):
    """
    parses a line related to a current COMPDATL keyword block
    @param well_comp_line: line related to a current COMPDATL keyword block
    @return: list of parameters in a COMPDATL line
    """
    # TODO: добавить учёт того, что могут задаваться не все параметры - нужно дополнять + существуют дефолтные параметры
    well_comp_line = re.sub(r"'|(\s+/$)", "", well_comp_line)
    well_comp_line = re.split(r"\s+", well_comp_line)
    return well_comp_line



def results_to_csv(schedule_list, csv_file, columns):
    """
    forms PanDas dataframe with results and (optional) writes it into .csv file
    @param schedule_list: list of elements [[DATA1, WELL1, PARAM1, PARAM2, ...], [DATA2, ...], ...]
    @param csv_file: path to .csv file to save PanDas dataframe with results
    @param columns: list of columns in output .csv file
    @return: PanDas dataframe with results
    """
    # TODO: даты можно конвертнуть в pd datetime, и использовать float-ы с разделителем, зависящим от локали ОС
    result = pd.DataFrame(schedule_list)
    result.columns = columns
    if csv_file:
        result.to_csv(csv_file, sep=";", header=columns)
        print(f"Schedule table is successfully saved to {csv_file}")
    return result


def find_schedule_well_data(schedule_df, well, date="ALL_DATES"):
    """
    finds appearances of completions for a certain well and (optional) for a certain date
    @param schedule_df: PanDas dataframe with Well completion schedule
    @param well: certain Well name to find completions
    @param date: certain Date to find completions. Default value is "ALL_DATES"
    @return: PanDas dataframe with a current Well completion schedule
    """
    well_schedule_df = schedule_df[schedule_df["Well name"] == well]
    if date != "ALL_DATES":
        well_data_schedule_df = well_schedule_df[well_schedule_df["Date"] == date]
        result = well_data_schedule_df
    else:
        result = well_schedule_df

    pretty_print_schedule_well_data(result, well, date, well_schedule_df)
    return result


def pretty_print_schedule_well_data(schedule_df, well, date, if_date_found):
    """
    prints the whole PanDas df of appearances of completions for a certain well and (optional) for a certain date
    @param schedule_df: dataframe of completions for a certain well and (optional) for a certain date
    @param well: certain Well name to find completions
    @param date: certain Date to find completions. Default value is "ALL_DATES"
    @param if_date_found: False if we find completions for "ALL_DATES"
    @return: None
    """
    if schedule_df.empty:
        if if_date_found.empty:
            print(f"No Well {well} completions exist for any Date")
        else:
            print(f"Well {well} completions exist, but not for Date {date}")
    else:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(schedule_df)


if __name__ == "__main__":

    keywords = ("DATES", "COMPDAT", "COMPDATL")
    parameters = ("Date", "Well name", "Local grid name", "I", "J", "K upper", "K lower", "Flag on connection",
                  "Saturation table", "Transmissibility factor", "Well bore diameter", "Effective Kh",
                  "Skin factor", "D-factor")
    input_file = "input_data/test_schedule.inc"
    clean_file = "output_data/handled_schedule.inc"
    output_csv = "output_data/schedule.csv"


