import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import datetime
import altair as alt

def run_app():
    geo_data = load_data('GeoData.csv')
    ops_data = load_data('KoreanWarOps.csv')
    ops_options = ['Pounds of Munitions Used', 'Bullets Used', 'Rockets Used', 'Enemy Aircraft Destroyed', 'Casualties',
                   'Aircraft Lost', 'Aircraft Damaged', 'Effective Aircraft on Mission']
    st.title('USAF Korean War Activity')
    st.header('Background')
    st.text('''
    The Korean War, sometimes referred to as 'The forgotten war', lasted from June 1950 to 
    July 1953. This war marked a major shift in US foreign policy as the US fought the spread
    of communism by containing the Soviet backed North Korea. During the war, the newly 
    founded United States Air Force (USAF) launched a series of bombing runs throughout the 
    Korean peninsula. Many of the unexploded ordinances are still somewhere along the DMZ.
    
    When the war started, the USAF employed a number of historians to record the events 
    of the war. Most of this data has been helpfully digitalized and made available for 
    public use by Lt Col Jenns Robertson and his team called THOR. Below you will find
    a few interactive tools to examine what went on during the Korean War for yourself
    based on the THOR dataset.
    ''')


    st.header('Korean War Bombings')
    st.text('Below are locations targeted by USAF bombers')
    hide_box = st.checkbox("Enable Date Filter")
    if hide_box:
        date_slider = st.slider("Date Filter",
                                    datetime.datetime(2051, 6, 1, 0, 0, 0),
                                    datetime.datetime(2052, 12, 30, 0, 0, 0),
                                    datetime.datetime(2051, 6, 2, 0, 0, 0),
                                    datetime.timedelta(1),
                                    format='MMM DD, YY')
    else:
        date_slider = None
    map = st.pydeck_chart(plot_map(geo_data, date_slider))
    st.header("Unit Activity")
    st.text('View individual statistics for USAF units that participated in the Korean war')
    unit_box = st.selectbox(label='Unit', options=['All Units'] + list(sorted(ops_data.fillna('NA').UNIT.unique())))
    acty_box = st.selectbox(label='Statistic', options=ops_options)
    chart1 = make_line(ops_data, unit_box, acty_box)
    chart2 = make_bar(ops_data, unit_box)
    st.text(acty_box + ' for ' + unit_box)
    st.altair_chart(chart1)
    st.text('Total Sorties for ' + unit_box)
    st.altair_chart(chart2)
    st.text('Made by Caleb Reigada ----- reigadacaleb@gmail.com')

@st.cache
def load_data(file):
    data = pd.read_csv(file)
    data['DATE'] = pd.to_datetime(data.DATE)
    return data

@st.cache
def df_finder(df, date):
    if date is None:
        return df.loc[:, ['lat', 'lon']]
    else:
        new_date = datetime.datetime(date.year-100, date.month, date.day, 0, 0, 0)
        return df[df.DATE == pd.to_datetime(new_date)].loc[:, ['lat', 'lon']]

def plot_map(data, date):
    view = pdk.ViewState(
        latitude=39,
        longitude=126,
        zoom=6,
        bearing=0,
        pitch=0
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_finder(data, date),
        pickable=True,
        get_radius=2000,
        auto_highlight=True,
        get_fill_color=[0, 0, 200, 160],
        get_position='[lon, lat]',
        tooltip=True
    )
    r = pdk.Deck(layers=[layer], initial_view_state=view, tooltip={'text': "Coords: {lat} {lon}"})
    return r

def make_line(df, unit, stat):
    df_map = {'Pounds of Munitions Used': 'TOTAL_MUNITIONS_LBS',
              'Bullets Used': 'BULLETS',
              'Rockets Used': 'ROCKETS',
              'Enemy Aircraft Destroyed': 'AC_DESTROYED',
              'Casualties': 'CASUALTIES',
              'Aircraft Lost': 'AC_LOST',
              'Aircraft Damaged': 'AC_DAMAGED',
              'Effective Aircraft on Mission': 'AC_EFFECTIVE'}
    if unit != 'All Units':
        df_data = df[df.UNIT == unit]
    else:
        df_data = df.copy()
    y = df_map[stat]
    df_data = df_data.fillna(0)
    c = alt.Chart(df_data).mark_line().encode(
    x='DATE',
    y=y,
    )
    return c

def make_bar(df, unit):
    if unit != 'All Units':
        count = df[df.UNIT == unit]
    else:
        count = df.copy()
    count['AC_TYPE'] = count['AC_TYPE'].fillna('N/A')
    count['AC_DISPATCHED'] = count['AC_DISPATCHED'].fillna(0)
    count = count.groupby('AC_TYPE').AC_DISPATCHED.sum()
    count = pd.DataFrame({
        'Aircraft': count.index.values,
        'Total Sorties': count.values
    })
    c = alt.Chart(count).mark_bar().encode(x='Aircraft', y='Total Sorties', tooltip=['Total Sorties'])
    return c

if __name__ == '__main__':
    run_app()


