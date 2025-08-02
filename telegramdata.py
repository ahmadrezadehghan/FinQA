import asyncio
import os
import sys
from datetime import datetime

import pandas as pd
from telethon import TelegramClient, errors
from telethon.network.connection import ConnectionTcpAbridged, ConnectionTcpFull
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import SearchRequest
from telethon.errors import UsernameInvalidError, UsernameNotOccupiedError

# --- CONFIGURATION ---
api_id = 26759493
api_hash = '0cb5fa93f0446d248efed1951585e008'

# List of groups to scrape (public @username or your own naming)
groups = [
    'cryptoclubpump'
    'wallstreetqueenofficial',
    'BitDegree',
    'Ian Crypto Trades',
    'Crypto Box Shilling',
    'degenpump_crypto_pump_signals',
    'Mark_CryptoNews',
    'CryptoNinjas Trading',
    'Binance Signals',
    'Binance Community (Official)',
    'Kraken Exchange Official Group',
    'KuCoin Exchange (Official News Channel)',
    'KuCoin Announcement',
    'ProSignalsFX',
    'TopTradingSignals',
    'Vasily Trader',
    'EliteSignals',
    'UnitedSignals',
    'SignalProvider',
    'SureshotFX',
    'SGX Market Updates',
    'CNBC TV18',
    'Business & Finance News',
    'Market Masters',
    'StockPro Online',
    'InvestingLive Stocks',
    'Everyday Profit',
    'Jackpot TradeX',
    'Trading Hub',
    'Original Bull',
    'Honest Stock Marketer',
    'Bulls VS Bears',
    'Stock Gainers',
    'Stock Idea',
    'Nifty 50 & Stocks',
    'NIFTY 50 BANKNIFTY DOMINATOR',
    'Profits Everyday',
    'NSE STOCK PRO',
    'Shree Tech Analysis',
    'Usha’s Analysis',
    'Intraday TradeX',
    'Growth Stock',
    'Stox Master Advisory',
    'Equitymaster',
    'Rawat Traders',
    'Banknifty Nifty Trading',
    'Stock Thunder',
    'Ghanshyam Tech Analysis',
    'Stock Market Ninjas',
    'The Options Club',
    'StockPro Official',
    'Shivam Trading Academy',
    'TradeOnomics',
    '20PAISA.COM™',
    'Options Traders',
    'Fno Advisory',
    'Supreme Market',
    'Om Traders',
    'Bull Bear Trader',
    'Index Options Tips',
    'Stock Tips & Options',
    'Option Trading Masters',
    'Dollars and Sense',
    'The Financial Coconut',
    'Sethisfy',
    'Seedly',
    'binancekillers',
    'RAVEN Signals Pro',
    'whale_alert_io',
    'NansenSmartAlerts',
    'Stock Market News',
    'FinTwit',
    'Onchain Alerts',
    'Stocks Watchlist',
    'PUMPNOW800',
    'CoinGapeNews',
    'dash2trade',
    'VerifiedCryptoGroup',
    'whale_alert',
    'RocketWalletSignals',
    'OnwardBTC',
    '3commas_io',
    'JacobCryptoBury',
    'SatoshiCalls',
    'PhantomDegen',
    'TonnyDrops',
    'LimboTrade',
    'CryptoPublish',
    'CryptoFinance',
    'CryptoExtreme',
    'WuBlockchain',
    'CryptoAlert',
    'CryptoPanic',
    'CointelegraphNews',
    'BitcoinMagazine',
    'solana',
    'cryptoquant_official',
    'santiment_network',
    '1000pipbuilder',
    'FXLeaders',
    'FXPremiere',
    'ForexTradingTipsCallsSignals',
    'TradingCryptoBitcoinSignals',
    'OlympTradeQuotexSignals',
    'TradingBinomoSignalsTips',
    'ForexIncomeForever',
    'PIPS1000BUILDERSIGNAL',
    'learn2tradenews',
    'FXLeaders',
    'FXPremiere',
    'ForexTradingTipsCallsSignals',
    'TradingCryptoBitcoinSignals',
    'OlympTradeQuotexSignals',
    'TradingBinomoSignalsTips',
    'ForexIncomeForever',
    'AltSignalsFX',
    'GoldSignals_io',
    'ForexSignals_io',
    'ApexBull',
    'BullDogSignals',
    'FXLondon',
    'FreeSignalPro',
    'DailyForexSignals',
    'DailyFX',
    'dailyfxanalysis1',
    'ForexSignalsSMS',
    'ForexFactoryCom',
    'forexsupports',
    'ForexRobotNation',
    'ForexGalaxy',
    'FXStreetNews',
    'OANDA',
    'ICMarkets',
    'XM_Global',
    'IGNews',
    'Pepperstone',
    'HotForex',
    'FXTMOfficial',
    'FP_Mentors',
    'ForexAnalytics',
    'babypips',
    'investingcom',
    'tickmill',
    'Exness',
    'FBS_OfficialGroup',
    'RoboForex',
    'Swissquote_Official'
   'sharktrading',
   'FXCMOfficial',
   'FreeForexSignalsDaily',
   'ForexSignals',
   'Learn2Trade',
   'CryptoWhalePumps',
   'CryptoSignals',
   'AltSignals',
   'ChainCrawlers',
   'Cabal Lines',
   'Glassnode',
   'glassnodealerts',
   'Equity99',
   'GoldSignalsVIP',
   'AnabelSignals',
   'Bloomberg',
   'InvestmentMoats',
   'TradingView',
   'ForexVIPSignals',
   'dailyfxgroup',
   'GoldSignalsDaily',
   'ForexSignals',
   'BitcoinBullets',
   'FatPigSignals',
   'CryptoVIPSignal',
   'Learn2Trade',
   'AltSignals',
   'cryptoinnercircle',
   'binance_announcements',
   'CoinCodeCap',
   'WolfOfTrading',
   'Fed_Russian_Insiders',
   'BinanceKillers',
   'CryptoInsider',
   'cryptoairdrops',
   'CryptoMoneyGlobal',
   'CryptoMiami',
   'CryptoProfitCoach',
   'CabalLines',
   'ChainCrawlers',
   'glassnodealerts',
   'CoinMarketCap',
   'CoinGecko',
   'MessariCrypto',
   'EthereumNews',
   'CardanoAnnouncements',
   'PolkadotOfficial',
   'ChainlinkOfficial',
   'PolygonOfficial',
   'BinanceResearch',
   'RAVENSignalsPro',
]
# Optional per-group invite links
INVITE_LINKS = {
    name: os.getenv(f'INVITE_LINK_{name}')
    for name in groups
}

# Date range: messages from START_DATE up to now
START_DATE = datetime(2025, 1, 1)
END_DATE   = datetime.now()

# Where to save Excel files
EXCEL_FOLDER = r"C:\Users\AHMAD\Desktop\web_perper\excels"
os.makedirs(EXCEL_FOLDER, exist_ok=True)

# Connection methods to try
auth_methods = [ConnectionTcpAbridged, ConnectionTcpFull]


def create_client(connection):
    """Instantiate a TelegramClient with the given connection class."""
    return TelegramClient('crypto_scraper', api_id, api_hash, connection=connection)


async def start_client(max_retries=5, wait_sec=5):
    """Attempt to connect using different connection methods + retries."""
    for conn in auth_methods:
        client = create_client(conn)
        for attempt in range(1, max_retries + 1):
            try:
                print(f"Attempt {attempt} with {conn.__name__}...")
                await client.start()
                if await client.is_user_authorized():
                    print(f"✅ Connected with {conn.__name__}.")
                    return client
            except Exception as e:
                print(f"  • Error on attempt {attempt} ({conn.__name__}): {e}")
                await asyncio.sleep(wait_sec)
        print(f"⚠️  Failed using {conn.__name__}, trying next method.")
    return None


async def resolve_entity(client, group):
    """
    Resolve a group name to an entity:
     1) Try public @username
     2) If missing, attempt invite-link join
     3) Fallback: scan your dialogs for a matching title
     4) Fallback: public-chat search by title
    """
    # 1) direct username lookup
    try:
        return await client.get_entity(group)
    except (UsernameInvalidError, UsernameNotOccupiedError, errors.RPCError):
        print(f"– Username {group!r} not found or not public.")

    # 2) try invite link
    invite = INVITE_LINKS.get(group)
    if invite:
        try:
            print(f"– Trying to join {group!r} via invite link…")
            await client(JoinChannelRequest(invite))
            return await client.get_entity(group)
        except Exception as e:
            print(f"  ✗ Invite join failed for {group!r}: {e}")

    # 3) scan existing dialogs
    print("– Scanning your existing dialogs for a match…")
    async for dialog in client.iter_dialogs():
        title = dialog.name or ''
        if group.lower() in title.lower():
            print(f"  ✓ Found in dialogs: {title!r}")
            return dialog.entity

    # 4) public‐chat search
    print(f"– Searching public chats for '{group}'…")
    result = await client(SearchRequest(q=group, limit=5))
    if result.chats:
        chat = result.chats[0]
        uname = getattr(chat, 'username', None)
        print(f"  ✓ Using public chat: {chat.title!r} (@{uname or 'no-username'})")
        return chat

    raise ValueError(f"Could not resolve or access group {group!r}.")


async def fetch_group_messages(client, group):
    """Fetch messages for one group between START_DATE and END_DATE, save to Excel."""
    try:
        entity = await resolve_entity(client, group)
    except Exception as e:
        print(f"Skipping {group!r}: {e}")
        return

    offset_id = 0
    batch_num = 1
    total_saved = 0
    print(f"\nFetching '{group}' from {START_DATE.date()} to {END_DATE.date()}…")

    while True:
        try:
            msgs = await client.get_messages(entity, limit=100, offset_id=offset_id)
        except (errors.RPCError, OSError) as e:
            print(f"  • Error fetching batch {batch_num}: {e}")
            await asyncio.sleep(5)
            continue

        if not msgs:
            break

        records = []
        for m in msgs:
            dt = m.date.replace(tzinfo=None)
            if dt < START_DATE:
                break
            if dt <= END_DATE:
                records.append({
                    'Date':   dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'Source': group,
                    'Message': m.message or ''
                })

        if not records:
            break

        df = pd.DataFrame(records)
        filename = os.path.join(EXCEL_FOLDER, f"{group}.xlsx")

        if os.path.exists(filename):
            try:
                df_old = pd.read_excel(filename)
                df = pd.concat([df_old, df], ignore_index=True)
            except Exception as e:
                print(f"  ⚠️ Warning: could not append to '{filename}': {e}")

        try:
            df.to_excel(filename, index=False, sheet_name='Messages')
            saved = len(records)
            total_saved += saved
            print(f"  Batch {batch_num}: saved {saved} messages")
        except Exception as e:
            print(f"  ✗ Error saving '{filename}': {e}")
            break

        offset_id = msgs[-1].id
        batch_num += 1

    print(f"✅ Completed '{group}', total messages saved: {total_saved}")


async def main():
    client = await start_client()
    if not client:
        print("🚨 Unable to connect. Exiting.")
        sys.exit(1)

    for group in groups:
        await fetch_group_messages(client, group)

    await client.disconnect()
    print("\nAll groups processed:")
    for g in groups:
        print(f" - {g}")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
