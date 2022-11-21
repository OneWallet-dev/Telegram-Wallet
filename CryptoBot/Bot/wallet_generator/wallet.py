import aiohttp
import asyncio


class Wallet:
    def __init__(self, api_key, blockchain, network):
        self.api_key = api_key
        self.main_url = "https://rest.cryptoapis.io/v2"
        self.blockchain = blockchain
        self.network = network

    async def headers(self):
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
        }
        return headers

    async def status(self):
        headers = await self.headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.main_url, headers=headers) as resp:
                print(await resp.text())

    async def list_supported_tokens(self):
        url = f"/wallet-as-a-service/info/{self.blockchain}/{self.network}/supported-tokens"
        querystring = {"context": "yourExampleString", "limit": 50, "offset": 0}
        headers = await self.headers()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.main_url + url, headers=headers, params=querystring) as resp:
                print(await resp.json())

    async def create_master_wallet(self, context, walletName, walletType):
        url = "/wallet-as-a-service/wallets/generate"
        payload = "{\"context\": \"{0}\",\"data\": {\"item\": {\"walletName\": \"{1}\",\"walletType\": \"{2}\"}}}"
        payload = payload.replace("{0}", walletName)
        payload = payload.replace("{1}", context)
        payload = payload.replace("{2}", walletType)
        headers = await self.headers()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.main_url + url, headers=headers, data=str(payload)) as resp:
                print(await resp.json())
                return await resp.json()

    async def generate_deposit_address(self, context, label, walletid):
        url = f"/wallet-as-a-service/wallets/{walletid}/{self.blockchain}/{self.network}/addresses"
        payload = "{\"context\": \"{0}\",\"data\": {\"item\": {\"label\": \"{1]\"}}}"
        payload = payload.replace("{0}", context)
        payload = payload.replace("{1}", label)
        headers = await self.headers()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.main_url + url, headers=headers, data=str(payload)) as resp:
                print(await resp.json())
                return await resp.json()

    async def transaction_addres_to_addres(self, context, walletid, from_address, to_address, amount, callbacksecretKey,
                                           callbackUrl, note, feePriority: str = "show"):
        """

        :param context:
        :param walletid: Represents the sender's specific and unique Wallet ID of the sender.
        :param from_address: Defines the specific source address for the transaction.
        :param to_address: Defines the specific recipient address for the transaction.
        For XRP we also support the X-address format
        :param amount: Represents the specific amount of the transaction
        :param callbacksecretKey: Represents the Secret Key value provided by the customer.
         This field is used for security purposes during the callback notification,
          in order to prove the sender of the callback as Crypto APIs.
        :param callbackUrl:Represents the URL that is set by the customer where the callback will be received at.
        :param note: Represents an optional note to add a free text in,
        explaining or providing additional detail on the transaction request.
        :param feePriority: Represents the fee priority of the automation, whether it is "slow", "standard" or "fast".
        :return:
        """
        url = f"/wallet-as-a-service/wallets/{walletid}/{self.blockchain}/" \
              f"{self.network}/addresses/{from_address}/transaction-requests"
        payload = "{\"context\": \"{0}\",\"data\": {\"item\": {\"amount\": \"{1}\"," \
                  "\"callbackSecretKey\": \"{2}\",\"callbackUrl\": \"{3}\"," \
                  "\"feePriority\": \"{4}\",\"note\": \"{5}\",\"recipientAddress\": \"{6}\"}}}"
        payload = payload.replace("{0}", context)
        payload = payload.replace("{1}", amount)
        payload = payload.replace("{2}", callbacksecretKey)
        payload = payload.replace("{3}", callbackUrl)
        payload = payload.replace("{4}", feePriority)
        payload = payload.replace("{5}", note)
        payload = payload.replace("{6}", to_address)
        payload = payload.replace("{5}", note)
        headers = await self.headers()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.main_url + url, headers=headers, data=str(payload)) as resp:
                print(await resp.json())
                return await resp.json()


async def main():
    wallets = Wallet("API-KEY", blockchain="tron", network="mainnet")
    # create wallet
    wallet = await wallets.create_master_wallet("context", "wallet_name", "main")
    wallet_id = wallet.get("data").get("item").get("walletId")

    # create address in wallet
    address_1 = await wallets.generate_deposit_address("address_1", "label", wallet_id)
    address_2 = await wallets.generate_deposit_address("address_2", "label", wallet_id)

    address_1_id = address_1.get("data").get("item").get("address")
    address_2_id = address_2.get("data").get("item").get("address")

    # create transaction
    transaction = await wallets.transaction_addres_to_addres(context="context", walletid=wallet_id,
                                                             from_address=address_1_id,
                                                             to_address=address_2_id, amount="10",
                                                             callbacksecretKey="key",
                                                             callbackUrl="https//", note="note", feePriority="fast")
    print(transaction)


asyncio.run(main())
