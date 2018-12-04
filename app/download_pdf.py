#
# Author: Pengyan Rao, z5099703
#
# It will create a document "pdf_doc" in current path for pdf files.
#

import requests
import os

# This mapping is created from page source.
link_location_mapping = {'nsw-ballina': ['NSW_TP009', 'Ballina'],
        'nsw-bermagui': ['NSW_TP010', 'Bermagui'],
        'nsw-botany-bay': ['NSW_TP001', 'Botany Bay'],
        'nsw-broughton-i': ['NSW_TP037', 'Broughton I.'],
        'nsw-brunswick-heads': ['NSW_TP016', 'Brunswick Heads'],
        'nsw-camden-haven': ['NSW_TP038', 'Camden Haven'],
        'nsw-camp-cove': ['NSW_TP011', 'Camp Cove'],
        'nsw-coffs-harbour': ['NSW_TP012', 'Coffs Harbour'],
        'nsw-crookhaven-heads': ['NSW_TP027', 'Crookhaven Heads'],
        'nsw-crowdy-head': ['NSW_TP017', 'Crowdy Head'],
        'nsw-dangar-i': ['NSW_TP034', 'Dangar I.'],
        'nsw-eden': ['NSW_TP002', 'Eden'],
        'nsw-ettalong': ['NSW_TP035', 'Ettalong'],
        'nsw-evans-head': ['NSW_TP013', 'Evans Head'],
        'nsw-forster': ['NSW_TP018', 'Forster'],
        'nsw-gosford': ['NSW_TP036', 'Gosford'],
        'nsw-harrington-inlet': ['NSW_TP019', 'Harrington Inlet'],
        'nsw-huskisson': ['NSW_TP031', 'Huskisson'],
        'nsw-jervis-bay': ['NSW_TP014', 'Jervis Bay'],
        'nsw-kingscliff': ['NSW_TP029', 'Kingscliff'],
        'nsw-ku-ring-gai-yc': ['NSW_TP033', 'Ku-Ring-Gai Y.C.'],
        'nsw-lord-howe-island': ['NSW_TP003', 'Lord Howe Island'],
        'nsw-moruya': ['NSW_TP030', 'Moruya'],
        'nsw-newcastle': ['NSW_TP004', 'Newcastle'],
        'nsw-nw-solitary-i': ['NSW_TP039', 'Nw Solitary I.'],
        'nsw-patonga': ['NSW_TP020', 'Patonga'],
        'nsw-port-hacking': ['NSW_TP021', 'Port Hacking'],
        'nsw-port-kembla': ['NSW_TP006', 'Port Kembla'],
        'nsw-port-macquarie': ['NSW_TP026', 'Port Macquarie'],
        'nsw-port-stephens': ['NSW_TP015', 'Port Stephens'],
        'nsw-princess-jetty': ['NSW_TP022', 'Princess Jetty'],
        'nsw-sand-pt-pittwater': ['NSW_TP032', 'Sand Pt (Pittwater)'],
        'nsw-south-west-rocks': ['NSW_TP023', 'South West Rocks'],
        'nsw-swansea': ['NSW_TP024', 'Swansea'],
        'nsw-sydney-fort-denison': ['NSW_TP007', 'Sydney (Fort Denison)'],
        'nsw-tweed-heads': ['NSW_TP028', 'Tweed Heads'],
        'nsw-ulladulla-harbour': ['NSW_TP025', 'Ulladulla Harbour'],
        'nsw-yamba': ['NSW_TP008', 'Yamba']
    }

# http://www.bom.gov.au/ntc/IDO59001/IDO59001_2018_NSW_TP029.pdf

bast_url = 'http://www.bom.gov.au/ntc/IDO59001/IDO59001_2018_'
pdf_doc = 'pdf_doc'
work_dir = os.getcwd()
absolute_pdf_doc = f'{work_dir}/{pdf_doc}'

def check_pdf_doc():
    """ If the pdf document doesn't exist, create it. """
    if os.path.exists(absolute_pdf_doc):
        print(f'Path exists:\n{absolute_pdf_doc}')
        return
    else:
        os.makedirs(absolute_pdf_doc)
        print(f'Path is created:\n{absolute_pdf_doc}')
        return

def download_pdf():

    check_pdf_doc()
    count = 0

    for k, v in link_location_mapping.items():

        url = bast_url + f'{v[0]}.pdf'
        r = requests.get(url)
        pdf_name = f'{k}.pdf'
        pdf_path = f'{absolute_pdf_doc}/{pdf_name}'

        if os.path.exists(pdf_path):
            print(f'Exist: {pdf_name}')
            continue

        else:
            with open(pdf_path, 'wb') as code:
               code.write(r.content)
               count += 1
               print(f'Success: {k}.pdf')
               
    print(f'Total: {len(link_location_mapping)}, Success: {count}')

if __name__ == '__main__':
    # print(work_dir)
    # check_pdf_doc()
    download_pdf()
