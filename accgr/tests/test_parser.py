import os
from accgr.parser import parse

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_parser_text_001():
    bookpath = os.path.join(dir_path, 'testbook.txt')
    data = parse(bookpath)
    assert data['data'][0]['per'] == 'Άνοιγμα χρήσης 2020'
    assert data['data'][0]['afm'] == '123123123'
    assert data['data'][0]['lines'][0]['value'] == 2000.21
    print(data)
