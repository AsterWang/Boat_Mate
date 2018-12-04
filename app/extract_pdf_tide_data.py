#
# Author: Pengyan Rao, z5099703
#
# return a dict of tide data
#

import PyPDF2
import re, os
import pprint

pdf_doc = 'pdf_doc'
pattern_first_data_line = re.compile(r'1[A-Z]*Time\s*m.*')
pattern_month_line = re.compile(r'1[A-Z]*Time\s*m')
pattern_time = re.compile(r'Time\s*m')

tide_data_unit_len = len('1715   0.32')
time_tag_len = len('Time     m')
time_date_len = len('2015   1.6116MOTime     m')

def get_pdf_data(file_path):
    """
        return a dict:
        {
         'SEPTEMBER': [
               {'date': [1, 'SA'],
                'tide_data': [['0538', 0.31], ['1211', 1.31], ['1805', 0.48]]},
               {'date': [2, 'SU'],
                'tide_data': [['0011', 1.19],
                              ['0621', 0.35],
                              ['1307', 1.32],
                              ['1915', 0.53]]},
               {'date': [3, 'MO'],
                'tide_data': [['0109', 1.09],
                              ['0715', 0.38],
                              ['1414', 1.35],
                              ['2040', 0.53]]},
                ...],
         ...}
    """

    if not os.path.exists(file_path):
        print(f'Extract fail: {file_path} doesn\'t exist!')
        return

    pdf_reader = PyPDF2.PdfFileReader(file_path)

    tide_year_data = dict()

    # page 1-3 have data
    for i in range(1, 4):
        pdf_page=pdf_reader.getPage(i)
        text = pdf_page.extractText()
        text = get_one_page_data(text)

        tide_list_to_dict(text, tide_year_data)

    # pprint.pprint(tide_year_data['DECEMBER'])
    # print(len(tide_year_data['DECEMBER']))
    # print(tide_year_data.keys())
    # check_result(tide_year_data)

    if len(tide_year_data.keys()) == 12:
        print(f'Get tide data: {file_path} ---> Success.')
    else:
        print(f'Get tide data: {file_path} ---> Fail !')

    return tide_year_data


def get_one_page_data(text):
    """
        return a list of one page data
    """
    
    text = text.split('\n')
    pretty_text = []
    first_data = re.search(pattern_first_data_line, text[3])
    if first_data:

        first_data = first_data.group()
        first_data = re.split(pattern_time, first_data)

        month = first_data[0][3:]
        day_week = first_data[0][1:3]

        pretty_text.append(f'#{month}')
        pretty_text.append([1, day_week])
        pretty_text.append(parse_unit_data(first_data[1]))

        for line in text[4:]:
            line_len = len(line)

            if line_len > 33:
                # '2134   1.281THFEBRUARYTime     m0312   0.14'
                # new month:
                month_line = re.split(pattern_month_line, line)
                yesterday_data = month_line[0]
                today_data = month_line[1]
                date_data = line.split('Time')[0][12:]
                day_week = date_data[:2]
                month = date_data[2:]

                pretty_text.append(parse_unit_data(yesterday_data))
                pretty_text.append(f'#{month}')
                pretty_text.append([1, day_week])
                pretty_text.append(parse_unit_data(today_data))

            elif line_len > 11:
                # other
                if line[-1] == 'm':
                    if line_len <= time_date_len:
                        # '2015   1.6116MOTime     m'
                        line = line[: 0-time_tag_len]
                        yesterday_data = line[: tide_data_unit_len]
                        date_nb = line[tide_data_unit_len: -2]
                        day_week = line[-2:]

                        pretty_text.append(parse_unit_data(yesterday_data))
                        pretty_text.append([int(date_nb), day_week])

                    else:
                        # '2143   1.581SUAPRILTime     m'
                        line = line[: 0-time_tag_len]
                        yesterday_data = line[: tide_data_unit_len]
                        date_nb = 1
                        day_week = line[tide_data_unit_len+1: tide_data_unit_len+3]
                        month = line[tide_data_unit_len+3:]

                        pretty_text.append(parse_unit_data(yesterday_data))
                        pretty_text.append(f'#{month}')
                        pretty_text.append([int(date_nb), day_week])

                else:
                    yesterday_data = line[: tide_data_unit_len]
                    today_data = line[0-tide_data_unit_len: ]
                    day_week = line[0-tide_data_unit_len-2: 0-tide_data_unit_len]
                    date_nb = line[tide_data_unit_len: 0-tide_data_unit_len-2]

                    pretty_text.append(parse_unit_data(yesterday_data))
                    pretty_text.append([int(date_nb), day_week])
                    pretty_text.append(parse_unit_data(today_data))
            else:
                # tide data
                # '1128   1.77'
                pretty_text.append(parse_unit_data(line))

    return pretty_text


def parse_unit_data(line):
    line = line.split(' ')
    return [line[0], float(line[-1])]

def tide_list_to_dict(text, year_dict):

    tide_year_data = year_dict
    month_data = list()
    day_data = list()
    oneday_data = dict()
    month = ''

    for t in text:
        if t[0] == '#':
            # month
            if len(month_data) > 0:
                oneday_data['tide_data'] = day_data
                month_data.append(oneday_data)
                tide_year_data[month] = month_data
                day_data = list()

            month = t[1:]
            month_data = list()

        elif isinstance(t[0], int):
            # date
            if len(day_data) > 0:
                oneday_data['tide_data'] = day_data
                # month_data.append(day_data)
                month_data.append(oneday_data)

            day_data = list()
            oneday_data = dict()
            oneday_data['date'] = t

        else:
            day_data.append(t)

    oneday_data['tide_data'] = day_data
    month_data.append(oneday_data)
    tide_year_data[month] = month_data


def check_result(data, is_details=False):
    for d in data.keys():
        if is_details:
            print(f'\n{d}: {len(data[d])} --> \n{data[d][0]};\n{data[d][-1]}')
        else:
            print(f'\n{d}: {len(data[d])}')


if __name__ == '__main__':

    file_path = f'{pdf_doc}/nsw-bermagui.pdf'
    # file_path = 'nsw-ballina.pdf'
    d = get_pdf_data(file_path)
    print(d.keys())
