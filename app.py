
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="رادار بازار ایران",
    page_icon="📊",
    layout="wide"
)

BASE = "https://tindex.app/api/public"

st.title("📊 رادار حرفه‌ای بازار ایران")
st.caption("منبع داده: Tindex | قیمت‌ها به تومان، مگر آنکه واحد دیگری درج شده باشد")

@st.cache_data(ttl=60)
def get_data(path):
    token = st.secrets["TINDEX_API_TOKEN"]
    response = requests.get(
        f"{BASE}/{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        params={"lang": "en"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    if not payload.get("success"):
        raise ValueError(payload.get("message", "API request failed"))

    return payload.get("data")

def to_rows(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("rows", "rates", "items", "data"):
            if isinstance(data.get(key), list):
                return data[key]
        if all(isinstance(v, dict) for v in data.values()):
            return [
                {"slug": k, **v} for k, v in data.items()
            ]
    return []

def show_table(rows):
    if not rows:
        st.info("داده قابل نمایش در قالب جدول پیدا نشد.")
        return

    df = pd.DataFrame(rows)
    preferred = [
        "name", "price", "unit", "change",
        "updated_at", "slug"
    ]
    cols = [c for c in preferred if c in df.columns]
    if cols:
        df = df[cols].rename(columns={
            "name": "نام",
            "price": "قیمت",
            "unit": "واحد",
            "change": "تغییر روزانه (%)",
            "updated_at": "زمان به‌روزرسانی",
            "slug": "شناسه",
        })
    st.dataframe(df, use_container_width=True, hide_index=True)

try:
    metals = to_rows(get_data(
        "indicators/by-category/precious-metals"
    ))

    st.subheader("🥇 طلا، سکه و فلزات گران‌بها")

    important = {
        "gold-18k", "GOLD-24K", "emami-coin",
        "HALF-COIN", "QUARTER-COIN", "GERAMI-COIN",
        "xauusd", "SILVER-999", "xagusd"
    }

    selected = [
        row for row in metals
        if str(row.get("slug", "")).lower()
        in {s.lower() for s in important}
    ]

    if selected:
        show_table(selected)
    else:
        show_table(metals)

except Exception as e:
    st.error(f"خطا در دریافت اطلاعات طلا: {type(e).__name__}: {e}")

st.divider()
st.subheader("💱 نرخ ارز")

try:
    currencies = get_data("currency-rates")
    currency_rows = to_rows(currencies)

    if currency_rows:
        show_table(currency_rows)
    else:
        st.warning("پاسخ ارز دریافت شد، اما قالب آن هنوز برای جدول شناسایی نشده است.")
        st.json(currencies)

except Exception as e:
    st.error(f"خطا در دریافت نرخ ارز: {type(e).__name__}: {e}")

st.caption(
    "آخرین بارگذاری صفحه: "
    + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)
st.caption("داده‌ها از Tindex دریافت می‌شوند؛ پیش از معامله، قیمت و زمان به‌روزرسانی را بررسی کنید.")
