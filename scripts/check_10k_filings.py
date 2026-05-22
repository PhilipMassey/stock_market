import requests
import pandas as pd
import market_data as md
import time
import argparse

def get_latest_10k_filings(symbols):
    """
    Fetches the latest 10-K filing dates and URLs for a list of symbols
    using the official (and free) SEC EDGAR API.
    """
    # The SEC requires a custom User-Agent in the format: "Name Email"
    headers = {'User-Agent': 'Philip Massey philipmassey@example.com'}
    
    print("1. Fetching SEC ticker-to-CIK mapping...")
    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(tickers_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch tickers: {response.status_code}")
        return pd.DataFrame()
        
    tickers_data = response.json()
    
    # Create mapping of Ticker -> CIK
    ticker_to_cik = {}
    for item in tickers_data.values():
        ticker_to_cik[item['ticker']] = str(item['cik_str']).zfill(10)
        
    print(f"   Found mapping for {len(ticker_to_cik)} total SEC registered companies.\n")
    
    print(f"2. Querying recent filings for {len(symbols)} portfolio symbols...")
    results = []
    
    for i, ticker in enumerate(symbols):
        ticker = ticker.upper()
        if ticker not in ticker_to_cik:
            print(f"   [{ticker}] CIK not found in SEC database. (Skipping)")
            continue
            
        cik = ticker_to_cik[ticker]
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        
        try:
            res = requests.get(submissions_url, headers=headers)
            
            if res.status_code != 200:
                print(f"   [{ticker}] Failed to fetch submissions: {res.status_code}")
                continue
                
            data = res.json()
            recent_filings = data['filings']['recent']
            
            # Find the latest 10-K
            found_10k = False
            for j in range(len(recent_filings['form'])):
                if recent_filings['form'][j] == '10-K':
                    filing_date = recent_filings['filingDate'][j]
                    accession_number = recent_filings['accessionNumber'][j].replace('-', '')
                    primary_doc = recent_filings['primaryDocument'][j]
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_number}/{primary_doc}"
                    
                    results.append({
                        'Symbol': ticker,
                        'Filing Date': filing_date,
                        'URL': doc_url
                    })
                    print(f"   [{ticker}] Latest 10-K: {filing_date}")
                    found_10k = True
                    break
                    
            if not found_10k:
                print(f"   [{ticker}] No 10-K found in recent filings.")
                
        except Exception as e:
            print(f"   [{ticker}] Error: {e}")
            
        # SEC allows max 10 requests per second. Let's sleep for 0.15s to be safe.
        time.sleep(0.15)
        
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        # Sort by filing date descending so the newest ones are at the top
        df_results = df_results.sort_values('Filing Date', ascending=False).reset_index(drop=True)
        
    return df_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check latest 10-K filings for portfolio.')
    parser.add_argument('--dir', type=str, default='Holding', help='Directory name (default: Holding)')
    parser.add_argument('--port', type=str, default='Stocks', help='Portfolio name (default: Stocks)')
    
    args = parser.parse_args()
    
    directory = args.dir
    port = args.port
    
    symbols = md.get_symbols_dir_or_port(directory=directory, port=port)
    print(f"Loaded {len(symbols)} symbols from Directory: '{directory}', Portfolio: '{port}'\n")
    
    df_10k = get_latest_10k_filings(symbols)
    
    if not df_10k.empty:
        print("\n--- SUMMARY OF RECENT 10-K FILINGS ---")
        print(df_10k[['Symbol', 'Filing Date']].to_string())
        
        # Save to CSV for easy review
        csv_file = f"10K_Filings_{directory}_{port}.csv"
        df_10k.to_csv(csv_file, index=False)
        print(f"\nDetailed results with URLs saved to: {csv_file}")
    else:
        print("\nNo 10-K data could be retrieved.")
