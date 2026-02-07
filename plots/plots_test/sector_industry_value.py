#!/usr/bin/env python
# coding: utf-8
import market_data as md
import performance as pf
import apis
import pandas as pd
from pymongo import MongoClient

client = MongoClient()
db = client[md.db_client]
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# In[26]:


collection = db[md.db_fidel_pos]
unique_dates = sorted(collection.distinct("Date"), reverse=True)
unique_dates[0:5]

# In[27]:


directory = 'Holding'
symbols = md.get_symbols_directory_and_port(directory=directory)
# symbols[0:10]


# In[28]:


target_date = unique_dates[0]
query = {
    "Date": target_date,
    "Symbol": {"$in": symbols}
}
# Fetch the records
collection = db[md.db_fidel_pos]
filtered_records = collection.find(query)

df = md.mdb_to_df(filtered_records)
df = df[['Date', 'Symbol', 'Current Value']]
df[0:5]


# In[29]:


def df_fidelity_current_value(symbols, a_date):
    collection = db[md.db_fidel_pos]
    query = {
        "Date": a_date,
        "Symbol": {"$in": symbols}
    }
    mdb_data = collection.find(query)
    df = md.mdb_to_df(mdb_data)
    df = df[['Date', 'Symbol', 'Current Value']]
    return df


df_current_value = df_fidelity_current_value(symbols, target_date)
df_current_value.head(5)


# In[30]:


def df_symbols_sectors_industries(symbols):
    fields = ['sectorname', 'primaryname', 'symbol']
    df_sector_ind = apis.df_symbol_profile(symbols, fields)
    df_sector_ind.dropna(inplace=True)
    df_sector_ind.rename(columns={'symbol': 'Symbol', 'sectorname': 'Sector', 'primaryname': 'Industry'}, inplace=True)
    return df_sector_ind


df_sector_ind = df_symbols_sectors_industries(symbols)
df_sector_ind.sort_values(by=['Sector']).head(5)


# In[31]:


def df_sector_ind_sym_current_value(symbols, df_current_value, df_sector_ind):
    df_sector_current_value = df_sector_ind.merge(df_current_value, on=['Symbol'], how='outer')
    return df_sector_current_value.sort_values(by=['Sector', 'Symbol'])


df_sector_ind_sym_val = df_sector_ind_sym_current_value(symbols, df_current_value, df_sector_ind)
df_sector_ind_sym_val.tail(5)

# In[32]:


df_sector_val = df_sector_ind_sym_val[['Sector', 'Current Value']]
df_sector_val.sort_values(by=['Sector']).head(5)

# In[33]:


df_sector_val = df_sector_val.groupby(['Sector'])['Current Value'].sum()
df_sector_val  # .tail(10)

# In[34]:


# Plotting the pie chart
plt.pie(df_sector_val, labels=df_sector_val.index, autopct='%1.1f%%', startangle=140)

# Adding a title
plt.title('Current Value Distribution by Sector')

# Ensuring the pie is drawn as a circle
plt.axis('equal')

# Display the plot
plt.tight_layout()
plt.savefig('sector_pie_chart.png')
plt.show()


# In[38]:


def get_sector_symbols(sector, symbols) -> list:
    coll_name = md.db_symbol_profile
    collection = db[coll_name]

    # Query for the specific sector and filter by the provided symbol list
    query = {
        "sectorname": sector,
        "symbol": {"$in": symbols}
    }
    return collection.distinct("symbol", query)


sector = 'Bond'
sector_symbols = get_sector_symbols(sector, symbols)
sector_symbols

# In[39]:


a_sector = 'Information Technology'
df_industry_value_for_sector = df_sector_ind_sym_val[df_sector_ind_sym_val['Sector'] == a_sector][
    ['Industry', 'Current Value']]
df_industry_value_for_sector
df_industry_value_for_sector = df_industry_value_for_sector.groupby(['Industry'])['Current Value'].sum()

# In[40]:


# Plotting the pie chart
plt.pie(df_industry_value_for_sector, labels=df_industry_value_for_sector.index, autopct='%1.1f%%', startangle=140)

# Adding a title
plt.title('Current Value Distribution by Industry')

# Ensuring the pie is drawn as a circle
plt.axis('equal')

# Display the plot
plt.tight_layout()
plt.savefig('industry_pie_chart.png')
plt.show()


