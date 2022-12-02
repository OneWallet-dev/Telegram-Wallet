from Dao.models.Address import Address
from Dao.models.Owner import Owner


async def getFeeStrategy(address: Address):
    owner: Owner = address.wallet.owner
    # TODO Надо придумать откуда брать фи
    return 0