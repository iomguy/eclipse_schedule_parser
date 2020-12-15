# -*- coding: utf-8 -*-
import re
import os
import pandas as pd


def read_schedule(path, mode, enc):
	"""
	@param path:
	@param mode:
	@param enc:
	@return: проверка на кодировки, память
	"""
	with open(path, mode, encoding=enc) as file:
		text = file.read()
	
	return text


def inspect_schedule(text):
	"""
	@param text:
	@return:
	"""
	# TODO: не пустой ли файл, есть ли закрывающая /
	inspected_text = text
	
	return inspected_text


def clean_schedule(text):
	"""
	@param text:
	@return: cleans '-- ' comments
	"""
	# TODO: использовать os.linesep вместо \n (Eclipse может работать на Линуксе). Но почему-то у меня это не работает
	cleaned_from_comments_text = re.sub(r"--.+\n", r"\n", text)
	cleaned_from_newlines_text = re.sub(r"\n(\s+)?\n", "\n", cleaned_from_comments_text)
	
	return cleaned_from_newlines_text


def parse_schedule(text, keywords):
	"""	
	@param text: 
	@param keywords: 
	@return: returns keywords text blocks ending with a newline "/"
	"""
	# keyword_regex = re.compile(r"(DATES|COMPDAT|COMPDATL)\n(.+?)^/\s*$", re.MULTILINE | re.DOTALL)
	keyword_template = "|".join(keywords)
	# TODO: использовать os.linesep вместо \n (Eclipse может работать на Линуксе). Но почему-то у меня это не работает
	keyword_regex = re.compile(rf"({keyword_template})\n(.+?)^/\s*$", re.MULTILINE | re.DOTALL)

	# first well completion data may have no date
	curr_date = ""

	schedule_list = []
	block_list = []

	keyword_blocks = keyword_regex.findall(text)
	if keyword_blocks:
		for keyword_block in keyword_blocks:
			keyword, keyword_lines = extract_lines_from_keyword_block(keyword_block)
			curr_date, schedule_list, block_list =\
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
		# TODO: использовать os.linesep вместо \n (Eclipse может работать на Линуксе). Но почему-то у меня это не работает
		lines = block[1].split("\n")[:-1]
		# print(lines)

	except:
		raise Exception("No keyword or no data corresponds to a keyword")
	
	return (keyword, lines)


def parse_keyword_block(keyword, keyword_lines, current_date, schedule_list, block_list):
	"""
	@param keyword:
	@param keyword_lines:
	@param current_date:
	@param schedule_list:
	@param block_list:
	@return:
	"""
	# TODO: чтобы не писать вермишель if-else-ов, можно сделать через eval и перенести весь функционал в парсеры кл. слов
	# eval(f"{keyword}_parser({date},{keyword},{schedule_list})")
	if keyword == "DATES":
		for current_date_line in keyword_lines:
			# current_date_line = keyword_lines[-1]
			if block_list:
				schedule_list.extend(block_list)
				block_list = []
			else:
				schedule_list.append((current_date, ""))
			current_date = parse_keyword_DATE_line(current_date_line)

	elif keyword == "COMPDAT":
		for well_comp_line in keyword_lines:
			well_comp_data = parse_keyword_COMPDAT_line(well_comp_line)
			block_list.append((current_date, well_comp_data))

	elif keyword == "COMPDATL":
		for well_comp_line in keyword_lines:
			well_comp_data = parse_keyword_COMPDATL_line(well_comp_line)
			block_list.append((current_date, well_comp_data))

	return current_date, schedule_list, block_list


def parse_keyword_DATE_line(current_date_line):
	"""
	@param current_date_line:
	@return:
	"""
	date = re.sub(r"\s+/(\s+)?$", "", current_date_line)
	return date


def parse_keyword_COMPDAT_line(well_comp_line):
	"""
	@param well_comp_line:
	@return:
	"""
	well_comp_line = re.sub(r"'|(\s+/(\s+)?$)", "", well_comp_line)
	well_comp_line = re.split(r"\s+", well_comp_line)
	well_comp_line.insert(1, 'NaN')
	return well_comp_line


def parse_keyword_COMPDATL_line(well_comp_line):
	"""
	@param well_comp_line:
	@return:
	"""
	well_comp_line = re.sub(r"'|(\s+/(\s+)?$)", "", well_comp_line)
	well_comp_line = re.split(r"\s+", well_comp_line)
	return well_comp_line



def results_to_csv(schedule_list, csv_file):
	"""
	@param schedule_list:
	@return:
	"""
	result = pd.DataFrame(schedule_list)
	if csv_file:
		result.to_csv(csv_file, sep=";")

	return result


if __name__ == "__main__":

	schedule_text = read_schedule(path="input_data/test_schedule.inc", mode="r", enc="utf-8")
	inspected_text = inspect_schedule(schedule_text)
	cleaned_text = clean_schedule(inspected_text)
	with open("output_data/handled_schedule.inc", "w", encoding="utf-8") as handled_file:
		handled_file.write(cleaned_text)

	schedule_list = parse_schedule(cleaned_text, ("DATES", "COMPDAT", "COMPDATL"))
	results_to_csv(schedule_list, "output_data/schedule.csv")
