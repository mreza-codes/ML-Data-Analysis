import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree

st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("netflix_titles.csv")

st.title("🎬 Netflix Titles Analysis Dashboard")
st.write("A structured dashboard for exploring Netflix movies and TV shows.")

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to section:",
                           ["Dataset Overview",
                            "Movie Duration Analysis",
                            "Country Distribution",
                            "Movies per Year",
                            "Boxplot (Movies since 2010)",
                            "Heatmap (Ratings since 2015)",
                            "Decision Tree Model"])

# -----------------------------
# Dataset Overview
# -----------------------------
if section == "Dataset Overview":
    st.header("📁 Dataset Overview")
    st.write("### First 10 Rows")
    st.dataframe(df.head(10))

    st.write("### Missing Values")
    st.dataframe(df.isnull().sum())

    st.write("### Columns")
    st.write(df.columns.tolist())

# -----------------------------
# Movie Duration Analysis
# -----------------------------
elif section == "Movie Duration Analysis":
    st.header("⏱ Movie Duration Analysis")

    movies = df[df["type"] == "Movie"].dropna(subset=["duration"]).copy()
    movies["duration_min"] = movies["duration"].str.replace(" min", "", regex=False).astype(int)

    st.write("### Duration Statistics")
    st.write("Mean duration:", movies["duration_min"].mean())
    st.write("Percentage < 60 min:", (movies["duration_min"] < 60).mean() * 100)

    fig, ax = plt.subplots(figsize=(8, 5))   # slightly smaller
    sns.histplot(movies["duration_min"], bins=30, kde=True,
                 color="skyblue", edgecolor="black", ax=ax)
    ax.set_title("Histogram of Movie Durations")
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

# -----------------------------
# Country Distribution
# -----------------------------
elif section == "Country Distribution":
    st.header("🌍 Top 5 Countries")

    country_counts = df["country"].value_counts().head(5)

    fig, ax = plt.subplots(figsize=(7, 7))   # slightly smaller
    wedges, texts, autotexts = ax.pie(country_counts, autopct="%1.1f%%")
    ax.legend(wedges, country_counts.index, title="Country",
              loc="upper right", bbox_to_anchor=(1.15, 1))
    ax.set_title("Top 5 Countries by Number of Titles")
    st.pyplot(fig)

# -----------------------------
# Movies per Year
# -----------------------------
elif section == "Movies per Year":
    st.header("📅 Number of Movies & TV Shows per Year")

    grouped = df.groupby(["release_year", "type"]).size().unstack(fill_value=0)
    recent = grouped.loc[grouped.index > 2010]

    fig, ax = plt.subplots(figsize=(10, 5))   # slightly smaller
    recent.plot(kind="bar", rot=0, ax=ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.set_title("Movies & TV Shows per Year (since 2011)")
    st.pyplot(fig)

# -----------------------------
# Boxplot (Movies since 2010)
# -----------------------------
elif section == "Boxplot (Movies since 2010)":
    st.header("📦 Movie Duration Boxplot (since 2010)")

    movies = df[df["type"] == "Movie"].dropna(subset=["duration"]).copy()
    movies["duration_min"] = movies["duration"].str.replace(" min", "", regex=False).astype(int)
    movies_recent = movies[movies["release_year"] > 2009]

    fig, ax = plt.subplots(figsize=(10, 5))   # slightly smaller
    sns.boxplot(x="release_year", y="duration_min", data=movies_recent, ax=ax)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_title("Duration of Movies per Year (since 2010)")
    st.pyplot(fig)

# -----------------------------
# Heatmap (Ratings since 2015)
# -----------------------------
elif section == "Heatmap (Ratings since 2015)":
    st.header("🔥 Heatmap of Movie Ratings (since 2015)")

    movies_ratings = df[df["type"] == "Movie"].copy()
    movies_ratings = movies_ratings.dropna(subset=["release_year", "rating"])
    movies_ratings = movies_ratings[~movies_ratings["rating"].str.contains("min", na=False)]

    ratings = movies_ratings[movies_ratings["release_year"] > 2014] \
        .groupby(["release_year", "rating"]).size().reset_index(name="count")

    ratings_pivot = ratings.pivot(index="rating", columns="release_year", values="count").fillna(0)
    ratings_pivot = ratings_pivot.astype(int)

    fig, ax = plt.subplots(figsize=(10, 6))   # slightly smaller
    sns.heatmap(ratings_pivot, cmap="Reds", annot=True, fmt="g", ax=ax)
    ax.set_title("Number of Movies by Rating (since 2015)")
    st.pyplot(fig)

# -----------------------------
# Decision Tree Model
# -----------------------------
elif section == "Decision Tree Model":
    st.header("🌳 Decision Tree Classification (Movie vs TV Show)")

    df_ml = df.copy()
    df_ml = df_ml[["type", "duration", "rating", "listed_in"]].dropna()

    df_ml["genre"] = df_ml["listed_in"].apply(lambda x: x.split(",")[0])

    le_type = LabelEncoder()
    le_rating = LabelEncoder()
    le_genre = LabelEncoder()

    df_ml["type_enc"] = le_type.fit_transform(df_ml["type"])
    df_ml["rating_enc"] = le_rating.fit_transform(df_ml["rating"])
    df_ml["genre_enc"] = le_genre.fit_transform(df_ml["genre"])

    X = df_ml[["rating_enc", "genre_enc"]]
    y = df_ml["type_enc"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = DecisionTreeClassifier(criterion="entropy", random_state=42)
    model.fit(X_train, y_train)

    st.write("### Accuracy")
    st.metric("Train Accuracy", f"{model.score(X_train, y_train)*100:.2f}%")
    st.metric("Test Accuracy", f"{model.score(X_test, y_test)*100:.2f}%")

    fig = plt.figure(figsize=(18, 12))   # slightly smaller
    tree.plot_tree(model,
                   feature_names=["rating", "genre"],
                   class_names=le_type.classes_,
                   filled=True,
                   rounded=True,
                   fontsize=10)
    st.pyplot(fig)
