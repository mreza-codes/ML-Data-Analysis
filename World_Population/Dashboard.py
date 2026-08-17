import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from matplotlib.ticker import FuncFormatter

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("world_population.csv")

df = load_data()

st.title("🌍 World Population Dashboard")
st.write("این داشبورد تحلیل جمعیت جهان را نمایش می‌دهد.")

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Section", [
    "Population by Continent",
    "Top 10 Population Countries",
    "South Korea Population Trend",
    "Top 10 Density Heatmap",
    "Iran Population Prediction (ML)"
])

colors = sns.color_palette('tab10')[0:10]

# -----------------------------
# 1) Population by Continent
# -----------------------------
if page == "Population by Continent":
    st.header("Population by Continent (2022)")

    continent_population = df.groupby('Continent')['2022 Population'].sum()

    fig, ax = plt.subplots(figsize=(10,6))
    ax.bar(continent_population.index, continent_population.values, color=colors)
    ax.set_title("Population by Continent (2022)")
    ax.set_xlabel("Continent")
    ax.set_ylabel("Population")
    st.pyplot(fig)

# -----------------------------
# 2) Top 10 Population Countries
# -----------------------------
elif page == "Top 10 Population Countries":
    st.header("Top 10 Population Countries (2022)")

    top10 = df.sort_values('2022 Population', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(8,8))
    wedges, texts, autotexts = ax.pie(
        top10['2022 Population'],
        autopct='%1.1f%%',
        colors=colors
    )
    ax.legend(
        handles=wedges,
        labels=top10['Country/Territory'].tolist(),
        title="Top 10 Population",
        loc="upper right",
        bbox_to_anchor=(1.13, 1)
    )
    ax.set_title("Top 10 Population Countries (2022)")
    st.pyplot(fig)

# -----------------------------
# 3) South Korea Population Trend
# -----------------------------
elif page == "South Korea Population Trend":
    st.header("South Korea Population Trend")

    columns = ['2000 Population', '2010 Population', '2015 Population', '2020 Population', '2022 Population']
    sk = df[df['Country/Territory'] == 'South Korea']

    populations = sk[columns].values.flatten() / 1_000_000
    years = [2000, 2010, 2015, 2020, 2022]

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(years, populations, marker='o', linestyle='dashed', color='red')
    ax.set_title("South Korea Population Trend")
    ax.set_xlabel("Year")
    ax.set_ylabel("Population (Millions)")
    ax.grid(True)
    st.pyplot(fig)

# -----------------------------
# 4) Top 10 Density Heatmap
# -----------------------------
elif page == "Top 10 Density Heatmap":
    st.header("Countries with Highest Population Density")

    top_density = df.sort_values('Density (per km²)', ascending=False).head(10)
    top_density = top_density[['Country/Territory', 'Density (per km²)']].set_index('Country/Territory')

    fig, ax = plt.subplots(figsize=(12,6))
    sns.heatmap(
        top_density,
        cmap='YlGnBu',
        annot=True,
        fmt='.0f',
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    ax.set_title("Countries with Highest Population Density")
    st.pyplot(fig)

# -----------------------------
# 5) Iran Population Prediction (ML)
# -----------------------------
elif page == "Iran Population Prediction (ML)":
    st.header("Iran Population Prediction (ML)")

    iran = df[df['Country/Territory'] == 'Iran']

    years = [1970, 1980, 1990, 2000, 2010, 2015, 2020, 2022]
    pop = [
        iran['1970 Population'].values[0],
        iran['1980 Population'].values[0],
        iran['1990 Population'].values[0],
        iran['2000 Population'].values[0],
        iran['2010 Population'].values[0],
        iran['2015 Population'].values[0],
        iran['2020 Population'].values[0],
        iran['2022 Population'].values[0]
    ]

    data = pd.DataFrame({'Year': years, 'Population': pop})

    train = data[data['Year'] < 2022]
    X_train = train[['Year']]
    y_train = train['Population']

    model = LinearRegression()
    model.fit(X_train, y_train)

    pred_2022 = model.predict(pd.DataFrame({'Year': [2022]}))[0]
    real_2022 = data[data['Year'] == 2022]['Population'].values[0]

    def millions(x, pos):
        return f'{int(x/1_000_000)}M'

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(data['Year'], data['Population'], marker='o', label='Real Population')
    ax.scatter(2022, pred_2022, color='red', label='Predicted 2022')
    ax.yaxis.set_major_formatter(FuncFormatter(millions))
    ax.set_title("Iran Population Prediction")
    ax.set_xlabel("Year")
    ax.set_ylabel("Population")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    st.write(f"**Real 2022:** {real_2022:,}")
    st.write(f"**Predicted 2022:** {int(pred_2022):,}")
    st.write(f"**Error:** {abs(real_2022 - pred_2022):,}")
