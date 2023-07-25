

import plotly.express as px
def plot_df_xaxis_yaxis(df, title, barorbubble, x_axis, y_axis):
    print('{} {}'.format(min(df.percent.values), max(df.percent.values)))
    df.sort_values(by=['date', 'percent'], ascending=[False, False], inplace=True)
    if barorbubble == 'bubble':
        fig = px.scatter(df, x=x_axis, y=y_axis,
                         animation_frame="date", animation_group=None,
                         size="volume", color='portfolio', hover_name='portfolio',
                         #llog_x=False, log_y=False,
                         size_max=50,
                         range_x=[0, len(set(df.portfolio.values))],
                         range_y=[min(df.percent.values), max(df.percent.values)],
                         width=1450, height=1000,
                         title=title)
    else:
        fig = px.bar(df, x=x_axis, y=y_axis,
                     color=x_axis, hover_name=x_axis,
                     animation_frame="date", animation_group=None,
                     log_x=False, log_y=False,
                     range_x=[0, len(set(df.portfolio.values))],
                     range_y=[min(df.percent.values), max(df.percent.values)],
                     width=1450, height=1000,
                     title=title)

    fig["layout"].pop("updatemenus")  # optional, drop animation buttons
    fig.show()
