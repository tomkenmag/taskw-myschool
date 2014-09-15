from bs4 import BeautifulSoup
from getpass import getpass
from requests.auth import HTTPBasicAuth
import argparse
import bs4
import os
import re
import requests
import assignment

def print_assignments( assignment_list, head):
    rows, columns = os.popen('stty size', 'r').read().split()
    width = int(columns) // 5
    print("Næstu verkefni: ")
    print("-"*int(columns))
    print('\033[1m','#'.ljust(3),
        head[0].ljust(width),head[1].ljust(int(width*1.5)),
        head[2].ljust(int(width*0.7)),head[4].ljust(width),'\033[0m')
    num = 0
    for i in assignment_list:
        num += 1
        i.print_row(num, width)
    print("-"*int(columns))

def parse_assignment_list( html ):
    soup = BeautifulSoup(html,'html.parser')
    tables = soup.find_all('tbody')
    assignment_elements = tables[0].find_all('tr')
    assignment_list = [ [ col.get_text() for col in row if 
            type(col)==bs4.element.Tag] for row in assignment_elements][:-1]
    head = assignment_list[0]
    links = [ i['href'] for i in tables[0].find_all('a')]
    for i in range(len(links)):
        assignment_list[i+1].append(links[i])
    return head, [ assignment.Assignment.parse_attr_list(i) for i in assignment_list[1:]]
    #return head, assignment_list[1:]

def get_auth():
    username = input("Username: ")
    password = getpass()
    return (username,password)

def read_auth( path ):
    with open( path ) as f:
        return tuple(re.split('\s+', f.read() )[:-1])

def get_assignment_list():
    auth = read_auth( 'auth' )
    ret = requests.get('https://myschool.ru.is/myschool/?Page=Exe&ID=1.12', auth=auth)
    if ret.ok:
        head, assignment_list = parse_assignment_list( ret.text )
        return assignment_list
    else:
        print("Authentication failed: {:d}".format(ret.status_code))
