import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import re
from PIL import Image
from RaceRefScrape import *
from plotly.subplots import make_subplots

st.set_page_config(layout='wide')

header = st.container()
model = st.container()
boxdata = st.container()
topdata = st.container()
dataset = st.container()

# import nascar image for header
image = Image.open("ncs_img.png")

#order is set at top...
with header:
    st.title("Nascar Cup Series Driver Overview")
    # st.image(image)

with model:
    sel_col, disp_col = st.columns(2)
    driver_select = sel_col.selectbox('Select Driver',options=get_active_drivers_rr("https://www.racing-reference.info/active-drivers/"))

    # data load section
    current_driver_url = get_driver_page_rr(driver_select)
    driver_data = get_driver_cup_table_rr(current_driver_url)
    driver_age = get_driver_age(current_driver_url)
    driver_years = re.findall(r'\d+',get_driver_years_cup(driver_data))
    driver_champ_count = get_driver_champs(driver_data)
    driver_top_count = get_driver_tfive_count(driver_data)
    driver_tten_count = get_driver_tten_count(driver_data)
    driver_pole_count = get_driver_pole_count(driver_data)
    driver_wins = get_driver_win_count(driver_data)
    driver_races = int(get_driver_total_race_count(driver_data))
    driver_team = get_driver_team(get_driver_page_espn(driver_select))
    years_in_list = get_years_in_list(int(driver_years[0]))

    df_espn = get_list_of_df_espn(years_in_list,get_espn_url_code(get_driver_page_espn(driver_select)))
    #combine last 3 year data and clean
    df_all = clean_and_combine_df(df_espn,years_in_list)

with boxdata:
    st.header("Driver Info")
    b1,b2,b3,b4 = st.columns((1,1,1,1))

    b1.metric("Age",driver_age)
    b2.metric("Years in Cup", driver_years[0])
    b3.metric("Championships",driver_champ_count)
    b4.metric("Current Team",driver_team)

with topdata:
    st.header("Driver Stats")
    st.subheader('Career Highlights')
    c1,c2,c3,c4 = st.columns((1,1,1,1))

    layout = go.Layout(margin=go.layout.Margin(
        l=0,
        r=0,
        b=0,
        t=0,
    ))

    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=driver_wins,
        gauge={'shape':'angular',
               'axis' : {'range':[None,driver_races]},
               },
        title={'text':"Wins"}
    ))

    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=driver_pole_count,
        gauge={'shape':'angular',
               'axis' : {'range':[None,driver_races]},
               },
        title={'text':"Poles"}
    ))

    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=driver_top_count,
        gauge={'shape':'angular',
               'axis' : {'range':[None,driver_races]},
               },
        title={'text':"Top 5's"}
    ))

    fig4 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=driver_tten_count,
        gauge={'shape':'angular',
               'axis' : {'range':[None,driver_races]},
               },
        title={'text':"Top 10's"}
    ))

    c1.plotly_chart(fig1,use_container_width=True,layout=layout)
    c2.plotly_chart(fig2,use_container_width=True,layout=layout)
    c3.plotly_chart(fig3,use_container_width=True,layout=layout)
    c4.plotly_chart(fig4,use_container_width=True,layout=layout)

with dataset:
    st.header("Driver Data")
    
    #Overview of finish position vs track
    st.subheader('Track Performance')
    fig = px.box(df_all,y='PLACE',x='RACE')
    st.plotly_chart(fig,use_container_width=True)

    #line plot of rank vs year
    df_rr = driver_data.dropna(axis=0)
    st.subheader('Driver Rank by Year')
    fig1 = px.line(df_rr,y='Rank',x='Year',markers=True)
    st.plotly_chart(fig1,use_container_width=True)

    #line plot of avg start and fin by year
    st.subheader('Driver Average Start & Avgerage Finish by Year')
    fig2 = px.line(df_rr,x='Year',y=df_rr.columns[11:13])
    st.plotly_chart(fig2,use_container_width=True)

    #Bar chart of percent of laps lead
    st.subheader('Driver % Laps Lead by Year')
    df_rr = get_perct_led(df_rr)
    fig3 = px.bar(df_rr,x='Year',y='per')
    st.plotly_chart(fig3,use_container_width=True)

    #Overview of finish position & start
    st.subheader('Overview of Start and Finish Position')
    fig4 = px.violin(df_all,y=df_all.columns[2:4],color='DATE')
    st.plotly_chart(fig4,use_container_width=True)

    #st.write(df_all.head(5))