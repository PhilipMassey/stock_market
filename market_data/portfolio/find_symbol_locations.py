import os
import pandas as pd
import market_data as md
import argparse

def find_and_optionally_delete_symbols(symbols, delete=False):
    """
    Search through all CSV files in the market_data/data directory
    and return a dictionary showing which files contain each symbol.
    If delete=True, it will remove those symbols from the CSV files.
    """
    data_dir = md.data_dir
    locations = {symbol: [] for symbol in symbols}
    
    # Ensure all symbols are uppercase for case-insensitive matching
    symbols_upper = [s.upper() for s in symbols]
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    
                    # Look for columns that might contain symbols ('Symbol', 'Ticker', etc.)
                    symbol_col = None
                    for col in df.columns:
                        if str(col).lower() in ['symbol', 'ticker', 'symbols']:
                            symbol_col = col
                            break
                            
                    # Fallback: assume first column
                    if not symbol_col and not df.empty:
                        symbol_col = df.columns[0]
                        
                    if symbol_col and not df.empty:
                        # Extract all symbols from the file
                        file_symbols = df[symbol_col].dropna().astype(str).str.upper().tolist()
                        
                        # Get the relative path to extract Directory & Portfolio
                        rel_path = os.path.relpath(file_path, data_dir)
                        dir_name = os.path.dirname(rel_path)
                        port_name = os.path.splitext(os.path.basename(rel_path))[0]
                        
                        location_str = f"Directory: '{dir_name}' | Portfolio: '{port_name}'"
                        
                        file_modified = False
                        
                        # Check against our target list
                        for i, sym in enumerate(symbols_upper):
                            if sym in file_symbols:
                                locations[symbols[i]].append(location_str)
                                if delete:
                                    # Filter out the symbol (case-insensitive match)
                                    df = df[df[symbol_col].astype(str).str.upper() != sym]
                                    file_modified = True
                                    
                        # If we need to delete and the file was modified, save it
                        if delete and file_modified:
                            df.to_csv(file_path, index=False)
                            print(f"Removed targeted symbols and saved: {file_path}")
                            
                except Exception as e:
                    pass # Safely skip unreadable files
                    
    return locations

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find and optionally delete specific symbols across all market data portfolios.')
    parser.add_argument('symbols', nargs='*', default=['AETUF', 'AMBP', 'AUGO', 'CRRFY', 'CTRA', 'GLXY', 'HUT', 'LYB', 'SLAB', 'SNCY'],
                        help='List of symbols to find/delete (defaults to the hardcoded OTC list)')
    parser.add_argument('--delete', action='store_true', help='If passed, actually deletes the symbols from the CSV files')
    
    args = parser.parse_args()
    
    symbols_to_process = args.symbols
    
    mode_text = "FINDING AND DELETING" if args.delete else "SEARCHING FOR"
    print(f"{mode_text} {len(symbols_to_process)} symbols across all market data files...\n")
    
    locations = find_and_optionally_delete_symbols(symbols_to_process, delete=args.delete)
    
    for sym, locs in locations.items():
        if locs:
            status = "❌ DELETED FROM:" if args.delete else "✅ FOUND IN:"
            print(f"\n{status} {sym}")
            for loc in locs:
                print(f"     - {loc}")
        else:
            print(f"\n➖ {sym}: NOT FOUND ANYWHERE")
