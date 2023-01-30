import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

st.markdown('# Functional group finder')

Groups = pd.read_csv('FunctionalGroups.csv', index_col=0).sort_values('min cm-1')
st.markdown('### List of all functional groups.')
st.write(Groups)

ShowGroups = st.sidebar.multiselect('Select Functional Groups to show (up to 5)', Groups['Group'].unique())

ColorList = ['red', 'green', 'orange', 'purple', 'black']

SearchAround = st.sidebar.slider('Search around cm-1:', Groups['min cm-1'].astype(float).min(), Groups['max cm-1'].astype(float).max(), 1000.0, 10.0)
SearchWidth = st.sidebar.slider('Search plus minus cm-1:', 0.0, 1000.0, 10.0, 1.0)

SearchForGroups = Groups[Groups['min cm-1'] < SearchAround+SearchWidth]
SearchForGroups = SearchForGroups[SearchForGroups['max cm-1'] > SearchAround-SearchWidth]
st.markdown(f'### Functional groups between {SearchAround-SearchWidth} and {SearchAround+SearchWidth} cm-1')
st.write(SearchForGroups)

st.set_option('deprecation.showfileUploaderEncoding', False)
SpectrumFile = st.file_uploader('Choose a spectrum file:')
if SpectrumFile is not None:
    S = pd.read_csv(SpectrumFile)

    # st.write(S)

    fig = go.Figure(layout_title_text='Experimental Spectrum')
    x,y = S.iloc[:,0], S.iloc[:,1]
    fig.add_trace(go.Line(x=x, y=y))
    if len(ShowGroups) > 0:
        for i, g in enumerate(ShowGroups):
            Records = Groups[Groups['Group'] == g]
            r_x = []
            r_y = []
            for j,r in Records.iterrows():
                if r['min cm-1'] == r['max cm-1']:
                    r_x.append(r['min cm-1']-10)
                    r_x.append(r['min cm-1']+10)
                    r_x.append(None)
                    r_y.append(y.max()-1-i/10)
                    r_y.append(y.max()-1-i/10)
                    r_y.append(None)
                else:
                    r_x.append(r['min cm-1'])
                    r_x.append(r['max cm-1'])
                    r_x.append(None)
                    r_y.append(y.max()-1-i/10)
                    r_y.append(y.max()-1-i/10)
                    r_y.append(None)
            fig.add_trace(go.Line(x=r_x, y=r_y, name=f'{r["Group"]}', mode='lines', line=dict(color=ColorList[i%len(ColorList)], width=5)))

    st.write(fig)
