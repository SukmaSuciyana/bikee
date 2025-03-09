import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Bike Rental Analysis", layout="wide")

try:
    day_df = pd.read_csv("dashboard/days.csv") 

except FileNotFoundError:
    st.error("Error: File 'days.csv' tidak ditemukan. Pastikan file ada di direktori yang benar.")
    st.stop()

# Data Cleaning & Transformation
day_df.drop(columns=['instant', 'windspeed'], inplace=True, errors='ignore')

day_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'weathersit': 'weather_cond',
    'cnt': 'count'
}, inplace=True)

month_map = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
             7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
weekday_map = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
weather_map = {1: 'Clear/Partly Cloudy', 2: 'Misty/Cloudy', 3: 'Light Snow/Rain', 4: 'Severe Weather'}

day_df['month'] = day_df['month'].map(month_map)
day_df['season'] = day_df['season'].map(season_map)
day_df['weekday'] = day_df['weekday'].map(weekday_map)
day_df['weather_cond'] = day_df['weather_cond'].map(weather_map)

day_df['dateday'] = pd.to_datetime(day_df['dateday'])

categorical_cols = ['season', 'year', 'month', 'holiday', 'weekday', 'workingday', 'weather_cond']
day_df[categorical_cols] = day_df[categorical_cols].astype('category')

# Streamlit Dashboard
st.title("🚴‍♂️ Bike Rental Analysis Dashboard 🚴‍♂️")
st.markdown("### Analisis Penyewaan Sepeda Berdasarkan Berbagai Faktor")

# Sidebar filters
st.sidebar.header("Filter Data")
year_filter = st.sidebar.selectbox("Pilih Tahun", options=day_df['year'].cat.categories, index=0)
filtered_df = day_df[day_df['year'] == year_filter]

# Pengaruh Kondisi Cuaca Terhadap Penyewaan
st.subheader("Pengaruh Kondisi Cuaca Terhadap Penyewaan Sepeda")

fig = px.box(filtered_df, x='weather_cond', y='count', color='weather_cond',
             title='Pengaruh Kondisi Cuaca Terhadap Penyewaan Sepeda',
             labels={'weather_cond': 'Kondisi Cuaca', 'count': 'Jumlah Penyewaan'})

st.plotly_chart(fig)

# Penyewaan berdasarkan hari dalam seminggu
st.subheader("Penyewaan Sepeda Berdasarkan Hari dalam Minggu")

fig = px.box(filtered_df, x='weekday', y='count', color='weekday',
             category_orders={"weekday": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]},
             title='Penyewaan Sepeda Berdasarkan Hari dalam Minggu',
             labels={'weekday': 'Hari', 'count': 'Jumlah Penyewaan'})

st.plotly_chart(fig)

# Perbandingan hari kerja vs non-hari kerja
st.subheader("Perbandingan Penyewaan: Working Day vs Non-Working Day")

fig = px.box(filtered_df, x='workingday', y='count', color='workingday',
             title='Perbandingan Penyewaan: Working Day vs Non-Working Day',
             labels={'workingday': 'Kategori Hari', 'count': 'Jumlah Penyewaan'},
             category_orders={'workingday': [0, 1]},
             category_orders_labels={0: 'Non-Working Day', 1: 'Working Day'}
             )

fig.update_xaxes(
    tickvals=[0, 1],
    ticktext=['Non-Working Day', 'Working Day']
)

st.plotly_chart(fig)

st.subheader("Tren Penyewaan Sepeda Berdasarkan Waktu")

fig = px.line(filtered_df, x='dateday', y='count', color='year',
              title='Tren Penyewaan Sepeda Berdasarkan Waktu',
              labels={'dateday': 'Tanggal', 'count': 'Jumlah Penyewaan', 'year': 'Tahun'})

st.plotly_chart(fig)

# Hubungan antara suhu dan penyewaan
st.subheader("Hubungan Antara Suhu dan Jumlah Penyewaan")

fig = px.scatter(filtered_df, x='temp', y='count', color='season',
                 title='Hubungan Antara Suhu dan Jumlah Penyewaan',
                 labels={'temp': 'Suhu', 'count': 'Jumlah Penyewaan', 'season': 'Musim'})

st.plotly_chart(fig)

# Pengaruh Musim Terhadap Penyewaan Sepeda
st.subheader("Distribusi Penyewaan Berdasarkan Musim")

fig = px.box(filtered_df, x='season', y='count', color='season',
             category_orders={"season": ["Spring", "Summer", "Fall", "Winter"]},
             title='Distribusi Penyewaan Berdasarkan Musim',
             labels={'season': 'Musim', 'count': 'Jumlah Penyewaan'})

st.plotly_chart(fig)

st.caption('Copyright (c) Sukma Suciyana 2025')