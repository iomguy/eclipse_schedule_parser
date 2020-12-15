# -*- coding: utf-8 -*-
import re
import pandas as pd
# TODO: regex использовать os.linesep вместо \n (Eclipse может работать на Линуксе). Но почему-то у меня это не работает


def transform_schedule(keywords, parameters, input_file, clean_file, output_csv):
    """
    @param keywords: Eclipse keywords to be parsed
    @param parameters: List of columns in output .csv file
    @param input_file: path to input .inc file
    @param clean_file: path to output .inc file without comments and extra spaces/newlines
    @param output_csv: path to output .csv file
    @return: dataframe with dates and corresponding wells and another keywords parameters
    """
    schedule_text = read_schedule(path=input_file, mode="r", enc="utf-8")
    if inspect_schedule(schedule_text):
        cleaned_text = clean_schedule(schedule_text)
        schedule = parse_schedule(cleaned_text, keywords)

        with open(clean_file, "w", encoding="utf-8") as handled_file:
            handled_file.write(cleaned_text)
        results_to_csv(schedule, output_csv, columns=parameters)
    return schedule


def read_schedule(path, mode, enc):
    """
    @param path:
    @param mode:
    @param enc:
    @return: string of input text
    """
    # TODO: добавить проверки на кодировку, объём файла, формат файла .inc
    with open(path, mode, encoding=enc) as file:
        text = file.read()

    return text


def inspect_schedule(text):
    """
    @param text:
    @return: inspects schedule syntax
    """
    # TODO: проверить, не пустой ли файл, есть ли закрывающая / в конце и т.д.
    text_accuracy = True

    return text_accuracy


def clean_schedule(text):
    """
    @param text:
    @return: cleans '-- ' comments
    """
    cleaned_from_comments_text = re.sub(r"--.+\n", r"\n", text)
    cleaned_from_newlines_and_extra_spaces_text = re.sub(r"\s*\n+", "\n", cleaned_from_comments_text)

    return cleaned_from_newlines_and_extra_spaces_text


def parse_schedule(text, keywords_tuple):
    """
    @param text:
    @param keywords_tuple:
    @return: returns keywords text blocks ending with a newline "/"
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
    @param block:
    @return:
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
    @param keyword:
    @param keyword_lines:
    @param current_date:
    @param schedule_list:
    @param block_list:
    @return:
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
    @param current_date_line:
    @return: list of parameters in a DATE line
    """
    date = re.sub(r"\s+/$", "", current_date_line)
    return date


def parse_keyword_COMPDAT_line(well_comp_line):
    """
    @param well_comp_line:
    @return: list of parameters (+ NaN Loc. grid. parameter) in a COMPDAT line
    """
    # TODO: добавить учёт того, что могут задаваться не все параметры - нужно дополнять + существуют дефолтные параметры
    well_comp_line = re.sub(r"'|(\s+/$)", "", well_comp_line)
    well_comp_line = re.split(r"\s+", well_comp_line)
    well_comp_line.insert(1, 'NaN')
    return well_comp_line


def parse_keyword_COMPDATL_line(well_comp_line):
    """
    @param well_comp_line:
    @return: list of parameters in a COMPDATL line
    """
    # TODO: добавить учёт того, что могут задаваться не все параметры - нужно дополнять + существуют дефолтные параметры
    well_comp_line = re.sub(r"'|(\s+/$)", "", well_comp_line)
    well_comp_line = re.split(r"\s+", well_comp_line)
    return well_comp_line



def results_to_csv(schedule_list, csv_file, columns):
    """
    @param schedule_list:
    @return: PanDas dataframe with results
    """
    # TODO: даты можно конвертнуть в pd datetime, и использовать float-ы с разделителем, зависящим от локали ОС
    result = pd.DataFrame(schedule_list)
    if csv_file:
        result.to_csv(csv_file, sep=";", header=columns)
        print(f"Schedule table is successfully saved to {csv_file}")
    return result


if __name__ == "__main__":

    keywords = ("DATES", "COMPDAT", "COMPDATL")
    parameters = ("Date", "Well name", "Local grid name", "I", "J", "K upper", "K lower", "Flag on connection",
                  "Saturation table", "Transmissibility factor", "Well bore diameter", "Effective Kh",
                  "Skin factor", "D-factor")
    input_file = "input_data/test_schedule.inc"
    clean_file = "output_data/handled_schedule.inc"
    output_csv = "output_data/schedule.csv"


