
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
st.caption("نسخه آزمایشی اتصال به API بازار تهران")

URL = "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tsetmc.com/",
    "Origin": "https://www.tsetmc.com",
}

PARAMS = {
    "market": 0,
    "industrialGroup": "",
    "showTraded": "false",
    "withBestLimits": "false",
    "hEven": 0,
    "RefID": 0,
}

for i in range(9):
    PARAMS[f"paperTypes[{i}]"] = i + 1

st.write(
    "زمان اجرای صفحه:",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)

@st.cache_data(ttl=60, show_spinner=False)
def get_market_data():
    response = requests.get(
        URL,
        params=PARAMS,
        headers=HEADERS,
        timeout=(15, 30),
    )

    response.raise_for_status()

    try:
        result = response.json()
    except Exception as exc:
        raise ValueError(
            "پاسخ سرور JSON معتبر نیست. "
            f"نوع محتوا: {response.headers.get('Content-Type')}; "
            f"نمونه پاسخ: {response.text[:500]}"
        ) from exc

    if not isinstance(result, dict):
        raise ValueError(
            f"ساختار پاسخ غیرمنتظره است: {type(result).__name__}"
        )

    rows = result.get("marketwatch")

    if rows is None:
        raise ValueError(
            "کلید marketwatch در پاسخ وجود ندارد. "
            f"کلیدهای دریافتی: {list(result.keys())}"
        )

    if not rows:
        raise ValueError(
            "API پاسخ داده اما فهرست بازار خالی است. "
            f"کلیدهای پاسخ: {list(result.keys())}"
        )

    return pd.DataFrame(rows), result

if st.button("🔄 دریافت مجدد اطلاعات"):
    get_market_data.clear()

try:
    with st.spinner("در حال اتصال به API جدید TSETMC..."):
        data, raw_result = get_market_data()

    st.success(
        f"پاسخ دریافت شد؛ تعداد ردیف‌ها: {len(data):,}"
    )

    st.caption("ستون‌های دریافتی: " + ", ".join(map(str, data.columns)))

    search = st.text_input("جست‌وجوی نماد یا نام شرکت")

    if search.strip():
        mask = data.astype(str).apply(
            lambda col: col.str.contains(
                search.strip(),
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        data = data.loc[mask]

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇️ دانلود اطلاعات CSV",
        data=data.to_csv(index=False).encode("utf-8-sig"),
        file_name="market_watch.csv",
        mime="text/csv",
    )

except Exception as error:
    st.error("دریافت اطلاعات بازار ناموفق بود.")
    st.write("نوع خطا:")
    st.code(type(error).__name__)
    st.write("پیام خطا:")
    st.code(str(error))

    with st.expander("جزئیات فنی کامل"):
        st.code(traceback.format_exc())

    st.warning(
        "تا زمانی که داده واقعی دریافت و بررسی نشده، "
        "این صفحه را مبنای معامله قرار ندهید."
    )
