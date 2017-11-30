import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

fields1 = ['id', 'topicid']
fields2 = ['id', 'year']

file_name = 'docsTopTopic.csv'
docTopics = pd.read_csv(file_name, na_values=[''], keep_default_na=False, usecols=fields1)
df_topics = pd.DataFrame(docTopics, columns= fields1)

file_name = 'data/papers.csv'
docYears = pd.read_csv(file_name,usecols=fields2)
df_years = pd.DataFrame(docYears, columns=fields2)

result = pd.merge(df_topics, df_years, on='id')

topic_by_year=result.groupby(['year', 'topicid']).count() #groupBy
year_count = result.groupby('year').count() #dataframe
# bla = year_count['id']
# print(bla.keys())
# print(year_count['id'])

l=[]
for key in topic_by_year['id'].keys():
    l.append([key[0], key[1], topic_by_year['id'][key]/year_count['id'][key[0]]])
print(l)

data = pd.DataFrame(l, columns=['year','topic', 'part'])
print(data)


fig, ax = plt.subplots()
labels = []
for key, grp in data.groupby(['topic']):
    # if not key == 7:
    ax = grp.plot(ax=ax, kind='line', x='year', y='part')
    labels.append(key+1)
lines, _ = ax.get_legend_handles_labels()
ax.legend(lines, labels, loc='upperright')
plt.show()


# i = 0
# for key, grp in data.groupby(['topic']):
#     grp.plot(kind='line', x='year', y='part')
#     i=i+1
#     plt.figure(i)
#
# plt.show()

# plt.figure()
# data.plot(x='year', y='part', kind='line')
# plt.show()