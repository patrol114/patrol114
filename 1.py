import os
import asyncio
import json
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from kucoinfutures import KucoinfuturesAsync, KucoinfuturesWs

# Załaduj zmienne środowiskowe
load_dotenv()

# Konfiguracja API
api_key = os.getenv('KUCOIN_API_KEY')
api_secret = os.getenv('KUCOIN_API_SECRET')
api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')

# Sprawdź czy klucze API są dostępne
if not all([api_key, api_secret, api_passphrase]):
    raise ValueError("Brak kluczy API! Ustaw zmienne środowiskowe w pliku .env")

# Konfiguracja poświadczeń
credentials = {
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase
}

class KuCoinFuturesTrader:
    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.rest_client = None
        self.ws_client = None
        self.symbol = "XBTUSDTM"  # Domyślny symbol

    async def initialize_clients(self):
        """Inicjalizacja klientów REST i WebSocket"""
        print("🚀 Inicjalizacja klientów KuCoin Futures...")
        
        # Klient REST
        self.rest_client = KucoinfuturesAsync(self.credentials)
        
        # Klient WebSocket
        self.ws_client = KucoinfuturesWs(self.credentials)
        
        print("✅ Klienci zostali zainicjalizowani pomyślnie")

    async def fetch_account_info(self):
        """Pobierz informacje o koncie"""
        try:
            print("\n💰 Pobieranie informacji o koncie...")
            
            # Pobierz saldo konta
            balance = await self.rest_client.fetch_balance()
            print("📊 Saldo konta Futures:")
            
            if balance:
                for currency, info in balance.items():
                    if float(info.get('total', 0)) > 0:
                        print(f"  💲 {currency}: {info.get('total', 'N/A')} "
                              f"(dostępne: {info.get('free', 'N/A')})")
            else:
                print("  ⚠️ Brak dostępnych środków")
                
        except Exception as e:
            print(f"❌ Błąd podczas pobierania informacji o koncie: {e}")

    async def fetch_market_data(self):
        """Pobierz dane rynkowe"""
        try:
            print(f"\n📈 Pobieranie danych rynkowych dla {self.symbol}...")
            
            # Pobierz ticker
            ticker = await self.rest_client.fetch_ticker(self.symbol)
            print(f"📊 Ticker {self.symbol}:")
            print(f"  💰 Cena ostatnia: {ticker.get('last', 'N/A')} USDT")
            print(f"  📈 Najwyższa (24h): {ticker.get('high', 'N/A')} USDT")
            print(f"  📉 Najniższa (24h): {ticker.get('low', 'N/A')} USDT")
            print(f"  📊 Wolumen (24h): {ticker.get('baseVolume', 'N/A')}")
            print(f"  📊 Zmiana (24h): {ticker.get('percentage', 'N/A')}%")
            
            # Pobierz order book
            order_book = await self.rest_client.fetch_order_book(self.symbol, limit=5)
            print(f"\n📋 Order Book {self.symbol} (Top 5):")
            
            if 'bids' in order_book and order_book['bids']:
                print("  🟢 Bids (kupno):")
                for i, (price, amount) in enumerate(order_book['bids'][:5]):
                    print(f"    {i+1}. Cena: {price:.2f}, Ilość: {amount:.4f}")
            
            if 'asks' in order_book and order_book['asks']:
                print("  🔴 Asks (sprzedaż):")
                for i, (price, amount) in enumerate(order_book['asks'][:5]):
                    print(f"    {i+1}. Cena: {price:.2f}, Ilość: {amount:.4f}")
                    
        except Exception as e:
            print(f"❌ Błąd podczas pobierania danych rynkowych: {e}")

    async def fetch_trading_info(self):
        """Pobierz informacje o tradingu"""
        try:
            print(f"\n🔄 Pobieranie informacji o tradingu...")
            
            # Pobierz otwarte zlecenia
            open_orders = await self.rest_client.fetch_open_orders(self.symbol)
            print(f"📋 Otwarte zlecenia dla {self.symbol}:")
            
            if open_orders:
                for order in open_orders[:5]:  # Pokaż maksymalnie 5 zleceń
                    print(f"  📄 ID: {order.get('id', 'N/A')}")
                    print(f"      Typ: {order.get('type', 'N/A')}, "
                          f"Strona: {order.get('side', 'N/A')}")
                    print(f"      Cena: {order.get('price', 'N/A')}, "
                          f"Ilość: {order.get('amount', 'N/A')}")
                    print(f"      Status: {order.get('status', 'N/A')}")
                    print()
            else:
                print("  ✅ Brak otwartych zleceń")
                
            # Pobierz ostatnie transakcje
            try:
                my_trades = await self.rest_client.fetch_my_trades(self.symbol, limit=5)
                print(f"📊 Ostatnie transakcje dla {self.symbol}:")
                
                if my_trades:
                    for trade in my_trades:
                        print(f"  💱 ID: {trade.get('id', 'N/A')}")
                        print(f"      Strona: {trade.get('side', 'N/A')}, "
                              f"Cena: {trade.get('price', 'N/A')}")
                        print(f"      Ilość: {trade.get('amount', 'N/A')}, "
                              f"Koszt: {trade.get('cost', 'N/A')}")
                        print(f"      Data: {trade.get('datetime', 'N/A')}")
                        print()
                else:
                    print("  ✅ Brak ostatnich transakcji")
            except Exception as e:
                print(f"  ⚠️ Nie udało się pobrać transakcji: {e}")
                
        except Exception as e:
            print(f"❌ Błąd podczas pobierania informacji o tradingu: {e}")

    async def fetch_positions_info(self):
        """Pobierz informacje o pozycjach"""
        try:
            print(f"\n📍 Pobieranie informacji o pozycjach...")
            
            # Pobierz pozycje
            positions = await self.rest_client.fetch_positions([self.symbol])
            print("📊 Aktualne pozycje:")
            
            if positions:
                for position in positions:
                    if float(position.get('contracts', 0)) != 0:
                        print(f"  📈 Symbol: {position.get('symbol', 'N/A')}")
                        print(f"      Strona: {position.get('side', 'N/A')}")
                        print(f"      Rozmiar: {position.get('contracts', 'N/A')}")
                        print(f"      Cena wejścia: {position.get('entryPrice', 'N/A')}")
                        print(f"      Cena oznaczenia: {position.get('markPrice', 'N/A')}")
                        print(f"      PnL: {position.get('unrealizedPnl', 'N/A')}")
                        print(f"      Procent PnL: {position.get('percentage', 'N/A')}%")
                        print()
            else:
                print("  ✅ Brak otwartych pozycji")
                
        except Exception as e:
            print(f"❌ Błąd podczas pobierania pozycji: {e}")

    async def fetch_market_symbols(self):
        """Pobierz dostępne symbole rynkowe"""
        try:
            print("\n🏪 Pobieranie listy dostępnych symboli...")
            
            # Pobierz rynki
            markets = await self.rest_client.fetch_markets()
            print(f"📊 Dostępne symbole kontraktów futures (pierwsze 10):")
            
            futures_symbols = []
            for symbol, market in markets.items():
                if market.get('type') == 'future':
                    futures_symbols.append(symbol)
                    
            for symbol in futures_symbols[:10]:
                market_info = markets[symbol]
                print(f"  💹 {symbol} - {market_info.get('base', 'N/A')}"
                      f"/{market_info.get('quote', 'N/A')}")
                print(f"      Status: {market_info.get('active', 'N/A')}")
                      
        except Exception as e:
            print(f"❌ Błąd podczas pobierania symboli: {e}")

    async def watch_real_time_data(self, duration: int = 60):
        """Obserwuj dane w czasie rzeczywistym przez WebSocket"""
        try:
            print(f"\n🔴 LIVE - Uruchamianie obserwacji danych real-time dla {self.symbol}...")
            print(f"⏱️ Czas trwania: {duration} sekund")
            print("📊 Naciśnij Ctrl+C aby zakończyć wcześniej")
            
            # Licznik aktualizacji
            update_count = 0
            
            async def handle_order_book_update():
                nonlocal update_count
                async for order_book in self.ws_client.watch_order_book(self.symbol):
                    update_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"\n🕐 [{timestamp}] Update #{update_count} - Order Book {self.symbol}:")
                    
                    # Najlepsze bids (kupno)
                    bids = order_book.get('bids', [])[:3]
                    if bids:
                        print("  🟢 Top 3 Bids:")
                        for i, (price, amount) in enumerate(bids):
                            print(f"    {i+1}. {price:.2f} USDT × {amount:.4f}")
                    
                    # Najlepsze asks (sprzedaż)
                    asks = order_book.get('asks', [])[:3]
                    if asks:
                        print("  🔴 Top 3 Asks:")
                        for i, (price, amount) in enumerate(asks):
                            print(f"    {i+1}. {price:.2f} USDT × {amount:.4f}")
                    
                    # Spread
                    if bids and asks:
                        spread = float(asks[0][0]) - float(bids[0][0])
                        print(f"  📊 Spread: {spread:.2f} USDT")
                    
                    print("-" * 50)
            
            # Uruchom obserwację z limitem czasu
            await asyncio.wait_for(handle_order_book_update(), timeout=duration)
            
        except asyncio.TimeoutError:
            print(f"\n⏰ Zakończono obserwację real-time po {duration} sekundach")
        except KeyboardInterrupt:
            print("\n⏹️ Obserwacja real-time przerwana przez użytkownika")
        except Exception as e:
            print(f"\n❌ Błąd podczas obserwacji real-time: {e}")

    async def cleanup(self):
        """Zamknij połączenia"""
        print("\n🧹 Zamykanie połączeń...")
        
        if self.rest_client:
            await self.rest_client.close()
            print("✅ Klient REST zamknięty")
            
        if self.ws_client:
            await self.ws_client.close()
            print("✅ Klient WebSocket zamknięty")

async def main():
    """Główna funkcja programu"""
    # Inicjalizacja na Windows (jeśli potrzebne)
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    trader = KuCoinFuturesTrader(credentials)
    
    try:
        # Inicjalizacja klientów
        await trader.initialize_clients()
        
        # Pobierz informacje o koncie
        await trader.fetch_account_info()
        
        # Pobierz dane rynkowe
        await trader.fetch_market_data()
        
        # Pobierz informacje o tradingu
        await trader.fetch_trading_info()
        
        # Pobierz informacje o pozycjach
        await trader.fetch_positions_info()
        
        # Pobierz dostępne symbole
        await trader.fetch_market_symbols()
        
        # Obserwuj dane w czasie rzeczywistym (60 sekund)
        await trader.watch_real_time_data(duration=60)
        
    except Exception as e:
        print(f"❌ Błąd w głównej funkcji: {e}")
    finally:
        # Zawsze zamknij połączenia
        await trader.cleanup()

if __name__ == '__main__':
    print("🎯 KuCoin Futures API - Comprehensive Trading Bot")
    print("=" * 60)
    asyncio.run(main())
