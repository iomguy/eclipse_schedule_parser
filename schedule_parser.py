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

	date = ""
	acc_list = []

	blocks = keyword_regex.findall(text)
	if blocks:
		for block in blocks:
			keyword, lines = parse_keyword_block(block)
			if keyword == "DATES":
				date = lines[-1]
			elif keyword == "COMPDAT":
				for line in lines:
					acc_list.append((date, line))
			elif keyword == "COMPDATL":
				for line in lines:
					acc_list.append((date, line))
	else:
		raise Exception("No keywords found in file")

	return acc_list


def parse_keyword_block(block):
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


def parse_keyword_line(line):
	"""
	@param line:
	@return:
	"""
	return

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
