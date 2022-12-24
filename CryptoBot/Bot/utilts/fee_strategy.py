from Dao.models.Address import Address


async def getFeeStrategy(address: Address):
    #owner: Owner = address.wallet.owner
    # TODO Надо придумать откуда брать фи
    return 0