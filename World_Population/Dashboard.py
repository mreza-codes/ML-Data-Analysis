import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import nan as NA
from sklearn.ensemble import RandomForestRegressor
import streamlit as st

# -----------------------------
# 1) Load dataset
# -----------------------------
df = pd.read_csv('Titanic-Dataset.csv')

# -----------------------------
# 2) Convert Sex to numeric
# -----------------------------
df["Sex"] = df["Sex"].map({"male": 0, "female": 1})

# -----------------------------
# 3) Impute missing Age using RandomForest
# -----------------------------
features = ['Sex', 'Pclass', 'Fare', 'SibSp', 'Parch']

df_full = df[df["Age"].notnull()]
df_missing = df[df["Age"].isnull()]

x_train = df_full[features]
y_train = df_full["Age"]

model = RandomForestRegressor()
model.fit(x_train, y_train)

x_missing = df_missing[features]
predicted_ages = model.predict(x_missing)

df.loc[df["Age"].isnull(), "Age"] = predicted_ages

# -----------------------------
# 4) Detect and remove outliers in Age
# -----------------------------
def detect_outliers(a):
    Q1 = a.quantile(0.25)
    Q3 = a.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (a < lower_bound) | (a > upper_bound)

outliers_age = detect_outliers(df["Age"])
df = df[~outliers_age]
df = df.reset_index(drop=True)

# -----------------------------
# 5) Survival by gender
# -----------------------------
female_survive = len(df[(df['Sex'] == 1) & (df['Survived'] == 1)])
male_survive = len(df[(df['Sex'] == 0) & (df['Survived'] == 1)])

len_female = len(df[df['Sex'] == 1])
len_male = len(df[df['Sex'] == 0])

percent_survive_female = (female_survive / len_female) * 100
percent_survive_male = (male_survive / len_male) * 100

# -----------------------------
# 6) Survival by class
# -----------------------------
percent_survive_class = df.groupby('Pclass')['Survived'].mean() * 100

# -----------------------------
# 7) Survival by class + gender
# -----------------------------
percent_survive_class_gender = df.groupby(['Sex', 'Pclass'])['Survived'].mean() * 100

# -----------------------------
# 8) Average age of survivors vs non-survivors
# -----------------------------
avg_age_status = df.groupby('Survived')['Age'].mean()
avg_age_status.index = ['Dead', 'Survived']

# -----------------------------
# 9) Age groups (10 bins)
# -----------------------------
df['Age_Group'] = pd.cut(df['Age'], 10)

survival_by_age_group = df.groupby('Age_Group')['Survived'].mean() * 100

# -----------------------------
# 10) Age group + gender
# -----------------------------
survival_age_gender = df.groupby(['Age_Group', 'Sex'])['Survived'].mean().unstack() * 100

# -----------------------------
# 11) Streamlit dashboard layout
# ----------------------------
st.title("Titanic Survival Analysis Dashboard")
st.markdown("""
این داشبورد، تحلیل زنده‌ماندن مسافران کشتی تایتانیک را بر اساس جنسیت، کلاس و سن نشان می‌دهد
""")
st.subheader("Dataset overview")
#number of index and columns:
st.write(f"تعداد ردیف‌ها: {df.shape[0]}")
st.write(f"تعداد ستون‌ها: {df.shape[1]}")
st.dataframe(df.head())  

# -----------------------------
#  زنده‌ماندن بر اساس جنسیت
# -----------------------------
st.subheader("Survival by gender")

col1, col2 = st.columns(2)  # دو ستون کنار هم برای نمایش مقادیر

# نمایش درصد زنده‌ماندن زنان
with col1:
    st.metric(
        label="درصد زنده‌ماندن زنان",
        value=f"{percent_survive_female:.2f} %"
    )

# نمایش درصد زنده‌ماندن مردان
with col2:
    st.metric(
        label="درصد زنده‌ماندن مردان",
        value=f"{percent_survive_male:.2f} %"
    )

# -----------------------------
#  زنده‌ماندن بر اساس کلاس
# -----------------------------
st.subheader("Survival rate by passenger class")

fig_class, ax_class = plt.subplots(figsize=(8, 4))  # ساخت شکل و محور

# رسم نمودار میله‌ای درصد زنده‌ماندن بر اساس کلاس
percent_survive_class.plot(kind='bar', ax=ax_class, color='skyblue',rot = 0)

ax_class.set_xlabel("Passenger Class")
ax_class.set_ylabel("Survival Rate (%)")
ax_class.set_title("Survival Rate by Class")

st.pyplot(fig_class)  # نمایش نمودار در داشبورد

# -----------------------------
#میانگین سن زنده‌مانده‌ها و فوت‌شده‌ها
# -----------------------------
st.subheader("Average age of survivors vs non-survivors")

fig_age, ax_age = plt.subplots(figsize=(8, 4))

avg_age_status.plot(kind='bar', ax=ax_age, color=['red', 'green'],rot = 0)

ax_age.set_xlabel("Status")
ax_age.set_ylabel("Average Age")
ax_age.set_title("Average Age of Survivors and Non-Survivors")

st.pyplot(fig_age)

# -----------------------------
# نرخ زنده‌ماندن بر اساس گروه سنی
# -----------------------------
st.subheader("Survival rate by age group")

fig_age_group, ax_age_group = plt.subplots(figsize=(10, 4))

survival_by_age_group.plot(kind='bar', ax=ax_age_group, rot=90, color='skyblue')

ax_age_group.set_xlabel("Age Group")
ax_age_group.set_ylabel("Survival Rate (%)")
ax_age_group.set_title("Survival Rate by Age Group")

st.pyplot(fig_age_group)

# -----------------------------
# نرخ زنده‌ماندن بر اساس گروه سنی و جنسیت
# -----------------------------
st.subheader("Survival rate by age group and gender")

bins = [0, 10, 20, 30, 40, 50, 60, 80]
labels = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-80"]

df['Age_Group'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)

survival_age_gender = df.groupby(['Age_Group', 'Sex'])['Survived'].mean().unstack() * 100

# تبدیل 0 و 1 به مرد و زن
survival_age_gender.columns = ['مرد', 'زن']

st.dataframe(survival_age_gender)








