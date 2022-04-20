import json
import requests

headers = [{
            'X-API-Key': 'd94cc41dff3de985d5730803b5020da1', #kyle
            'Content-Type': 'application/json',
        },
        {
            'X-API-Key': '9374064d28d4f4d52a8a7dda4ce7d826', #feridot
            'Content-Type': 'application/json',
        },
        {
            'X-API-Key': '10019fa39a7dcd40e3633f1ae4b7609e', #Rhee
            'Content-Type': 'application/json',         
        }]

header_index = 0

def get_account_balance(acount_address):
    global header_index
    header_index += 1
    data_row = {'key': acount_address}
    response = requests.post(f'https://khala.api.subscan.io/api/v2/scan/search', headers=headers[header_index % len(headers)], data=json.dumps(data_row))
    json_obj = response.json()
     
    return json_obj

def get_current_price() -> list:

    headers = {
      'accept': 'application/json',
    }
    url = f'https://api.coingecko.com/api/v3/simple/price?ids=pha&vs_currencies=usd'


    response = requests.get(url, headers=headers)

    data = response.json()
    
    pricedata = data.get('pha').get('usd')
    return (pricedata)

if __name__ == '__main__':
    print(get_current_price())