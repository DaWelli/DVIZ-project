import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# -- Page config --
st.set_page_config(page_title='World development',
                   page_icon=':earth_africa:',
                   layout='wide')

# -- Here I remove the Streamlit header and footer --
st.markdown(
    """
    <style>
        footer {display: none}
        [data-testid="stHeader"] {display: None}
    </style>
    """, unsafe_allow_html=True
)

# -- Loading CSS --
with open('./style/styles.css') as f:
    css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


# -- Navbar --
def navbar():
    with st.sidebar:
        st.page_link('App.py', label='Home', icon='🏠')
        st.page_link('pages/Suicide.py', label='Suicide Data', icon='🌍')
        st.page_link('pages/About.py', label='About / Code', icon='❓')


navbar()

# --Title --
st.markdown('# :earth_africa: Suicide Data')
st.write("""
Here you can explore the suicide data around the world. Be mindful this is only the data from reported and proven
suicide cases, there are sadly alot more unreported cases.
""")
st.write('Please, seek professional help if you are in need: ',
         'https://en.wikipedia.org/wiki/List_of_suicide_crisis_lines')


# -- Cache data --
@st.cache_data(show_spinner=False)
def load_data(data):
    data = pd.read_csv(data)
    return data


# -- Load data --
df_pop = load_data('./csv_files/world_population_revisited.csv')
df_pop = df_pop.dropna(subset=['Continent'])

df_suicides = load_data('./csv_files/suicides.csv')

# -- I replace the counter for the suicides from 0 to 1 as it should have been --
df_suicides['SuicideCount'] = df_suicides['SuicideCount'].replace(0, 1)

# -- I replace 'Central and South America' with 'South America' for the choropleth map and for better division
df_suicides['RegionName'] = df_suicides['RegionName'].replace('Central and South America', 'South America')

# -- I replace 'North America and the Caribbean' with 'North America' for the choropleth map and for better division
df_suicides['RegionName'] = df_suicides['RegionName'].replace('North America and the Caribbean', 'North America')

df_continent = load_data('./csv_files/continents.csv')

# -- Setup tabs --

tab_selection = option_menu(
    menu_title='Please choose a main filter:',
    options=['Worldwide', 'Continents', 'Countries'],
    icons=['globe-americas', 'archive', 'airplane'],
    menu_icon='cast',
    default_index=0,
    orientation='horizontal',
    styles={
        'container': {'padding': '0!important', 'background-color': 'transparent'},
        'icon': {'color': 'white', 'font-size': '25px'},
        'nav-link': {
            'font-size': '25px',
            'text-align': 'center',
            'margin': '0',
            '--hover-color': 'orange'
        },
        'nav-link-selected': {'background-color': 'dodgerblue'}
    }
)


# st.dataframe(df_pop)
# st.dataframe(df_suicides)

# -- Population line chart --

def population_line_chart():
    df_melted = pd.melt(df_selection, id_vars=['Country', 'Continent'],
                        value_vars=['2022_Population', '2020_Population',
                                    '2015_Population', '2010_Population',
                                    '2000_Population', '1990_Population',
                                    '1980_Population', '1970_Population'],
                        var_name='Year', value_name='Population')

    df_melted['Year'] = df_melted['Year'].str.split('_').str[0]

    year_order = ['1970', '1980', '1990', '2000', '2010', '2015', '2020', '2022']

    fig = px.line(df_melted, x='Year', y='Population', color='Country',
                  labels={'Population': 'Population Count', 'Year': 'Year'},
                  category_orders={'Year': year_order},
                  title='👨‍👩‍👧‍👦 Population over the years')

    # -- Customizing chart appearance --
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(title='Country', title_font=dict(size=24)),
        xaxis=dict(showgrid=True, title_font=dict(size=24)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))

    st.plotly_chart(fig, use_container_width=True)


# -- Suicides per gender pie chart --
def suicides_by_gender(selected_countries, selected_generation):
    if selected_generation != 'All generations':
        suicide_by_gender = df_suicides[(df_suicides['CountryName'].isin(selected_countries)) &
                                        (df_suicides['Generation'] == selected_generation)].dropna().groupby(['Sex'])[
            'SuicideCount'].sum()
        chart_title = f" Total suicides by gender ({selected_generation})"
    else:
        suicide_by_gender = df_suicides[df_suicides['CountryName'].isin(selected_countries)].dropna().groupby(['Sex'])[
            'SuicideCount'].sum()
        chart_title = "Total suicides by gender (All generations)"

    labels = ['Female', 'Male']
    # -- Defining colors for the genders --
    colors = ['lightcoral', 'dodgerblue']

    fig = go.Figure(data=[go.Pie(labels=labels, values=suicide_by_gender,
                                 textinfo='label+percent', marker=dict(colors=colors))])

    # -- Customizing chart appearance --
    fig.update_layout(title='👦👧' + chart_title, showlegend=True)

    st.plotly_chart(fig, use_container_width=True)


# -- Suicide Line Chart
def suicides_chart():
    fig = px.line(suicides_filtered, x='Year', y='SuicideCount', color='CountryName',
                  labels={'SuicideCount': 'Number of Suicides', 'Year': 'Year', 'CountryName': 'Country'},
                  title=f'💀 {suicide_chart_title}, for {selected_generation}')

    # -- Customizing chart appearance --
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(title='Country', title_font=dict(size=24)),
        xaxis=dict(showgrid=True, title_font=dict(size=24), tickmode='linear', tick0=1970, dtick=1),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))
    st.plotly_chart(fig, use_container_width=True)


# -- Suicides per 100K people Bar Chart #1--
def suicides100K_gender():
    suicides100k_gender_data = df_suicides.groupby(['RegionName', 'Year', 'Sex'])[
        'DeathRatePer100K'].sum().reset_index()
    suicides100k_gender_data = suicides100k_gender_data[suicides100k_gender_data['Sex'] != 'Unknown']

    # -- Defining colors for the genders --
    colors = {'Male': 'dodgerblue', 'Female': 'lightcoral'}

    fig = px.bar(suicides100k_gender_data, x='RegionName', y='DeathRatePer100K', color='Sex',
                 barmode='group', color_discrete_map=colors,
                 labels={'DeathRatePer100K': 'Number of Suicides per 100K', 'RegionName': 'Continent'},
                 title='👦👧 Suicides by Continent and Gender over the years (1990 - 2022)',
                 animation_frame='Year', animation_group='RegionName')

    # -- Customizing chart appearance --
    fig.update_layout(
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(size=24)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))

    st.plotly_chart(fig, use_container_width=True)


# -- Suicides per 100K people Bar Chart #2--
def suicides100K_age():
    suicides100k_age_data = (df_suicides.groupby(['RegionName', 'Year', 'AgeGroup'])['DeathRatePer100K']
                             .sum().reset_index())
    suicides100k_age_data = suicides100k_age_data[suicides100k_age_data['AgeGroup'] != 'Unknown']

    # -- Defining colors for the genders --
    # https://matplotlib.org/stable/gallery/color/named_colors.html
    colors = {'0-14 years': 'dodgerblue',
              '15-24 years': 'orchid',
              '25-34 years': 'orange',
              '55-74 years': 'chocolate',
              '75+ years': 'maroon'}

    fig = px.bar(suicides100k_age_data, x='RegionName', y='DeathRatePer100K', color='AgeGroup',
                 barmode='group', color_discrete_map=colors,
                 labels={'DeathRatePer100K': 'Number of Suicides per 100K', 'RegionName': 'Continent'},
                 title='👶👱‍♀️👴 Suicides by Continent and the age group over the years (1990 - 2022)',
                 animation_frame='Year', animation_group='RegionName')

    # -- Customizing chart appearance --
    fig.update_layout(
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(size=24)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))

    st.plotly_chart(fig, use_container_width=True)


# -- Choropleth MAP for total counts --
def choropleth_100k():
    # -- Create dummy df for choropleth map --
    dummy_data = (df_suicides.groupby(['RegionName', 'Year'])['SuicideCount']
                  .sum().reset_index())
    dummy_data = dummy_data.sort_values(by=['RegionName', 'Year'])
    dummy_data['Total Suicides'] = dummy_data.groupby('RegionName')['SuicideCount'].cumsum()

    # -- Now I delete all the years except the latest year
    df_latest_year = dummy_data.groupby('RegionName').tail(1)

    # -- Now I merge both dfs, fill all NaN with 0, and remove obsolete columns
    choropleth_data = pd.merge(df_continent, df_latest_year, how='left', left_on='Continent', right_on='RegionName')
    choropleth_data['Total Suicides'] = choropleth_data['Total Suicides'].fillna(0)
    choropleth_data.drop(columns=['Year_x', 'RegionName', 'SuicideCount'], inplace=True)

    # st.dataframe(choropleth_data)
    fig = px.choropleth(choropleth_data, locations='Code', color='Total Suicides', hover_name='Continent',
                        projection='cylindrical stereographic',
                        title='Total number of suicides per continent (1990 - 2022)',
                        color_continuous_scale='jet')

    # -- Customizing chart appearance --
    fig.update_layout(autosize=False)

    st.plotly_chart(fig, use_container_width=True)


# -- GDP Line chart --
def gdp_line_chart():
    fig = px.line(suicides_filtered, x='Year', y='GDPPerCapita', color='CountryName',
                  labels={'GDPPerCapita': 'GDP per Capita', 'Year': 'Year', 'CountryName': 'Country'},
                  title=f'💵 GDP per Capita')

    # -- Customizing chart appearance --
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(title='Country', title_font=dict(size=24)),
        xaxis=dict(showgrid=True, title_font=dict(size=24), tickmode='linear', tick0=1970, dtick=1),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))
    st.plotly_chart(fig, use_container_width=True)


# -- GNI Line chart --
def gni_line_chart():
    fig = px.line(suicides_filtered, x='Year', y='GrossNationalIncome', color='CountryName',
                  labels={'GrossNationalIncome': 'Gross National income', 'Year': 'Year', 'CountryName': 'Country'},
                  title=f'💰 Gross National Income')

    # -- Customizing chart appearance --
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(title='Country', title_font=dict(size=24)),
        xaxis=dict(showgrid=True, title_font=dict(size=24), tickmode='linear', tick0=1970, dtick=1),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))
    st.plotly_chart(fig, use_container_width=True)


# -- Country Trivia --
def trivia(selected_country):
    country_data = df_selection[df_selection['Country'] == selected_country]
    if not country_data.empty:
        population_density = country_data['2022_Population'] / country_data['Area']
        st.write(f'{selected_country}\'s population Density is: {population_density.values[0]:,.2f} people per km$^2$')

        st.write(f'The countries total area is: {country_data["Area"].values[0]:,.0f} km$^2$')

        growth_rate = ((country_data['2022_Population'] - country_data['1970_Population']) / country_data[
            '1970_Population']) * 100
        st.write(f'Growth rate over the years: {growth_rate.values[0]:,.2f}%')

        capital = country_data['Capital'].values[0]
        st.write(f'Capital of {selected_country} is: {capital}')


# -- Today's population percentage chart--
def population_percentage():
    total_population_selected_countries = df_selection['2022_Population'].sum()
    total_population_world = df_pop['2022_Population'].sum()

    population_percentage = (total_population_selected_countries / total_population_world) * 100

    rest_of_world_percentage = 100 - population_percentage

    colors = ['#E41E3F', '#0040C9']

    fig = go.Figure(data=[go.Pie(labels=['Selected Countries', 'Rest of the World'],
                                 values=[population_percentage, rest_of_world_percentage],
                                 pull=[0.01, 0.1],
                                 marker=dict(colors=colors))])
    fig.update_layout(title='📈 Population Percentage Compared to the Rest of the World')

    st.plotly_chart(fig, use_container_width=True)


# -- Worldwide suicide by gender line chart (with years) --
def world_line_gender_chart():
    suicides100k_world_gender_data = df_suicides.groupby(['Year', 'Sex'])[
        'DeathRatePer100K'].sum().reset_index()
    suicides100k_world_gender_data = suicides100k_world_gender_data[suicides100k_world_gender_data['Sex'] != 'Unknown']

    # -- Defining colors for the genders --
    colors = {'Male': 'dodgerblue', 'Female': 'lightcoral'}

    fig = px.line(suicides100k_world_gender_data, x='Year', y='DeathRatePer100K', color='Sex',
                  color_discrete_map=colors,
                  labels={'DeathRatePer100K': 'Number of Suicides per 100K', 'Year': 'Year'},
                  title='👦👧 Suicides worldwide by Gender over the years (1990 - 2022)')

    # -- Customizing chart appearance --
    fig.update_layout(
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(size=24)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))

    st.plotly_chart(fig, use_container_width=True)


# -- Worldwide suicide line chart (with years) --
def world_line_chart():
    suicides100k_world_data = df_suicides.groupby(['Year'])[
        'DeathRatePer100K'].sum().reset_index()

    fig = px.line(suicides100k_world_data, x='Year', y='DeathRatePer100K',
                  labels={'DeathRatePer100K': 'Number of Suicides per 100K', 'Year': 'Year'},
                  title='💀 Suicides worldwide over the years (1990 - 2022)')

    # -- Customizing chart appearance --
    fig.update_layout(
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(size=24)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))

    st.plotly_chart(fig, use_container_width=True)


# -- Worldwide suicide by age line chart (with years) --
def world_line_age_chart():
    suicides100k_world_age_data = (df_suicides.groupby(['Year', 'AgeGroup'])['DeathRatePer100K']
                                   .sum().reset_index())
    suicides100k_world_age_data = suicides100k_world_age_data[suicides100k_world_age_data['AgeGroup'] != 'Unknown']

    # -- Defining colors for the genders --
    # https://matplotlib.org/stable/gallery/color/named_colors.html
    colors = {'0-14 years': 'dodgerblue',
              '15-24 years': 'orchid',
              '25-34 years': 'orange',
              '55-74 years': 'chocolate',
              '75+ years': 'maroon'}

    fig = px.line(suicides100k_world_age_data, x='Year', y='DeathRatePer100K', color='AgeGroup',
                  color_discrete_map=colors,
                  labels={'DeathRatePer100K': 'Number of Suicides per 100K', 'RegionName': 'Continent'},
                  title='👶👱‍♀️👴 Suicides worldwide by age group over the years (1990 - 2022)')

    # -- Customizing chart appearance --
    fig.update_layout(
        width=1200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title_font=dict(size=24)),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='#dddddd', title_font=dict(size=24)))

    st.plotly_chart(fig, use_container_width=True)


# -- Population of the world treemap --
def treemap():
    selected_filter = st.selectbox('Select data',
                                   ['Area', 'Population Density', 'Growth Rate', 'Population'])

    filter_to_column = {
        'Area': 'Area',
        'Population Density': 'Density',
        'Growth Rate': 'Growth Rate',
        'Population': '2022_Population'
    }

    selected_column = filter_to_column.get(selected_filter, '2022_Population')

    treemap_continent = df_pop['Continent']
    treemap_country = df_pop['Country']
    treemap_population = df_pop['2022_Population']
    treemap_area = df_pop['Area']
    treemap_density = df_pop['Density']
    treemap_growth_rate = df_pop['Growth_Rate']
    treemap_percentage = df_pop['World_Population Percentage']

    if selected_column == '2022_Population':
        treemap_values = treemap_population
        hover_data = {
            'Country': treemap_country,
            'Population': treemap_values,
            'Percentage': treemap_percentage
        }
        hover_template = ('<b>Continent:</b> %{label}<br>' +
                          '<b>Country:</b> %{customdata[0]}<br>' +
                          '<b>Population:</b> %{customdata[1]}<br>' +
                          '<b>World Population Percentage:</b> %{customdata[2]:.2f}%<extra></extra>')
    elif selected_column == 'Area':
        treemap_values = treemap_area
        hover_data = {
            'Country': treemap_country,
            'Area': treemap_values
        }
        hover_template = ('<b>Continent:</b> %{label}<br>' +
                          '<b>Country:</b> %{customdata[0]}<br>' +
                          '<b>Area:</b> %{customdata[1]:,.2f} km²<extra></extra>')
    elif selected_column == 'Density':
        treemap_values = treemap_density
        hover_data = {
            'Country': treemap_country,
            'Density': treemap_values
        }
        hover_template = ('<b>Continent:</b> %{label}<br>' +
                          '<b>Country:</b> %{customdata[0]}<br>' +
                          '<b>Population Density:</b> %{customdata[1]:,.2f} per km²<extra></extra>')
    else:
        treemap_values = treemap_growth_rate
        hover_data = {
            'Country': treemap_country,
            'Growth Rate': treemap_values
        }
        hover_template = ('<b>Continent:</b> %{label}<br>' +
                          '<b>Country:</b> %{customdata[0]}<br>' +
                          '<b>Growth Rate:</b> %{customdata[1]:.2f}%<extra></extra>')

    # -- Title --
    if selected_filter == 'Population':
        title_text = '🌳 2022 Population of the entire world'
    else:
        title_text = f'🌳 {selected_filter} of the entire world'

    fig = px.treemap(df_pop,
                     path=[px.Constant('Continent'), 'Continent', 'Country'],
                     values=treemap_values,
                     color=treemap_values,
                     title=title_text,
                     hover_data=[],
                     color_continuous_scale='jet'
                     )

    fig.update_layout(
        title_font_size=34,
        height=1000,
        width=1600,
        coloraxis_colorbar=dict(title=selected_filter),
    )

    fig.update_traces(
        hovertemplate=hover_template,
        customdata=list(zip(*hover_data.values()))
    )

    st.plotly_chart(fig, use_container_width=True)


if tab_selection == 'Worldwide':
    st.title('Worldwide')
    st.markdown('#### This is the world tab, here you can analyze the global suicide statistics.')
    # -- Setup columns
    col1, col2 = st.columns(2)
    with col1:
        world_line_chart()
        world_line_age_chart()
    with col2:
        world_line_gender_chart()
    treemap()

if tab_selection == 'Continents':
    st.title('Continents')
    st.markdown('#### This is the continent tab, here you can analyze an the continents.')
    # -- Setup columns
    col1, col2 = st.columns(2)
    with col1:
        suicides100K_gender()
        suicides100K_age()
    with col2:
        choropleth_100k()

if tab_selection == 'Countries':
    st.title('Countries')
    st.markdown('#### This is the country tab, here you can analyze an individual country or compare multiple '
                'countries.')
    # -- Filters (Continent, Country) --
    st.write('Please select a continent first, you can choose multiple for each filter, expect gender and generations.')
    continent = st.multiselect(
        'Select continent',
        df_pop['Continent'].unique()
    )

    filtered_countries = df_pop[df_pop['Continent'].isin(continent)]['Country'].unique().tolist()
    country = st.multiselect(
        'Select country',
        filtered_countries
    )

    df_selection = df_pop.query(
        'Country == @country & Continent == @continent')

    # -- Filters (Gender, Generation) --
    selected_sex = st.selectbox('Select the gender', ['Both', 'Male', 'Female', 'Unknown'])
    generation_options = ['All generations'] + list(df_suicides['Generation'].unique())
    selected_generation = st.selectbox('Select generation', generation_options)

    # -- Gender Logic --
    if selected_sex == 'Both':
        suicides_filtered = df_suicides[df_suicides['CountryName'].isin(country)]
        suicide_chart_title = 'Suicides for both genders'
    elif selected_sex == 'Male':
        suicides_filtered = df_suicides[(df_suicides['CountryName'].isin(country)) & (df_suicides['Sex'] == 'Male')]
        suicide_chart_title = 'Suicides for males'
    elif selected_sex == 'Female':
        suicides_filtered = df_suicides[(df_suicides['CountryName'].isin(country)) & (df_suicides['Sex'] == 'Female')]
        suicide_chart_title = 'Suicides for females'
    else:
        suicides_filtered = df_suicides[(df_suicides['CountryName'].isin(country)) & (df_suicides['Sex'] == 'Unknown')]
        suicide_chart_title = 'Suicides for unknown gender'

    # -- Generation Logic --
    if selected_generation != 'All generations':
        suicides_filtered = suicides_filtered[suicides_filtered['Generation'] == selected_generation]

    # -- Aggregating by Year --
    suicides_filtered = suicides_filtered.groupby(['CountryName', 'Year']).agg({
        'SuicideCount': 'sum',
        'CauseSpecificDeathPercentage': 'max',
        'DeathRatePer100K': 'max',
        'Population': 'max',
        'GDP': 'max',
        'GDPPerCapita': 'max',
        'GrossNationalIncome': 'max',
        'GNIPerCapita': 'max',
        'InflationRate': 'max',
        'EmploymentPopulationRatio': 'max'
    }).reset_index()

    # -- Setup columns
    col1, col2, col3 = st.columns(3)
    with col1:
        population_line_chart()
        suicides_chart()
    with col2:
        gdp_line_chart()
        gni_line_chart()
        population_percentage()
    with col3:
        suicides_by_gender(country, selected_generation)
        if len(country) == 1:
            for selected_country in country:
                st.subheader(f':bulb: Trivia about {selected_country}:')
                trivia(selected_country)
        elif len(country) == 2:
            for selected_country in country:
                st.subheader(f':bulb: Trivia about {selected_country}:')
                trivia(selected_country)
        else:
            st.subheader('Top 3 countries selected for trivia (based on 2022 population):')
            top_countries = df_selection.nlargest(3, '2022_Population')
            for index, row in top_countries.iterrows():
                st.subheader(f':bulb: Trivia about {row["Country"]}:')
                trivia(row['Country'])
