import mplfinance as mpf


def get_style(background_colour, line_colour, text_colour):
    market_colours = mpf.make_marketcolors(up="g", down="r",
                                           edge=background_colour,
                                           wick=line_colour)

    style_dict = {"xtick.color": line_colour,
                  "ytick.color": line_colour,
                  "xtick.labelcolor": text_colour,
                  "ytick.labelcolor": text_colour,
                  "axes.spines.top": False,
                  "axes.spines.right": False,
                  "axes.labelcolor": text_colour,
                  "axes.labelsize": 18}

    style = mpf.make_mpf_style(marketcolors=market_colours,
                               facecolor=background_colour,
                               edgecolor=line_colour,
                               figcolor=background_colour,
                               gridcolor=line_colour,
                               gridstyle="--",
                               rc=style_dict)
    return style
