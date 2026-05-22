import asyncio
import nest_asyncio
nest_asyncio.apply()
import market_data as md
    
async def main():
    ndays_to = 1
    ndays_from = md.get_year_bdays_from()
    incl = md.all
    symbols = md.get_symbols(incl)
    md.run_mdb_missing(symbols, ndays_from, ndays_to)

if __name__ == '__main__':
    asyncio.run(main())
