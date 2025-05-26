import db.py_mongo_test as db
import datetime
from bson.objectid import ObjectId


def get_smartlab_data(instrument: str):
    res = ""
    # print('get_smartlab_data', instrument)
    instrument = instrument.split('\n')[0]
    result = db.find_document({"symbol": instrument}, "smartlab_data")
    columns = db.find_document({}, "smartlab_columns", multiple=True)
    # print('get_smartlab_data',instrument, result)
    # print(columns)
    ### Mock ###
    columns_ = dict(zip([x['name_eng'] for x in columns], [x['name_rus'] for x in columns]))
    for key, value in result.items():
        if key == '_id' or value is None:
            continue
        if key in columns_.keys():
            res += f"- *{columns_.get(key)}*: {value}" + "\n"
        else:
            res += f"{key} {value}" + "\n"
    return res


def get_risk_data():
    res = ""
    result = db.find_document({}, "risk", multiple=True)
    ### Mock ###
    result_ = sorted([x for x in result if x['downside_dev'] != 0], key=lambda x: x['downside_dev'])[:10]
    if len(result_) > 0:
        res += "`\nname    downside_dev  volatility" + "\n" + "______________________________" + "\n"
        f_len = max([len(x['name']) for x in result_])
        for it in result_:
            name_ = it['name'] + " " * (f_len - len(it['name']))
            res += f"\n{name_}  {round(it['downside_dev'], 2)}       {round(it['volatility'], 2)}"
        res += "`"
    return res


def get_predictions():
    res = ""
    result_grow = db.find_document({'predict': 1}, "predictions", multiple=True)
    result_fall = db.find_document({'predict': 0}, "predictions", multiple=True)
    ### Mock ###
    grow_symbols = [x['symbol'] for x in result_grow]
    res = result_grow
    return res


# print(get_smartlab_data('PHOR'))
# print(get_risk_data())
# print(get_predictions())
