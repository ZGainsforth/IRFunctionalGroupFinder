import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

st.markdown('# Functional group finder')

Groups = pd.read_csv('FunctionalGroups.csv', index_col=0).sort_values('min cm-1')
st.markdown('### List of all functional groups.')
st.write(Groups)

ShowGroups = st.sidebar.multiselect('Select Functional Groups by bond (up to 5)', np.sort(Groups['Group'].unique()))

ShowNames = st.sidebar.multiselect('Select Functional Groups by description (up to 5)', np.sort(Groups['Name'].unique()))

ColorList = ['red', 'green', 'orange', 'purple', 'black']

SearchAround = st.sidebar.slider('Search around cm-1:', Groups['min cm-1'].astype(float).min(), Groups['max cm-1'].astype(float).max(), 1000.0, 10.0)
SearchWidth = st.sidebar.slider('Search plus minus cm-1:', 0.0, 1000.0, 10.0, 1.0)

SearchForGroups = Groups[Groups['min cm-1'] < SearchAround+SearchWidth]
SearchForGroups = SearchForGroups[SearchForGroups['max cm-1'] > SearchAround-SearchWidth]
st.markdown(f'### Functional groups between {SearchAround-SearchWidth} and {SearchAround+SearchWidth} cm-1')
st.write(SearchForGroups)

# We can show multiple spectra, but we need to keep them in a list.
SpectrumDict = {} 
# Option to add a spectrum.
st.set_option('deprecation.showfileUploaderEncoding', False)
SpectrumFiles = st.file_uploader('Choose a spectrum file(s) in csv two-column format: (cm-1, intensity [between 0 and 1]):', accept_multiple_files=True)
if SpectrumFiles is not None:
    for SpectrumFile in SpectrumFiles:
        SpectrumDict[SpectrumFile.name] = pd.read_csv(SpectrumFile)

# If there is no spectrum, and the user isn't adding one, then we have to have a default (empty) spectrum so we can still show functional group positions in the plot.
if (len(SpectrumDict) == 0):
    S = pd.DataFrame()
    S['cm-1'] = range(0,4000,4)
    S['I'] = np.zeros(1000)
    st.write('Loading default spectrum.')
    SpectrumDict['Default'] = S

fig = go.Figure(layout_title_text='Experimental Spectrum')
for label,S in SpectrumDict.items():
    x,y = S.iloc[:,0], S.iloc[:,1]
    fig.add_trace(go.Line(x=x, y=y, name=label))
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
if len(ShowNames) > 0:
    for i, g in enumerate(ShowNames):
        Records = Groups[Groups['Name'] == g]
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
        fig.add_trace(go.Line(x=r_x, y=r_y, name=f'{r["Name"]}', mode='lines', line=dict(color=ColorList[i%len(ColorList)], width=5)))

st.write(fig)
