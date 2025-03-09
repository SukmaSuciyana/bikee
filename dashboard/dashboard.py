import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Bike Rental Analysis", layout="wide")

# Membaca data
day_df = pd.read_csv("dashboard/days.csv")

# Menghapus kolom yang tidak diperlukan
day_df.drop(columns=['windspeed'], inplace=True)

# Mengubah nama judul kolom
day_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'weathersit': 'weather_cond',
    'cnt': 'count'
}, inplace=True)

# Fungsi untuk mapping data
def map_data(df):
    df['month'] = df['month'].map({
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    })
    df['season'] = df['season'].map({
        1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
    })
    df['weekday'] = df['weekday'].map({
        0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'
    })
    df['weather_cond'] = df['weather_cond'].map({
        1: 'Clear/Partly Cloudy',
        2: 'Misty/Cloudy',
        3: 'Light Snow/Rain',
        4: 'Severe Weather'
    })
    return df

# Mapping data
day_df = map_data(day_df)

# Fungsi untuk membuat DataFrame
def create_df(df, groupby_col, agg_col, agg_func='sum'):
    return df.groupby(by=groupby_col).agg({agg_col: agg_func}).reset_index()

# Membuat komponen filter
min_date = pd.to_datetime(day_df['dateday']).dt.date.min()
max_date = pd.to_datetime(day_df['dateday']).dt.date.max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan tanggal
main_df = day_df[(pd.to_datetime(day_df['dateday']).dt.date >= start_date) & 
                 (pd.to_datetime(day_df['dateday']).dt.date <= end_date)]

# Membuat berbagai DataFrame
daily_rent_df = create_df(main_df, 'dateday', 'count')
daily_casual_rent_df = create_df(main_df, 'dateday', 'casual')
daily_registered_rent_df = create_df(main_df, 'dateday', 'registered')
season_rent_df = create_df(main_df, 'season', ['registered', 'casual'])
monthly_rent_df = create_df(main_df, 'month', 'count')
weekday_rent_df = create_df(main_df, 'weekday', 'count')
workingday_rent_df = create_df(main_df, 'workingday', 'count')
holiday_rent_df = create_df(main_df, 'holiday', 'count')
weather_rent_df = create_df(main_df, 'weather_cond', 'count')

# Menampilkan DataFrame (opsional)
st.write("Daily Rent DataFrame:", daily_rent_df)
st.write("Season Rent DataFrame:", season_rent_df)
st.write("Monthly Rent DataFrame:", monthly_rent_df)
st.write("Weekday Rent DataFrame:", weekday_rent_df)
st.write("Workingday Rent DataFrame:", workingday_rent_df)
st.write("Holiday Rent DataFrame:", holiday_rent_df)
st.write("Weather Rent DataFrame:", weather_rent_df)

# Visualisasi data (opsional)
st.write("Daily Rent Chart")
fig = px.line(daily_rent_df, x='dateday', y='count', title='Daily Bike Rentals')
st.plotly_chart(fig)

st.write("Season Rent Chart")
fig = px.bar(season_rent_df, x='season', y=['registered', 'casual'], title='Seasonal Bike Rentals')
st.plotly_chart(fig)

# Membuat judul
st.header('🚲Bike Rental Dashboard 🚲🚲...')

# --- Jumlah Penyewaan Harian ---
st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual_rent_df['casual'].sum()
    st.metric('Casual User', value=daily_rent_casual, delta=None, delta_color="normal")

with col2:
    daily_rent_registered = daily_registered_rent_df['registered'].sum()
    st.metric('Registered User', value=daily_rent_registered, delta=None, delta_color="normal")

with col3:
    daily_rent_total = daily_rent_df['count'].sum()
    st.metric('Total User', value=daily_rent_total, delta=None, delta_color="normal")

# --- Jumlah Penyewaan Bulanan ---
st.subheader('Monthly Rentals')

# Membuat grafik 
fig = px.line(
    monthly_rent_df,
    x=monthly_rent_df.index,
    y='count',
    title='Monthly Rentals',
    labels={'count': 'Rent Count', 'index': 'Month'},
    line_shape='linear',
    render_mode='svg'
)

fig.update_traces(line=dict(color='skyblue', width=2))
st.plotly_chart(fig, use_container_width=True) # Menampilkan grafik di Streamlit

# Membuat jumlah penyewaan berdasarkan season
st.subheader('Seasonly Rentals')
# Membuat grafik batang bertumpuk 
fig = go.Figure(data=[
    go.Bar(name='Registered', x=season_rent_df['season'], y=season_rent_df['registered'], marker_color='skyblue'),
    go.Bar(name='Casual', x=season_rent_df['season'], y=season_rent_df['casual'], marker_color='lightcoral')
])

# Menambahkan label teks di atas batang
for index, row in season_rent_df.iterrows():
    fig.add_annotation(
        x=row['season'],
        y=row['registered'],
        text=str(row['registered']),
        showarrow=False,
        yshift=10,
        font=dict(size=12)
    )
    fig.add_annotation(
        x=row['season'],
        y=row['casual'],
        text=str(row['casual']),
        showarrow=False,
        yshift=10,
        font=dict(size=12)
    )

# Mengatur tata letak grafik, termasuk legenda
fig.update_layout(
    barmode='stack',
    xaxis_title=None,
    yaxis_title=None,
    xaxis=dict(tickfont=dict(size=15)),
    yaxis=dict(tickfont=dict(size=12)),
    legend=dict(
        orientation="h",  # Mengatur legenda menjadi horizontal
        yanchor="bottom",  # Menempatkan legenda di bagian bawah
        y=1.02,  # Sedikit di atas bagian bawah untuk menghindari tumpang tindih
        xanchor="right",  # Menempatkan legenda di bagian kanan
        x=1  # Paling kanan
    )
)

st.plotly_chart(fig, use_container_width=True) # Menampilkan grafik di Streamlit


st.subheader('Weatherly Rentals')
# Daftar warna yang sesuai dengan matplotlib colors
colors = ["skyblue", "lightcoral", "lightgreen"] 

# Membuat grafik batang 
fig = go.Figure(data=[
    go.Bar(
        x=weather_rent_df.index,
        y=weather_rent_df['count'],
        marker_color=colors
    )
])

# Menambahkan label teks di atas batang
for index, value in enumerate(weather_rent_df['count']):
    fig.add_annotation(
        x=weather_rent_df.index[index],
        y=value,
        text=str(value),
        showarrow=False,
        yshift=10,
        font=dict(size=12)
    )

# Mengatur tata letak grafik
fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    xaxis=dict(tickfont=dict(size=15)),
    yaxis=dict(tickfont=dict(size=12))
)

st.plotly_chart(fig, use_container_width=True) # Menampilkan grafik di Streamlit

# Membuat jumlah penyewaan berdasarkan weekday, working dan holiday
st.subheader('Weekday, Workingday, and Holiday Rentals')
# --- Grafik Berdasarkan Working Day ---
st.write('Number of Rents based on Working Day')
colors1 = ["skyblue", "lightcoral"]
fig1 = go.Figure(data=[
    go.Bar(x=workingday_rent_df['workingday'], y=workingday_rent_df['count'], marker_color=colors1)
])
for index, value in enumerate(workingday_rent_df['count']):
    fig1.add_annotation(x=workingday_rent_df['workingday'].iloc[index], y=value, text=str(value), showarrow=False, yshift=10, font=dict(size=12))
fig1.update_layout(xaxis_title=None, yaxis_title=None, xaxis=dict(tickfont=dict(size=15)), yaxis=dict(tickfont=dict(size=10)))
st.plotly_chart(fig1, use_container_width=True)

# --- Grafik Berdasarkan Holiday ---
st.write('Number of Rents based on Holiday')
colors2 = ["skyblue", "lightcoral"]
fig2 = go.Figure(data=[
    go.Bar(x=holiday_rent_df['holiday'], y=holiday_rent_df['count'], marker_color=colors2)
])
for index, value in enumerate(holiday_rent_df['count']):
    fig2.add_annotation(x=holiday_rent_df['holiday'].iloc[index], y=value, text=str(value), showarrow=False, yshift=10, font=dict(size=12))
fig2.update_layout(xaxis_title=None, yaxis_title=None, xaxis=dict(tickfont=dict(size=15)), yaxis=dict(tickfont=dict(size=10)))
st.plotly_chart(fig2, use_container_width=True)

# --- Grafik Berdasarkan Weekday ---
st.write('Number of Rents based on Weekday')
colors3 = ["skyblue", "lightcoral", "lightgreen", "lightsalmon", "plum", "tan", "pink"]
fig3 = go.Figure(data=[
    go.Bar(x=weekday_rent_df['weekday'], y=weekday_rent_df['count'], marker_color=colors3)
])
for index, value in enumerate(weekday_rent_df['count']):
    fig3.add_annotation(x=weekday_rent_df['weekday'].iloc[index], y=value, text=str(value), showarrow=False, yshift=10, font=dict(size=12))
fig3.update_layout(xaxis_title=None, yaxis_title=None, xaxis=dict(tickfont=dict(size=15)), yaxis=dict(tickfont=dict(size=10)))
st.plotly_chart(fig3, use_container_width=True)
st.caption('Copyright (c) Sukma Suciyana 2025')
