
import io
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="رادار بازار ایران",
    page_icon="📊",
    layout="wide"
)

st.title("📊 رادار حرفه‌ای بازار ایران")
st.caption("نسخه اولیه — آزمایش اتصال به داده‌های واقعی بورس")

URL = "https://old.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0"

@st.cache_data(ttl=90)
def get_market_data():
    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )
    response.raise_for_status()
    return pd.read_excel(io.BytesIO(response.content))

if st.button("🔄 به‌روزرسانی داده‌های بازار"):
    get_market_data.clear()

st.write("زمان اجرای صفحه:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

try:
    with st.spinner("در حال دریافت اطلاعات از TSETMC..."):
        data = get_market_data()

    st.success(f"تعداد ردیف‌های دریافت‌شده: {len(data):,}")

    search = st.text_input("جست‌وجوی نماد یا نام شرکت")

    if search:
        mask = data.astype(str).apply(
            lambda col: col.str.contains(
                search, case=False, na=False
            )
        ).any(axis=1)
        data = data[mask]

    st.dataframe(data, use_container_width=True)

    st.download_button(
        "دانلود اطلاعات CSV",
        data=data.to_csv(index=False).encode("utf-8-sig"),
        file_name="market_data.csv",
        mime="text/csv"
    )

except Exception as error:
    st.error("دریافت داده از TSETMC موفق نشد.")
    st.write("ممکن است اتصال مسدود باشد یا قالب فایل تغییر کرده باشد.")
    st.code(str(error))
    st.info(
        "تا زمانی که دریافت داده واقعی تأیید نشده، "
        "این صفحه را مبنای معامله قرار ندهید."
    )
