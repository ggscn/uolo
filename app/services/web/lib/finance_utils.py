import pandas as pd

def rsi(df,_window=14,_plot=0,_start=None,_end=None):
    """[RSI function]

    Args:
        df ([DataFrame]): [DataFrame with a column 'Close' for the close price]
        _window ([int]): [The lookback window.](default : {14})
        _plot ([int]): [1 if you want to see the plot](default : {0})
        _start ([Date]):[if _plot=1, start of plot](default : {None})
        _end ([Date]):[if _plot=1, end of plot](default : {None})
    """    

    ##### Diff for the différences between last close and now
    df['Diff'] = df['Close'].transform(lambda x: x.diff())
    ##### In 'Up', just keep the positive values
    df['Up'] = df['Diff']
    df.loc[(df['Up']<0), 'Up'] = 0
    ##### Diff for the différences between last close and now
    df['Down'] = df['Diff']
    ##### In 'Down', just keep the negative values
    df.loc[(df['Down']>0), 'Down'] = 0 
    df['Down'] = abs(df['Down'])

    ##### Moving average on Up & Down
    df['avg_up'+str(_window)] = df['Up'].transform(lambda x: x.rolling(window=_window).mean())
    df['avg_down'+str(_window)] = df['Down'].transform(lambda x: x.rolling(window=_window).mean())

    ##### RS is the ratio of the means of Up & Down
    df['RS_'+str(_window)] = df['avg_up'+str(_window)] / df['avg_down'+str(_window)]

    ##### RSI Calculation
    ##### 100 - (100/(1 + RS))
    df['RSI_'+str(_window)] = 100 - (100/(1+df['RS_'+str(_fast)]))

    ##### Drop useless columns
    df = df.drop(['Diff','Up','Down','avg_up'+str(_window),'avg_down'+str(_window),'RS_'+str(_window)],axis=1)

    ##### If asked, plot it!
    if _plot == 1:
        sns.set()
        fig = plt.figure(facecolor = 'white', figsize = (30,5))
        ax0 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4)
        ax0.plot(df[(df.index<=end)&(df.index>=start)&(df.Symbol==_ticker.replace('/',''))]['Close'])
        ax0.set_facecolor('ghostwhite')
        ax0.legend(['Close'],ncol=3, loc = 'upper left', fontsize = 15)
        plt.title(_ticker+" Close from "+str(start)+' to '+str(end), fontsize = 20)

        ax1 = plt.subplot2grid((6,4), (5,0), rowspan=1, colspan=4, sharex = ax0)
        ax1.plot(df[(df.index<=end)&(df.index>=start)&(df.Symbol==_ticker.replace('/',''))]['RSI_'+str(_window)], color = 'blue')
        ax1.legend(['RSI_'+str(_window)],ncol=3, loc = 'upper left', fontsize = 12)
        ax1.set_facecolor('silver')
        plt.subplots_adjust(left=.09, bottom=.09, right=1, top=.95, wspace=.20, hspace=0)
        plt.show()
    return(df)
