#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pickle
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import ipython_memory_usage
#get_ipython().run_line_magic('ipython_memory_usage_start', '')


print(f"Pandas: {pd.__version__}")
print(f"NumPy: {np.__version__}")

# In[2]:


#get_ipython().run_line_magic('load_ext', 'watermark')
#get_ipython().run_line_magic('watermark', '-i -v -m -p pandas,numpy,matplotlib -g -b')


# In[3]:

NROWS = 10_000_000
NBR_LOOPS = 100

#NROWS = 1_000_000
#NBR_LOOPS = 3 
#NROWS = 100_000_000
#NBR_LOOPS = 3
MATH_FN = 'mean'
#MATH_FN = 'std'
#MATH_FN = 'max'
timings_filename = "timings.png"
results_filename = "timings.pickle"

# 'longdouble' is 16 (or so) bytes, the timings seem to be quite varied, I'm not sure measuring
# it is useful - aka float128 and others
dtypes = ['int64', 'int32', 'int16', 'int8', 'uint8', 'float64', 'float32', 'float16']
#cols = {}
#for dtyp in dtypes:
    # makes random data using normal distribution, then cast
    # to various dtypes (which will involve rounding)
#    arr = np.random.normal(size=NROWS).astype(dtyp)
#    cols[dtyp] = arr
#df_data = pd.DataFrame(cols)
#df_data.head(5)


# In[4]:


#df_data.info()


# In[5]:

bytes_used = {}

if 'df_results' not in dir():
    cols = []
    #for col in df_data.columns:
    for col in dtypes:
        #arr = df_data[col]
        arr = pd.Series(np.random.normal(size=NROWS, loc=1).astype(col))
        print(f"Working on {col}, values start: {arr.values[:3]}")
        for fn_idx in range(2):
            if fn_idx == 0:
                fn_name = "ser"
                fn = getattr(arr, MATH_FN)
            else:
                fn = getattr(getattr(arr, 'values'), MATH_FN)
                fn_name = "ser.values"
            for n in range(NBR_LOOPS):
                t1 = time.time()
                fn()
                #timings[n] = time.time() - t1
                delta = time.time() - t1
                bytes_used[col] = arr.memory_usage()
                cols.append({'fn_name': fn_name, 'col': col, 't': delta})
    df_results = pd.DataFrame(cols)
    df_results.sample(5)


# In[ ]:


df_results.info()


gpby = df_results.groupby(['fn_name', 'col'])
#central_measure = gpby.median().unstack(0)
central_measure = gpby.mean().unstack(0)
central_measure = central_measure.loc[dtypes]
central_measure

stds = gpby.std().unstack(0)
stds = stds.loc[dtypes]
se = stds / np.sqrt(NBR_LOOPS)
se_95pc = se * 1.96
se_95pc

fig, ax = plt.subplots(figsize=(8, 6))
central_measure.plot(kind='bar', ax=ax, yerr=se_95pc)

title = f"Fn '{MATH_FN}' execution time on {NROWS:,} rows of normal rnd over {NBR_LOOPS:,} loops"
title += f"\nBlack bars are the 95% Confidence Interval. Central measure is: mean"
title += "\nUsing Pandas Series and Series.values"
ax.set_title(title);
ax.set_ylabel('Seconds (smaller is better)');

locs, labels = plt.yticks()
y_ticks = []
new_yticks=[f"{d:0.3f}s" for d in locs]
plt.yticks(locs,new_yticks); #, rotation=45, horizontalalignment='right')

locs, labels = plt.xticks()
new_xticks = [f"{l.get_text()} (≈{int(bytes_used[l.get_text()]/100_000):,} MB)" for l in labels]
#{bytes_used[s]}
plt.xticks(locs, new_xticks); #, rotation=45, horizontalalignment='right')
ax.set_xlabel('dtype');

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x')

ax.get_figure().tight_layout()
ax.grid()

ax.get_figure().savefig(timings_filename)
#plt.show()

if False:
    with open(results_filename, "wb") as f:
        pickle.dump(df_results, f)
