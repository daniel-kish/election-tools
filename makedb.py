import csv
import sys
import argparse
import json
import sqlite3
import codecs
import os


fields_type = {
    "region": "text",
    "oik": "text",
    "tik": "text",
    "uik": "text",
    "votersReg": "integer",
    "ballotsAllocated": "integer",
    "ballotsIssuedEarly": "integer",
    "ballotsIssuedOnStation": "integer",
    "ballotsIssuedOutside": "integer",
    "ballotsCancelled": "integer",
    "ballotsInMobileBoxes": "integer",
    "ballotsInStationaryBoxes": "integer",
    "invalidBallots": "integer",
    "validBallots": "integer",
    "lostBallots": "integer",
    "unaccountedBallots": "integer",
    "ballotsIssued": "integer",
    "ballotsFound": "integer"
}


def subseq(query, base):
    l = len(query)
    for i in range(len(base)):
        if base[i:i+l] == query:
            return i
    return -1

def get_table(csv_path, delim_char):
    with open(args.csv) as f:
        reader = csv.reader(f, delimiter=delim_char)
        row = next(reader)
        data_row = next(reader)

        headers = []
        values = []
        for i in range(0, len(row)):
            headers.append(row[i])
            values.append(data_row[i])

        return headers, values


def get_protocol_table(protocol_path):
    with open(protocol_path) as f:
        gas_data = f.read()
    gas_lines = [[y for y in line.split('\t') if y] for line in gas_data.split('\n')]
    gas_lines = filter(lambda x: len(x) > 1, gas_lines)

    gas_fields = [x[1] for x in gas_lines]
    gas_values = [x[2] for x in gas_lines]

    return gas_fields, gas_values


def mk_all_fields_list(config):
    col_defns = [] # [ (field_name, type) ]
    for field_cfg in config['fields']:
        if len(field_cfg) < 3:
            col_defns.append((field_cfg[1], fields_type[field_cfg[1]]))
        elif field_cfg[-1] == 'cand':
            col_defns.append((field_cfg[1], "integer"))
            col_defns.append((field_cfg[1] + "_res", "real"))
    for add_field in config['additional_fields']:
        col_defns.append((add_field[0], "integer"))
    col_defns.append(("turnout", "real"))

    return col_defns


def mk_create_table_query(col_defns):
    rowsClause = ', '.join("{} {}".format(*x) for x in col_defns)
    createQuery = 'CREATE TABLE IF NOT EXISTS {table_name} ({rowsClause})'.format(rowsClause=rowsClause, table_name=config['table_name'])
    return createQuery


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", help="path to JSON config file")
    parser.add_argument("--csv", help="path to CSV file", required=True)
    parser.add_argument("--enum-cols", action="store_true", help="Show column names of CSV with their indices")
    parser.add_argument("--protocol", help="Protocol copy pasted from the izbirkom.ru page for field hints")
    parser.add_argument("--delim", default='tab', help="Delimiter to use for CSV parsing")
    parser.add_argument("--db", help="Path to create DB at")

    args = parser.parse_args()

    delim_char = ' '

    if args.delim == "tab":
        delim_char = '\t'
    elif args.delim == "comma":
        delim_char = ','

    if args.enum_cols:
        headers, values = get_table(args.csv, delim_char)

        if not args.protocol:
            for i in range(0, len(headers)):
                print(u"{} {} {}".format(i, headers[i].decode('utf-8'), values[i].decode('utf-8')))

        if args.protocol:
            proto_fields, proto_values = get_protocol_table(args.protocol)
            p = subseq(proto_values, values)
            for i in range(0, len(headers)):
                pf = proto_fields[i - p] if i >= p else "---"
                print(u"{:>2} {:>5} {:>30} {}".format(i, headers[i], values[i].decode('utf-8'), pf.decode('utf-8')))
        exit(0)

    if not args.config:
        print("Need a config file")
        exit(2)

    with open(args.config) as f:
        config = json.load(f)

    # validate config
    for field_cfg in config['fields']:
        if len(field_cfg) <= 2 and field_cfg[1] not in fields_type:
            print("Unknown non-candidate field: {}".format(field_cfg[1])) 
            exit(1)

    cols_defns = mk_all_fields_list(config)
    create_q = mk_create_table_query(cols_defns)

    conn = sqlite3.connect(args.db)
    c = conn.cursor()
    c.execute(create_q)

    rows = []
    with open(args.csv) as f:
        reader = csv.reader(f, delimiter=delim_char)
        for row in reader:
            rows.append(row)
    
    fields_to_idx = {x[1]: x[0] for x in config['fields']}
    idx_to_fields = {x[0]: x[1] for x in config['fields']}
    additional_fields = {x[0]: x[1] for x in config['additional_fields']}
    
    err_log_path = os.path.join(os.path.dirname(args.db), "error-log.txt")
    errors = codecs.open(err_log_path, mode="w", encoding='utf-8')

    cnt = 0
    for row in rows[1:]:
        try:
            print("\r{}/{}".format(cnt, len(rows)-1))
            cnt += 1

            cols_values = dict()

            # usual fields calculation
            for field_info in config['fields']:
                idx = field_info[0]
                name = field_info[1]
                if name in fields_type and fields_type[name] == 'text':
                    v = u'"' + row[idx].decode('utf-8') + u'"'
                else:
                    v = row[idx]
                cols_values[name] = v

            # additional fields calculation
            for af_name, names in additional_fields.items():
                cols_values[af_name] = sum([int(row[fields_to_idx[name]]) for name in names])

            # turnout calculation
            if int(cols_values["votersReg"]) == 0:
                cols_values["turnout"] = 0.0
            else:
                cols_values["turnout"] = float(cols_values["ballotsIssued"]) / float(cols_values["votersReg"])

            # <candidate>_res calculation
            for name, ftype in cols_defns:
                if not name.endswith(u"_res"):
                    continue
                if int(cols_values["ballotsFound"]) == 0:
                    cols_values[name] = 0.0
                else:
                    cols_values[name] = float(row[fields_to_idx[name[:-4]]]) / float(cols_values["ballotsFound"])

            values = []
            for name, ftype in cols_defns:
                values.append(unicode(cols_values[name]))

            query = u"INSERT INTO {table_name} VALUES ({})".format(', '.join(values),
                                                                   table_name=config['table_name'])
            c.execute(query)
        except Exception as x:
            errors.write("Error: {}\n".format(x))
            for i in range(0, len(row)):
                errors.write(rows[0][i].decode('utf-8') + u': "' + row[i].decode('utf-8') + u'"' + u'\n')
            errors.write(u'\n\n')
            continue
    conn.commit()
    conn.close()
