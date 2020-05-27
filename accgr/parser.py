import re
from collections import defaultdict
from accgr.dec import Dec


def parse_set(line: str, data: dict):
    _, key, *val = line.strip().split()
    data['set'][key] = ' '.join(val)


def parse_acc(line: str, data: dict):
    _, acc, alternative = line.strip().split()
    data['acc'][acc] = alternative


def parse_header(line):
    vals = line.strip().split()
    lvals = len(vals)
    if lvals == 4:
        date, typ, *_, afm = vals
    elif lvals == 3:
        date, typ, _ = vals
        afm = ''
    else:
        raise ValueError('Error')
    return date, typ, afm


def parse_tranline(line, tvalue):
    vals = line.strip().split()
    lvals = len(vals)
    if lvals == 2:
        account, value = vals
        value = Dec.from_gr(value)
    elif lvals == 1:
        account = vals[0]
        value = -tvalue
    else:
        raise ValueError(f'line {line} Error')
    return account, value


def parse_check_point(line: str, data: dict):
    _, date, account, value = line.strip().split()
    data['check_points'].append(
        {
            'date': date,
            'account': account,
            'value': Dec.from_gr(value)
        }
    )


def parse(filename):
    ddata = {
        'set': {},
        'acc': {},
        'data': [],
        'check_points': [],
        'error_accounts': defaultdict(int)
    }
    re_par_per = re.compile(r'"[^"]*"')
    re_iso_date = re.compile(r'^\d{4}-\d{2}-\d{2}')
    re_afm = re.compile(r' \d{9}')
    inside_header = 0
    tran = {}
    trtotal = 0
    with open(filename) as fil:
        for lin in fil.readlines():
            if len(lin.strip()) == 0:
                continue
            elif lin.startswith(('#', ';', '?')):
                continue
            # Γραμμές σημείων ελέγχου
            elif lin.startswith('@'):
                parse_check_point(lin, ddata)
            # Γραμμές που ορίζουν διάφορες παραμέτρους
            elif lin.startswith('set'):
                parse_set(lin, ddata)
            # Γραμμές που ορίζουν τους ισχύοντες λογαριασμούς
            elif lin.startswith('acc'):
                parse_acc(lin, ddata)
            # έλεγχος αν είναι ημερομηνία iso (9999-99-99)
            elif re_iso_date.match(lin):
                # we are inside header
                inside_header = 1
                parper = re_par_per.findall(lin)
                if len(parper) == 1:
                    par = ''
                    per = parper[0]
                else:
                    par, per = re_par_per.findall(lin)
                found_afm = re_afm.search(lin)
                afm = found_afm.group().strip() if found_afm else ''
                dat, ledg, *_ = lin.strip().split()
                tran = {
                    'date': dat,
                    'ledger': ledg,
                    'par': par.replace('"', ''),
                    'per': per.replace('"', ''),
                    'afm': afm,
                    'lines': []
                }
                ddata['data'].append(tran)
                inside_header = 2
            elif re.match(r'^  .', lin):
                if inside_header in (0, 1):
                    raise ValueError(f'Error in line: {lin}')
                elif inside_header == 2:
                    acc, val = parse_tranline(lin, trtotal)
                    if acc == 'ΦΠΑ':  # Ειδική περίπτωση
                        pass
                    elif acc not in ddata['acc'].keys():
                        ddata['error_accounts'][acc] += 1
                    trtotal += val
                    tran['lines'].append({'account': acc, 'value': val})
            else:
                raise ValueError(f'File {filename} is not proper')
    return ddata
