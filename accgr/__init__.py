import os
from accgr.parser import parse

dir_path = os.path.dirname(os.path.realpath(__file__))

def test_parse():
    filenam = os.path.join(dir_path, 'testbook.txt')
    data = parse(filenam)
    assert data == {}