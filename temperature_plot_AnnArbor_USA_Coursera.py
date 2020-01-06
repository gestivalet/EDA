import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd
import numpy as np
from matplotlib.lines import Line2D

#### load the data
fname = 'data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv'
df = pd.read_csv(fname)


#### organize table
# organize value scales
df['Data_Value'] = df['Data_Value'] / 10

# organize dates
df['Date'] = pd.to_datetime(df['Date'])
df = df.assign(month=df['Date'].dt.month,
               day=df['Date'].dt.day)

month_names = ['a_Jan', 'b_Feb', 'c_Mar', 'd_Apr', 'e_May', 'f_Jun',
               'g_Jul', 'h_Aug', 'i_Sep', 'j_Oct', 'k_Nov', 'l_Dec']

month_map = {k:v for k,v in zip(range(1,13), month_names)}

df['month'] = df['month'].map(month_map)
df['day'] = df['day'].apply(lambda x: '0'+str(x) if x<10 else str(x))
df['period'] = df['month'] + '-' + df['day']

# split dfs
df_limits = df[df['Date'] <= '2014-12-31']
df_2015   = df[df['Date']  > '2014-12-31']


def clean_df(frame):
	"""
	Organizes dfs with necessary min and max temperatures with the index being the period (format=%b-%d).
	"""
    frame = frame.groupby('period')['Data_Value'].agg(['min', 'max']).sort_index().reset_index()
    frame['period'] = frame['period'].apply(lambda x: x[2:])
    frame = frame[frame.period != 'Feb-29'] # remove Feb-29
    return frame.set_index('period')
    

df2 = clean_df(df_limits)
df2['id'] = range(df2.shape[0]) # create period id
df_2015 = clean_df(df_2015)


# boundaries - months + auxiliar plot objects
df_limits = df_limits[df_limits.period != 'b_Feb-29']
aux = df_limits.groupby('month')['day'].agg(['min', 'max']).reset_index()
aux['lower'] = aux[['month', 'min']].apply(lambda pair: pair[0][2:]+'-'+pair[1], axis=1)
aux['upper'] = aux[['month', 'max']].apply(lambda pair: pair[0][2:]+'-'+pair[1], axis=1)
span_boundaries = aux[['lower', 'upper']].unstack().tolist()
ix_boundaries = df2['id'][df2.index.isin(span_boundaries)].tolist()
boundaries = [ix_boundaries[i * 2:(i + 1) * 2] for i in range((len(ix_boundaries) + 2 - 1) // 2 )][:-1]
colors = ['gray', 'white']*6


#### plot
fig, ax = plt.subplots(figsize=(22,5))

# label parameters
n = np.arange(365)
xlabels = [n[2:] for n in month_names]
posx = df2['id'][df2.index.str.contains('15')].tolist()
posy = list(range(-40, 41, 10))

# create vspans for months (alternating colors)
for b,c in zip(boundaries, colors):
    ax.axvspan(b[0], b[1], facecolor=c, alpha=0.1)

# plot min and max daily temperatures (2005-2014)
ax.plot(n, df2['min'], 'k-', linewidth=0.6)
ax.plot(n, df2['max'], 'k-', linewidth=0.6)

# shade area between lines
ax.fill_between(n, df2['min'], df2['max'], 
                facecolor='black', alpha=0.25)

# plot 2015 data if exceeds min OR max temperatures
for i,point in enumerate(zip(df2.iterrows(), df_2015.iterrows())):
    min_, min_2015 = point[0][1]['min'], point[1][1]['min']
    max_, max_2015 = point[0][1]['max'], point[1][1]['max']
    
    # plot min
    if min_2015 < min_:
        plt.scatter(n[i], min_2015, s=100, color='blue', label='min2015')

    # plot max    
    if max_2015 > max_:
        plt.scatter(n[i], max_2015, s=100, color='red')

        
# FORMATTING
# remove spines
for spine in ax.spines.values():
    spine.set_visible(False)


# add horizontal gridlines
[plt.axhline(py, color='gray', alpha=0.25) for py in posy]


# labels and ticks
tit="Variation of minimum and maximum temperatures between 2005 and 2015 - Ann Arbor, Michigan - USA"
plt.title(tit, fontsize=15, fontweight='bold')
plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='on', labelbottom='on')
plt.xticks(posx, xlabels, rotation=0, horizontalalignment='center', alpha=0.8, fontsize=12) 
plt.yticks(fontsize=14, alpha=0.8)
plt.ylabel('Temperature (Celsius)', alpha=0.8, fontsize=12)
#plt.xlabel('Period', alpha=0.8)

# legend
legend_elements = [Line2D([0], [0], color='k', label='Daily minimum & maximum temperatures for 2005-2014', alpha=0.8),
                   Line2D([0], [0], marker='o', color='w', label='days in 2015 that broke a record high for 2005-2014',
                          markerfacecolor='r', markersize=12),
                   Line2D([0], [0], marker='o', color='w', label='days in 2015 that broke a record low for 2005-2014',
                          markerfacecolor='b', markersize=12)]
ax.legend(handles=legend_elements, loc='lower center', frameon=False, fontsize=12)

plt.show()