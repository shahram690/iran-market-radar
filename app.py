
import io
import traceback
from datetime import datetime

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="رادار حرفه‌ای بازار ایران",
    page_icon="📊",
    layout="wide",
)

st.title("📊 رادار حرفه‌ای بازار ایران")
st.caption(
    "نسخه آزمایشی — بررسی اتصال به داده‌های واقعی بورس تهران"
)

URL = (
    "https://old.tsetmc.com/"
    "tsev2/excel/MarketWatchPlus.aspx?d=0"
)

st.info(
    "این نسخه فقط اطلاعات دریافتی از منبع را نمایش می‌دهد. "
    "تا زمانی که داده‌ها تأیید نشده‌اند، "
    "از آن برای تصمیم معاملاتی استفاده نکنید."
)


@st.cache_data(ttl=90, show_spinner=False)
def get_market_data():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=(15, 45),
    )

    response.raise_for_status()

    if not response.content:
        raise ValueError("سرور فایل خالی برگردانده است.")

    try:
        data = pd.read_excel(
            io.BytesIO(response.content)
        )
    except Exception as exc:
        raise ValueError(
            "پاسخ سرور دریافت شد، اما فایل به‌صورت Excel "
            "قابل‌خواندن نیست. ممکن است ساختار منبع تغییر کرده "
            "یا به‌جای فایل، صفحه خطا دریافت شده باشد."
        ) from exc

    if data.empty:
        raise ValueError("فایل دریافت شد اما هیچ ردیفی ندارد.")

    return data


col1, col2 = st.columns(2)

with col1:
    st.write(
        "زمان اجرای صفحه:",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

with col2:
    if st.button("🔄 به‌روزرسانی داده‌های بازار"):
        get_market_data.clear()

search = st.text_input(
    "جست‌وجوی نماد یا نام شرکت",
    placeholder="مثلاً فولاد",
)

try:
    with st.spinner("در حال دریافت داده از TSETMC..."):
        data = get_market_data()

    st.success(
        f"دریافت موفق بود؛ تعداد ردیف‌ها: {len(data):,}"
    )

    st.write("ستون‌های فایل:", ", ".join(map(str, data.columns)))

    if search.strip():
        mask = data.astype(str).apply(
            lambda column: column.str.contains(
                search.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        data = data.loc[mask]

        st.write(f"تعداد نتایج جست‌وجو: {len(data):,}")

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="⬇️ دانلود اطلاعات CSV",
        data=data.to_csv(index=False).encode("utf-8-sig"),
        file_name="market_data.csv",
        mime="text/csv",
    )

except Exception as error:
    st.error("دریافت یا پردازش داده از TSETMC ناموفق بود.")

    st.subheader("نوع خطا")
    st.code(type(error).__name__)

    st.subheader("پیام خطا")
    st.code(repr(error))

    with st.expander("جزئیات فنی کامل", expanded=True):
        st.code(traceback.format_exc())

    st.warning(
        "این نسخه هنوز اتصال موفق به منبع داده را تأیید نکرده است. "
        "تا رفع خطا، اطلاعات آن را مبنای معامله قرار ندهید."
    )
