import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix

st.set_page_config(page_title="Iris Dashboard", layout="wide")

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("Iris.csv")

st.title("🌸 Iris Dataset Analysis Dashboard")
st.write("A clean and structured dashboard for exploring the Iris dataset.")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Navigation")
section = st.sidebar.radio("Go to section:", 
                           ["Dataset Overview", 
                            "Scatter Plot",
                            "Box Plot",
                            "Pair Plot",
                            "Statistical Summary",
                            "SVM Classification"])

# -----------------------------
# Dataset Overview
# -----------------------------
if section == "Dataset Overview":
    st.header("📁 Dataset Overview")
    st.write("### First 5 Rows")
    st.dataframe(df.head())

    st.write("### Dataset Description")
    st.dataframe(df.describe())

    st.write("### Columns")
    st.write(df.columns.tolist())

# -----------------------------
# Scatter Plot
# -----------------------------
elif section == "Scatter Plot":
    st.header("Scatter Plot: Petal Length vs Petal Width")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.scatterplot(data=df, x='PetalLengthCm', y='PetalWidthCm', hue='Species', ax=ax)
    st.pyplot(fig)

# -----------------------------
# Box Plot
# -----------------------------
elif section == "Box Plot":
    st.header("Box Plot: Sepal Width by Species")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.boxplot(data=df, x='Species', y='SepalWidthCm', hue='Species', ax=ax)
    ax.grid()
    st.pyplot(fig)

# -----------------------------
# Pair Plot
# -----------------------------
elif section == "Pair Plot":
    st.header("Pair Plot of Iris Features")
    st.write("This may take a few seconds…")
    fig = sns.pairplot(data=df.drop(columns=['Id']), hue='Species')
    st.pyplot(fig)

# -----------------------------
# Statistical Summary
# -----------------------------
elif section == "Statistical Summary":
    st.header("📊 Statistical Summary by Species")
    x = df.drop(columns=['Id']).groupby('Species')
    summary = x.aggregate(['mean','std','min','max'])
    st.dataframe(summary)

# -----------------------------
# SVM Classification
# -----------------------------
elif section == "SVM Classification":
    st.header("🤖 SVM Classification")

    features = df[['SepalLengthCm','SepalWidthCm','PetalLengthCm','PetalWidthCm']]
    y = df['Species']

    le = LabelEncoder()
    y = le.fit_transform(y)

    x_train, x_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42)

    model = SVC(kernel='linear')
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)

    st.subheader("Model Accuracy")
    st.metric("Accuracy", f"{acc*100:.2f}%")

    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6,4))
    sns.heatmap(cm, annot=True, cmap='Blues', fmt='d',
                xticklabels=le.classes_, yticklabels=le.classes_, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    st.pyplot(fig)
