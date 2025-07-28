
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

VERSION = "v0.6"
LAST_MODIFIED = datetime.fromtimestamp(os.path.getmtime(__file__)).strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Credit Card Dashboard - {VERSION}** (Last modified: {LAST_MODIFIED})")

# --- File Loading ---
# df1 = pd.read_excel("max_2025_07.xlsx")
# df2 = pd.read_excel("max_2025_08.xlsx")
# df = pd.concat([df1, df2], ignore_index=True)
df = pd.read_excel("downloads/manual/max_all_3_month.xlsx", header=3)

# --- Column Mapping ---
COLUMN_MAPPING = {
    "תאריך עסקה": "Date",
    "שם בית העסק": "Business",
    "קטגוריה": "Category",
    "4 ספרות אחרונות של כרטיס האשראי": "CardNumber",
    "סכום חיוב": "Amount"
}
df = df.rename(columns=COLUMN_MAPPING)

# Remove totals and rows with invalid date
df = df[df["Date"].apply(lambda x: isinstance(x, str) and not x.startswith("סך הכל"))]
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Date"])
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# --- Translations ---
CATEGORY_TRANSLATIONS = {
    "מזון וצריכה": "Groceries",
    "מסעדות, קפה וברים": "Restaurants & Cafes",
    "תחבורה ורכבים": "Transportation & Vehicles",
    "רפואה ובתי מרקחת": "Pharmacy & Health",
    "פנאי, בידור וספורט": "Leisure & Entertainment",
    "שונות": "Miscellaneous",
    "עירייה וממשלה": "Municipality & Government",
    "ביטוח": "Insurance",
    "דלק, חשמל וגז": "Fuel, Electricity & Gas",
    "שירותי תקשורת": "Telecom Services",
    "חשמל ומחשבים": "Electronics & Computers",
    "העברת כספים": "Money Transfers",
    "ספרים ודפוס": "Books",
    "טיסות ותיירות": "Flights & Travel",
    "עיצוב הבית": "Home Design",
    "משיכת מזומן": "Cash Withdrawal"
}

BUSINESS_TRANSLATIONS = {
    "שיבא משק וחניה בע\"מ": "",
    "שרות וטרינרי-עיריית רחובו": "Veterinary",
    "אמיר בעיר": "Amir Ba'Ir",
    "גד רכיבה טיפולית": "Gad Therapeutic Riding",
    "רשות הדואר-רכישת מוצר דאר": "Israel Post",
    "קרן מכבי": "Maccabi",
    "מרקט בעיר אייזנברג מקס אי": "Market in the City",
    "מדנייט רחובות": "Midnight Rehovot",
    "הרצל בר קפה": "Herzl Bar Cafe",
    "כרטיס נטען מועדון": "Prepaid Club Card",
    "מכבי וייסגל": "Maccabi Weisgal",
    "SPIRIT FITNESS   BOUTIQUE": "Spirit Fitness Boutique",
    "אלונית - נען מזרח": "Alonit - Naan East",
    "סנאקס קיוסק הנשיא": "Snacks Kiosk HaNasi",
    "מינמרקט האחים טוויק בע\"מ": "Twik Brothers Mini Market Ltd.",
    "רשות הטבע והגנים - חוף פל": "Palmahim Beach",
    "הסתדרות מדיצינית הדסה": "Hadassah Medical",
    "סיבוס פלאקסי": "Sodexo Flexi",
    "הראל-ביטוח בריאות": "Harel - Health Insurance",
    "טיב טעם רשתות  רחובות": "Tiv Taam",
    "אשל חומרי בניין-צמרת": "Eshel Building Materials",
    "וויקום מובייל בע\"מ": "Wicom Mobile Ltd.",
    "הרצליה פיצוח": "Herzliya Nuts & Seeds",
    "כספומט לאומי    רחובות": "Leumi ATM Rehovot",
    "מכון דוידסון-צמרת": "Davidson Institute",
    "סיטי מרקט הרצל רחובות": "City Market Herzl Rehovot",
    "פליינג טייגר - סינימה ראש": "Flying Tiger - Cinema Rishon",
    "סינמה סיטי קיוסק": "Cinema City Kiosk",
    "נאייקס ישראל מכונות אוטומ": "Nayax Israel Vending Machines",
    "מקדונלד'ס ראשון לציון": "McDonald's Rishon LeZion",
    "ביחד בשבילך": "Together For You",
    "מגדל חיים/בריאות": "Migdal - Life/Health",
    "דור אלון פארק המדע": "Dor Alon Science Park",
    "כביש 6": "Route 6",
    "שטראוס מים בע\"מ הו\"ק": "Strauss Water",
    "חברת החשמל לישראל בע\"מ": "Israel Electric",
    "שטראוס מים בע\"מ": "Strauss Water",
    "מנורה מבטחים-חיים/בריאות": "Menorah Mivtachim - Life/Health",
    "סופרפארם שער רחובות": "Super-Pharm",
    "פנגו חשבונית חודשית": "Pango",
    "הראל ביטוח חיים": "Harel Life Insurance",
    "כלל ביטוח בריאות הוק": "Clal Health Insurance",
    "בזק הוראות קבע": "Bezeq Standing Order",
    "הפניקס ביטוח": "Phoenix Insurance",
    "הפניקס חיים ובריאות": "Phoenix Life and Health",
    "דמי כרטיס": "Card Fee",
    "שריקי'ס ש בע\"מ": "Shriky's Ltd.",
    "4CHEF": "4CHEF",
    "דוכן הפרדסן מקס איט ניכיו": "Dohan haPardes",
    "נייקי שנקר הרצליה": "Nike Shenkar Herzliya",
    "PAYBOX                 TEL AVIV      IL": "PayBox",
    "מקס פינוקים פלוס": "MAX Benefits Plus",
    "הוט סינמה רחובות": "HOT Cinema Rehovot",
    "בית מרקחת הנשיא": "HaNasi Pharmacy",
    "SEVEN EXPRESS": "Seven Express",
    "רכבת ישראל-רחובות (א' הדר": "Israel Railways",
    "רכבת ישראל-ת\"א האוניברסיט": "Israel Railways",
    "בית החולים הוטרינרי רחובו": "Veterinary",
    "פט בסט בע\"מ": "Pet Best",
    "עירית רחובות אינטרנט": "Rehovot Municipality",
    "הבאר השלישית.": "Beer haShilishit",
    "מחסני השוק  רחובות הנשיא": "Machsaney HaShuk",
    "מאכלי קייס": "Kais Foods",
    "בעל הבית - משלוחה": "Baal haBait - Delivery",
    "קונפידנס מערכות": "Konfidence Systems",
    "ארומה תל השומר": "Aroma Tel HaShomer",
    "שרות בוש/סימנס/קונסטרוקטה": "Bosch/Siemens",
    "משלוחה הזמנת אוכל אונליין": "Mislocha Food Delivery",
    "משלוחה - ריבר נודלס בר": "River Noodles Bar",
    "בנייני רובינשטיין בע\"מ": "Rubinstein Buildings Ltd.",
    "אלונית - נען מערב": "Alonit - Naan West",
    "מסעדת ברזיל הקטנה אילת": "Little Brazil Eilat",
    "סופר קלאב הוטל": "Super Club Hotel",
    "ריף כפר דולפינים באילת בע": "Dolphin Reef Eilat Ltd.",
    "ריף כפר הדולפינים באילת ב": "Dolphin Reef Eilat",
    "סופר פארם אילת קניון מול": "Super-Pharm",
    "מצפה תת ימי ים סוף בעמ חנ": "Coral World Underwater Observatory",
    "רי באר בע\"מ": "Re-Bar Ltd.",
    "ספרינט-מגדל סונול": "Sprint - Migdal Sonol",
    "ספרינט מוטורוס בע\"מ -  דר": "Sprint Motors",
    "שטיפת אמריקן סיטי": "American City Car Wash",
    "אוטלו רחובות": "Otello Rehovot",
    "טמבורית הנשיא": "Tamburit HaNasi",
    "חניון פארק ויצמן רחובות": "Weizmann Park Parking",
    "חניוני תל אביב": "Tel Aviv Parking Lots",
    "KSP רחובות": "KSP",
    "ארנק נטען מועדון ביחד בשב": "Prepaid Wallet - Together For You",
    "מילתא": "Milta",
    "CAFE NOOK": "Cafe Nook",
    "סופר פארם רוטשילד": "Super-Pharm",
    "מקדונלד'סWALLET-": "McDonalds Wallet",
    "מ.תחבורה - פנגו מוביט": "Pango Moovit",
    "רשות המיסים-מידע": "Israel Tax Authority - Info",
    # Add more if needed
}

df["Category_Eng"] = df["Category"].map(CATEGORY_TRANSLATIONS).fillna(df["Category"])
df["Business_Eng"] = df["Business"].map(BUSINESS_TRANSLATIONS).fillna(df["Business"])

# --- Filters ---
available_months = sorted(df["Month"].unique())
selected_month = st.selectbox("Select Month", available_months, index=len(available_months) - 1)
df_month = df[df["Month"] == selected_month]

# --- Plot Settings ---
FIG_SIZE = (14, 8)
TITLE_FONTSIZE = 18
LABEL_FONTSIZE = 14
TICK_FONTSIZE = 10

# --- Plot 1: Daily Scatter ---
st.subheader("Plot 1: Daily spending (scatter)")
plt.figure(figsize=FIG_SIZE)
plt.scatter(df_month["Date"], df_month["Amount"])
plt.title("Daily Spending", fontsize=TITLE_FONTSIZE)
plt.xlabel("Date", fontsize=LABEL_FONTSIZE)
plt.ylabel("Amount", fontsize=LABEL_FONTSIZE)
plt.xticks(rotation=45, fontsize=TICK_FONTSIZE)
plt.yticks(fontsize=TICK_FONTSIZE)
st.pyplot(plt)

# --- Plot 2: By Category ---
st.subheader("Plot 2: Spending by category")
category_sum = df_month.groupby("Category_Eng")["Amount"].sum().sort_values(ascending=False)
plt.figure(figsize=FIG_SIZE)
category_sum.plot(kind="bar")
plt.title("Spending by Category", fontsize=TITLE_FONTSIZE)
plt.ylabel("Amount", fontsize=LABEL_FONTSIZE)
plt.xticks(rotation=45, fontsize=TICK_FONTSIZE)
plt.yticks(fontsize=TICK_FONTSIZE)
st.pyplot(plt)

# --- Plot 3: By Business ---
st.subheader("Plot 3: Spending by business")
business_sum = df_month.groupby("Business_Eng")["Amount"].sum().sort_values(ascending=False).head(20)
plt.figure(figsize=FIG_SIZE)
business_sum.plot(kind="bar")
plt.title("Top 20 Businesses by Spending", fontsize=TITLE_FONTSIZE)
plt.ylabel("Amount", fontsize=LABEL_FONTSIZE)
plt.xticks(rotation=45, fontsize=TICK_FONTSIZE)
plt.yticks(fontsize=TICK_FONTSIZE)
st.pyplot(plt)

# --- Plot 4: By Card Number ---
st.subheader("Plot 4: Spending by card number")
card_sum = df_month.groupby("CardNumber")["Amount"].sum().sort_values(ascending=False)
# Handle card numbers robustly
card_sum.index = card_sum.index.astype(str).str.extract(r"(\d{4})")[0]
plt.figure(figsize=FIG_SIZE)
card_sum.plot(kind="bar")
plt.title("Spending by Card (Last 4 Digits)", fontsize=TITLE_FONTSIZE)
plt.xlabel("Card", fontsize=LABEL_FONTSIZE)
plt.ylabel("Amount", fontsize=LABEL_FONTSIZE)
plt.xticks(rotation=0, fontsize=TICK_FONTSIZE)
plt.yticks(fontsize=TICK_FONTSIZE)
st.pyplot(plt)