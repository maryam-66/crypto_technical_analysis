import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
import streamlit as st
import os

def run_sentiment_analysis(symbols, start_date=None, end_date=None):
    analyzer = SentimentIntensityAnalyzer()
    newsapi_key = "1fbbb3b298474644b2187f4a534484d4"

    all_data = []

    for symbol in symbols:
        url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&language=en&pageSize=5&apiKey={newsapi_key}"
        r = requests.get(url)
        if r.status_code != 200:
            st.warning(f"❌ خطا در دریافت اخبار {symbol}")
            continue

        articles = r.json().get("articles", [])
        st.info(f"📥 تعداد اخبار دریافت‌شده برای {symbol}: {len(articles)}")

        for article in articles:
            text = f"{article.get('title', '')}. {article.get('description', '')}"
            score = analyzer.polarity_scores(text)
            all_data.append({
                "symbol": symbol,
                "date": article.get("publishedAt", "")[:10],
                "title": article.get("title", ""),
                "compound": score['compound'],
                "pos": score['pos'],
                "neg": score['neg'],
                "neu": score['neu']
            })

    if not all_data:
        st.error("❌ هیچ خبری دریافت نشد.")
        return

    df = pd.DataFrame(all_data)
    st.success("✅ تحلیل احساسات با موفقیت انجام شد.")
    st.dataframe(df)

    # خلاصه آماری
    st.subheader("📊 میانگین احساسات کلی")
    avg_scores = df[['pos', 'neg', 'neu', 'compound']].mean()
    st.dataframe(avg_scores.to_frame("میانگین"))

    # نمودار میله‌ای احساسات
    st.subheader("📈 نمودار احساسات کلی")
    fig, ax = plt.subplots()
    avg_scores[['pos', 'neg', 'neu']].plot(kind='bar', ax=ax, color=['green', 'red', 'gray'])
    ax.set_ylabel("Average")
    ax.set_title("Sentiment")
    st.pyplot(fig)

    # خروجی Excel
    excel_buf = BytesIO()
    df.to_excel(excel_buf, index=False)
    st.download_button("⬇️ دانلود Excel", data=excel_buf.getvalue(), file_name="sentiment.xlsx")

    # خروجی PDF فارسی
    class PDF(FPDF): pass

    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", fname="DejaVuSans.ttf", uni=True)
    pdf.add_font("DejaVu", "B", fname="DejaVuSans-Bold.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)
    title = get_display(arabic_reshaper.reshape("Financial News Sentiment Analysis"))
    pdf.cell(200, 10, txt=title, ln=True, align="C")

    for symbol, group in df.groupby("symbol"):
        pdf.set_font("DejaVu", "B", size=12)
        pdf.ln(10)
        sym_txt = get_display(arabic_reshaper.reshape(f"نماد: {symbol}"))
        pdf.cell(0, 10, txt=sym_txt, ln=True)
        pdf.set_font("DejaVu", "", size=11)
        for _, row in group.iterrows():
            fa_title = get_display(arabic_reshaper.reshape(row['title']))
            date = row['date']
            compound = row['compound']
            sentiment_txt = get_display(arabic_reshaper.reshape(f"احساس کلی: {compound:.2f}"))
            pdf.multi_cell(0, 10, txt=f"{date}\n{fa_title}\n{sentiment_txt}\n")

        # نمودار احساسات
        fig, ax = plt.subplots()
        sentiments = group[['pos', 'neg', 'neu']].mean()
        ax.pie(sentiments, labels=['Positive', 'Negative', 'Neuter'], autopct='%1.1f%%')
        ax.axis('equal')
        chart_buf = BytesIO()
        plt.savefig(chart_buf, format='png')
        plt.close(fig)
        chart_path = f"{symbol}_chart.png"
        with open(chart_path, "wb") as f:
            f.write(chart_buf.getvalue())
        pdf.image(chart_path, w=100)
        os.remove(chart_path)

    pdf.output("report.pdf")
    with open("report.pdf", "rb") as f:
        st.download_button("⬇️ دانلود PDF", data=f.read(), file_name="sentiment_report.pdf")
