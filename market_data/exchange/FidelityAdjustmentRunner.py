
from market_data.exchange.FidelityAdjustments import FidelityAdjustments


if __name__ == '__main__':
    portfolios = ['Alpha Picks', 'Dividends', 'ETFs', 'Stocks']
    for portfolio in portfolios:
        xlsxfilenane = portfolio + '.xlsx'
        CombHoldStand = md.CombineHoldingsStandards(portfolio + ' Standards.xlsx' ,xlsxfilenane)
        CombHoldStand.prepare_df_fidelity()

        xldf_proc = md.AdjustmentFromHoldingsStandards(CombHoldStand.df_fidelity)
        directory = join(md.download_dir, 'Fidelity Adjustments')
        xldf_proc.create_excel_writer(directory, xlsxfilenane)
        xldf_proc.write_totals_row()
        xldf_proc.write_col_formula(op='-', cols = ['Buy/Sell %' ,'Holding %' ,'Current Value %'])
        xldf_proc.write_sum_formulas()
        xldf_proc.write_current_return_percent()
        xldf_proc.write_current_value_percent()
        xldf_proc.write_buy_sell_dollar()
        xldf_proc.format_sheet()
