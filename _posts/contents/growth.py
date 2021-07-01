import pandas as pd
import altair as alt
import numpy as np
alt.data_transformers.disable_max_rows()


population_data = pd.read_csv('data/population-by-country.csv')
population_data = population_data[population_data['Year'] >= 1990]
population_data['pop'] = population_data['Population by Country (Clio Infra (2016))']

# +
population_data['date'] = pd.DatetimeIndex(population_data['Year'].apply(lambda x: f'01-01-{x}'))

l = []
for country, dat in population_data.groupby('Entity'):
    row = dat.iloc[-1]
    row['Year'] = 2019
    row['date'] = pd.Timestamp('2019-01-01')
    dat = dat.append(row).reset_index()
    l.append(dat.set_index('date').resample('Y').ffill().reset_index())

population_data_resampled = pd.concat(l).reset_index()
population_data = population_data_resampled.set_index(['Entity', 'date'])
# -

data2 = pd.read_csv('data/production-vs-consumption-co2-emissions.csv')
data2['date'] = pd.DatetimeIndex(data2['Year'].apply(lambda x: f'01-01-{x}'))

l = []
for country, dat in data2.groupby('Entity'):
    try:
        dat['CO2 per capita'] = dat['Annual CO2 emissions'].values / population_data.loc[country]['pop'].values
        dat['consumption CO2 per capita'] = dat['Annual consumption-based CO2 emissions'].values / population_data.loc[country]['pop'].values
        l.append(dat)
    except:
        pass
data = pd.concat(l)

data_gdp = pd.read_csv('./data/gdp-per-capita-worldbank.csv')
data_gdp['date'] = pd.DatetimeIndex(data_gdp['Year'].apply(lambda x: f'01-01-{x}'))
data_gdp['gdp'] = data_gdp['GDP per capita, PPP (constant 2011 international $)']

data = data.drop(['Code', 'Year'], axis=1)
data_gdp = data_gdp.drop(['Code', 'Year'], axis=1)
data_combined = data.set_index(['Entity', 'date']).join(data_gdp.set_index(['Entity', 'date'])).reset_index()
data_combined.rename(columns={'Entity': 'Country'}, inplace=True)

countries = ['Germany', 'United States', 'China']
base = alt.Chart(data_combined[data_combined['Country'].isin(countries)])
emissions_base = base.encode(
   x='date:T',
   y=alt.Y('CO2 per capita', axis=alt.Axis(title='CO2 per capita')),
   color='Country')
gdp_base = base.mark_circle().encode(
   x='date:T',
   y='gdp:Q',
   color='Country')
emissions = emissions_base.mark_line()
gdp = gdp_base.mark_circle()
chart = alt.layer(emissions, gdp).resolve_scale(y='independent')

chart.save('imgs/decoupling.png')


