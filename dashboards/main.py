
# from flask import session
import os
import altair as alt
import streamlit as st
from vega_datasets import data
import pandas as pd
import numpy as np
from pathlib import Path

# from _first_azure.config.settings import config

# from webapp.app import session

def msg(msg):
    from flask import current_app
    from webapp.app import session
    # print(session)
    with current_app.app_context():
        pass

# msg('test')

st.title("AIxPact Dashboard Main")
# st.markdown(session.get("info", 'no session info'))

name = st.text_input("What's your name?", '')
st.write(name)

# st.write(os.getcwd())
path = Path('./data')
# st.write(path)

# path = os.path.join('./data', file_temp)  # "/_first_azure/data"

# st.markdown(os.listdir("/_first_azure/"))
file = f'{path}/{st.selectbox("select file: ", os.listdir(path))}'
st.markdown(file)

with open(file, 'r') as f:
    text = f.read()[:500] + '....'

    st.write(text)


# # Adds a checkbox to the sidebar
# add_selectbox = st.sidebar.checkbox(
#     'How would you like to be contacted?',
#     ('Email', 'Home phone', 'Mobile phone'))

# # Adds a slider to the sidebar
# add_slider = st.sidebar.slider(
#     'Select a range of values',
#     1.0, 100.0, (1.0, 50.0))

# # Amsterdam 52.379189, 4.899431 - km to latlon [71, 111]
# map_data = pd.DataFrame(
#     np.random.randn(5000, 2) * [add_slider[0]/71, add_slider[1]/71] + [52.379189, 4.899431],
#     columns=['lat', 'lon'])

# st.map(map_data)





# cars = data.cars()
# iris = data.iris()

# cars_scatter = alt.Chart(cars).mark_point().encode(
#     x="Horsepower",
#     y="Miles_per_Gallon",
#     color="Origin",
# )

# iris_scatter = alt.Chart(iris).mark_circle().encode(
#     alt.X('sepalLength', scale=alt.Scale(zero=False)),
#     alt.Y('sepalWidth', scale=alt.Scale(zero=False)),
#     color='species'
# )

# chart = cars_scatter | iris_scatter

# def id_transform(data):
#     """ Altair data transformer that returns a fake named dataset with the object id. """
#     return {
#         "name": str(id(data))
#     }

# # register the id transformer
# alt.data_transformers.register("id", id_transform)

# with alt.data_transformers.enable("id"):
#     chart_dict = chart.to_dict()

#     st.json(chart_dict)

#     data = {
#         id(cars): cars,
#         id(iris): iris
#     }

#     st.vega_lite_chart(data, chart_dict)
