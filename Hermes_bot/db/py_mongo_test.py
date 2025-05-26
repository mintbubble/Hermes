import pymongo
import re
from bson.objectid import ObjectId

client = pymongo.MongoClient('localhost', 27017)
db = client['hermes_db']


def insert_document(data, collection):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    collection_obj = db[collection]
    return collection_obj.insert_one(data).inserted_id


def find_document(elements, collection, multiple=False):
    """ Function to retrieve single or multiple documents from a provided
    Collection using a dictionary containing a document's elements.
    """
    collection_obj = db[collection]
    # print(collection_obj)
    # print(elements)
    if multiple:
        results = collection_obj.find(elements)
        return [r for r in results]
    else:
        ### Mock ###
        # return {'_id': ObjectId('6737e6750cf4067423696d98'), 'Report_date': '28.08.2024', 'Report_currency': 'RUB',
        #           'Revenue': 1.5, 'Operating_profit': 0.337, 'EBITDA': 0.197, 'Operating_cashflow': 0.496,
        #           'CAPEX': 0.216, 'FCF': 0.273, 'Dividend_payout': 0.111, 'Dividend': '1,2', 'Dividends_profit': '11%',
        #           'Oper_expenses': 1.16, 'Depreciation': 0.1, 'Interest_expenses': 0.053, 'Assets': 2.51,
        #           'Net_assets': 0.433, 'Debt': 0.61, 'Cash': 0.37, 'Net_debt': 0.24, 'JSC_share_price': 101.8,
        #           'JSC_share_number': 92.6, 'Capitalization': 9.43, 'EV': 9.67, 'Balancesheet_value': -0.39,
        #           'EPS': 10.4, 'FCF_share': 2.94, 'BV_share': -4.19, 'EBITDA_return': '13.2%', 'Net_return': '64.7%',
        #           'FCF_yield': '2.9%', 'ROE': '223.6%', 'ROA': '38.6%', 'PE': 9.74, 'PFCF': 34.6, 'PS': 6.31,
        #           'PBV': -24.3, 'EVEBITDA': 49.1, 'DebtEBITDA': 1.22, 'RD_CAPEX': 0, 'CAPEX_Revenue': '14%',
        #           'symbol': 'ABIO'}
        return collection_obj.find_one(elements)


def update_document(query_elements, new_values, collection):
    """ Function to update a single document in a collection.
    """
    collection_obj = db[collection]
    collection_obj.update_one(query_elements, {'$set': new_values})


def delete_document(query, collection):
    """ Function to delete a single document from a collection.
    """
    collection_obj = db[collection]
    collection_obj.delete_one(query)


# print(find_document({'symbol': 'VTBR RX'}, "smartlab_data")) #.metadata.json
# print(find_document({}, "smartlab_columns", multiple=True))
# print(find_document({}, "risk", multiple=True))
# rgx = re.compile('.*PHOR.*', re.IGNORECASE)
# print(find_document({"ticker": f'PHOR'}, "risk"))
# print(find_document({'ticker':{'$regex':'PHOR'}}, "risk"))
# print(find_document({'ticker':{'$regex':'PHOR'}}, "risk"))