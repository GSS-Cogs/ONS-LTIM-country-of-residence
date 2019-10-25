#!/usr/bin/env python
# coding: utf-8

# Long-term international migration 2.02, last or next resident, UK and England and Wales

# In[35]:


from gssutils import *
scraper = Scraper('https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/'                   'internationalmigration/datasets/longterminternationalmigrationcountryoflastornextresidencetable202')
scraper


# In[36]:


tab = next(t for t in scraper.distributions[0].as_databaker() if t.name == 'Table 2.02')


# In[37]:


cell = tab.filter('Year')
cell.assert_one()


# In[38]:


observations = cell.shift(RIGHT).fill(DOWN).filter('Estimate').expand(RIGHT).filter('Estimate')                 .fill(DOWN).is_not_blank().is_not_whitespace() 
Str =  tab.filter(contains_string('Significant Change?')).fill(RIGHT).is_not_number()
observations = observations - (tab.excel_ref('A1').expand(DOWN).expand(RIGHT).filter(contains_string('Significant Change')))
original_estimates = tab.filter(contains_string('Original Estimates')).fill(DOWN).is_number()
observations = observations - original_estimates - Str

removal1 = tab.filter(contains_string('Original Estimates1'))
removal2 = tab.filter(contains_string('2011 Census Revisions1'))
Residence = cell.fill(RIGHT).is_not_blank().is_not_whitespace()  |             cell.shift(0,1).fill(RIGHT).is_not_blank().is_not_whitespace() |             cell.shift(0,2).expand(RIGHT).is_not_blank().is_not_whitespace().is_not_bold()             .filter(lambda x: type(x.value) != 'All' not in x.value) - removal1 - removal2


# In[39]:


CI = observations.shift(RIGHT)


# In[40]:


Year = cell.fill(DOWN) 
Year = Year.filter(lambda x: type(x.value) != str or 'Significant Change?' not in x.value)


# In[41]:


Geography = cell.fill(DOWN).one_of(['United Kingdom', 'England and Wales'])
Flow = cell.fill(DOWN).one_of(['Inflow', 'Outflow', 'Balance'])


# In[42]:


csObs = ConversionSegment(observations, [
    HDim(Year,'Year', DIRECTLY, LEFT),
    HDim(Geography,'Geography', CLOSEST, ABOVE),
    HDim(Residence, 'Country of Residence', DIRECTLY, ABOVE),
    HDim(Flow, 'Flow', CLOSEST, ABOVE),
    HDimConst('Measure Type', 'Count'),
    HDimConst('Unit','People (thousands)'),
    HDim(CI,'CI',DIRECTLY,RIGHT),
    HDimConst('Revision', '2011 Census Revision')
])
#savepreviewhtml(csObs)
savepreviewhtml(csObs, fname="Preview.html")

tidy_revised = csObs.topandas()


# In[43]:


csRevs = ConversionSegment(original_estimates, [
    HDim(Year, 'Year', DIRECTLY, LEFT),
    HDim(Geography,'Geography', CLOSEST, ABOVE),
    HDim(Residence, 'Country of Residence', DIRECTLY, ABOVE),
    HDim(Flow, 'Flow', CLOSEST, ABOVE),
    HDimConst('Measure Type', 'Count'),
    HDimConst('Unit','People (thousands)'),
    HDim(original_estimates.shift(RIGHT), 'CI', DIRECTLY, RIGHT),
    HDimConst('Revision', 'Original Estimate')
])
orig_estimates = csRevs.topandas()


# In[44]:


tidy = pd.concat([tidy_revised, orig_estimates], axis=0, join='outer', ignore_index=True, sort=False)


# In[45]:


import numpy as np
tidy['OBS'].replace('', np.nan, inplace=True)
tidy.dropna(subset=['OBS'], inplace=True)
if 'DATAMARKER' in tidy.columns:
    tidy.drop(columns=['DATAMARKER'], inplace=True)
tidy.rename(columns={'OBS': 'Value'}, inplace=True)
tidy['Value'] = tidy['Value'].astype(int)
tidy['CI'] = tidy['CI'].map(lambda x:'' if x == ':' else int(x[:-2]) if x.endswith('.0') else 'ERR')


# In[46]:


for col in tidy.columns:
    if col not in ['Value', 'Year', 'CI']:
        tidy[col] = tidy[col].astype('category')
        display(col)
        display(tidy[col].cat.categories)


# In[47]:


tidy['Geography'] = tidy['Geography'].cat.rename_categories({
    'United Kingdom': 'K02000001',
    'England and Wales': 'K04000001'
})
tidy['Country of Residence'] = tidy['Country of Residence'].cat.rename_categories({
    'All3' : 'non-eu',
    'Central and South America' : 'central-and-south-america', 
    'East Asia' : 'east-asia', 
    'European Union EU15' : 'eu15',
    'European Union EU2' : 'eu2', 
    'European Union EU8' : 'eu8', 
    'European Union Other' : 'eu-other',
    'European Union2' : 'eu' , 
    'Middle East and Central Asia' : 'middle-east-and-central-asia' ,
    'North Africa' : 'north-africa', 
    'North America' : 'north-america', 
    'Oceania' : 'oceania',
    'Other Europe3' : 'europe-exc-eu', 
    'Rest of the World' : 'rest-of-world', 
    'South Asia' : 'south-asia', 
    'South East Asia' :'south-east-asia',
    'Sub-Saharan Africa' : 'sub-saharan-africa',
    'All countries' : 'all',
    'Asia'  : 'asia'
            
})
tidy['Flow'] = tidy['Flow'].cat.rename_categories({
    'Balance': 'balance', 
    'Inflow': 'inflow',
    'Outflow': 'outflow'
})

tidy = tidy[['Geography', 'Year', 'Country of Residence', 'Flow',
              'Measure Type','Value', 'CI','Unit', 'Revision']]


# In[48]:


tidy['Year'] = tidy['Year'].apply(lambda x: pd.to_numeric(x, downcast='integer'))


# In[49]:


tidy['Year'] = tidy['Year'].astype(int)


# In[50]:


tidy


# In[51]:


from pathlib import Path
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

tidy.to_csv(destinationFolder / ('observations.csv'), index = False)


# In[52]:


from gssutils.metadata import THEME

scraper.dataset.family = 'migration'
scraper.dataset.theme = THEME['population']
scraper.dataset.license = 'http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/'

with open(destinationFolder / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
    
csvw = CSVWMetadata('https://gss-cogs.github.io/ref_migration/')
csvw.create(destinationFolder / 'observations.csv', destinationFolder / 'observations.csv-schema.json')


# In[ ]:




