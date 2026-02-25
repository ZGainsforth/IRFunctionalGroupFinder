import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

st.markdown('# Functional group finder')

# Select whether we are doing XANES or IR
SpectrumType = st.sidebar.radio('Spectral type', ['IR','XANES'])

# Ionization thresholds for XANES (eV), ordered by energy
XANES_THRESHOLDS = {
    'C K':   (290.0,  'steelblue'),
    'Ca L3': (346.2,  'seagreen'),
    'Ca L2': (349.7,  'seagreen'),
    'N K':   (409.9,  'steelblue'),
    'Ti L3': (453.8,  'darkorange'),
    'Ti L2': (459.4,  'darkorange'),
    'O K':   (543.1,  'steelblue'),
    'Fe L3': (706.8,  'firebrick'),
    'Fe L2': (719.9,  'firebrick'),
    'Ni L3': (852.7,  'mediumpurple'),
    'Ni L2': (870.0,  'mediumpurple'),
}

if SpectrumType == 'XANES':
    Groups = pd.read_csv('XANESFunctionalGroups.csv', index_col=0).sort_values('min eV')
    # 'Group' column holds the functional group name; derive absorption edge for Group
    Groups['Name'] = Groups['Group']
    Groups['Group'] = Groups['min eV'].apply(lambda x: 'C 1s' if x < 298 else ('N 1s' if x < 500 else 'O 1s'))
    SpectrumUnit = 'eV'
    # A default spectrum in case the user doesn't load one.
    S = pd.DataFrame()
    S[SpectrumUnit] = np.linspace(250,1000,10000)
    S['I'] = np.zeros(len(S[SpectrumUnit]))
    MinimumFeatureWidth = 0.5
else:
    Groups = pd.read_csv('IRFunctionalGroups.csv', index_col=0).sort_values('min cm-1')
    SpectrumUnit = 'cm-1'
    # A default spectrum in case the user doesn't load one.
    S = pd.DataFrame()
    S[SpectrumUnit] = range(0,4000,4)
    S['I'] = np.zeros(len(S[SpectrumUnit]))
    MinimumFeatureWidth = 10.0

SpectrumMin = Groups[f'min {SpectrumUnit}'].astype(float).min()
SpectrumMax = Groups[f'max {SpectrumUnit}'].astype(float).max()
st.markdown('### List of all functional groups.')
st.write(Groups)

ShowGroups = st.sidebar.multiselect('Select Functional Groups by bond (up to 5)', np.sort(Groups['Group'].unique()))

ShowNames = st.sidebar.multiselect('Select Functional Groups by description (up to 5)', np.sort(Groups['Name'].unique()))

if SpectrumType == 'XANES':
    ShowThresholds = st.sidebar.checkbox('Show ionization thresholds', value=True)

ColorList = ['red', 'green', 'orange', 'purple', 'gray']

SearchAround = st.sidebar.number_input(f'Search around {SpectrumUnit}:', value=10.0)
SearchWidth = st.sidebar.number_input(f'Search plus minus {SpectrumUnit}:', 0.0, (SpectrumMax+SpectrumMin)/10, 10.0, (SpectrumMax-SpectrumMin)/1000)
# SearchAround = st.sidebar.slider(f'Search around {SpectrumUnit}:', SpectrumMin, SpectrumMax, (SpectrumMax+SpectrumMin)/2, (SpectrumMax-SpectrumMin)/10000)
# SearchWidth = st.sidebar.slider(f'Search plus minus {SpectrumUnit}:', 0.0, (SpectrumMax+SpectrumMin)/10, 10.0, (SpectrumMax-SpectrumMin)/1000)

SearchForGroups = Groups[Groups[f'min {SpectrumUnit}'] < SearchAround+SearchWidth]
SearchForGroups = SearchForGroups[SearchForGroups[f'max {SpectrumUnit}'] > SearchAround-SearchWidth]
st.markdown(f'### Functional groups between {SearchAround-SearchWidth} and {SearchAround+SearchWidth} {SpectrumUnit}')
st.write(SearchForGroups)

# We can show multiple spectra, but we need to keep them in a list.
SpectrumDict = {}
# Option to add a spectrum.
#st.set_option('deprecation.showfileUploaderEncoding', False)
SpectrumFiles = st.file_uploader(f'Choose a spectrum file(s) in csv two-column format: ({SpectrumUnit}, intensity [between 0 and 1]):', accept_multiple_files=True)
if SpectrumFiles is not None:
    for SpectrumFile in SpectrumFiles:
        try:
            SpectrumDict[SpectrumFile.name] = pd.read_csv(SpectrumFile, delim_whitespace=True)
        except IndexError:
            st.write('Not comma delimited.')

# If there is no spectrum, and the user isn't adding one, then we have to have a default (empty) spectrum so we can still show functional group positions in the plot.
if (len(SpectrumDict) == 0):
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
            if r[f'min {SpectrumUnit}'] == r[f'max {SpectrumUnit}']:
                r_x.append(r[f'min {SpectrumUnit}']-MinimumFeatureWidth)
                r_x.append(r[f'min {SpectrumUnit}']+MinimumFeatureWidth)
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
            else:
                r_x.append(r[f'min {SpectrumUnit}'])
                r_x.append(r[f'max {SpectrumUnit}'])
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
            if r[f'min {SpectrumUnit}'] == r[f'max {SpectrumUnit}']:
                r_x.append(r[f'min {SpectrumUnit}']-MinimumFeatureWidth)
                r_x.append(r[f'min {SpectrumUnit}']+MinimumFeatureWidth)
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
            else:
                r_x.append(r[f'min {SpectrumUnit}'])
                r_x.append(r[f'max {SpectrumUnit}'])
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
        fig.add_trace(go.Line(x=r_x, y=r_y, name=f'{r["Name"]}', mode='lines', line=dict(color=ColorList[i%len(ColorList)], width=5)))

if SpectrumType == 'XANES':
    # Autoscale x-axis: ±50 eV around the shown functional groups.
    # Collect all records currently being displayed as group markers.
    dfs = []
    if ShowGroups:
        dfs.append(Groups[Groups['Group'].isin(ShowGroups)])
    if ShowNames:
        dfs.append(Groups[Groups['Name'].isin(ShowNames)])
    selected = pd.concat(dfs) if dfs else pd.DataFrame(columns=Groups.columns)

    if len(selected) > 0:
        x_lo = selected['min eV'].min() - 50
        x_hi = selected['max eV'].max() + 50
    else:
        # No groups selected: show the full database range with padding
        x_lo = SpectrumMin - 50
        x_hi = SpectrumMax + 50
    fig.update_layout(xaxis_range=[x_lo, x_hi])

    # Ionization threshold vertical lines
    if ShowThresholds:
        for label, (ev, color) in XANES_THRESHOLDS.items():
            # Shift L2 labels down slightly so they don't overlap with adjacent L3
            yshift = -20 if label.endswith('L2') else 0
            fig.add_vline(
                x=ev,
                line_dash='dot',
                line_color=color,
                line_width=1,
                annotation_text=label,
                annotation_position='top',
                annotation_font_size=10,
                annotation_font_color=color,
                annotation_yshift=yshift,
            )

st.write(fig)
