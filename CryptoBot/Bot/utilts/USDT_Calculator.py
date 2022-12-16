import json
import requests


class USDT_Calculator:
    def __init__(self):
        self.api_ulr = "https://api.binance.com/api/v1/ticker/24hr?symbol="
    def calculate(self, amount:float, token_name: str) -> float:
        ticker_name = f"{token_name.upper()}USDT" #TRXUSDT
        print(f"{self.api_ulr}{ticker_name}")
        response = requests.get(f"{self.api_ulr}{ticker_name}") #https://api.binance.com/api/v1/ticker/24hr?symbol=USDTTRX
        print(response.text)#
        response_json = response.text
        last_price:float = self.get_lastprice_from_response(response_json)

        result = amount*last_price
        print(result)
        return result

    def get_lastprice_from_response(self,response_json:str)->float:
        #write your code
        response_dict: dict[str, str] = json.loads(response_json)
        value = response_dict["lastPrice"]
        return float(value)


USDT_Calculator().calculate(10,"btc")
