import market_data as md

if __name__ == '__main__':
    seeking_symbols = []
    for port in md.portfolios:
        seeking_symbols.extend(md.get_symbols_dir_and_port(md.sa, 'Current ' + port))
    seeking_symbols = set(seeking_symbols)
    fidelity_symbols = set(md.get_symbols(md.holding))
    print('fidelity extras ', fidelity_symbols.difference(seeking_symbols))
    print('seeking extras ', seeking_symbols.difference(fidelity_symbols))