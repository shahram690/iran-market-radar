
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Tindex API Test", layout="wide")
st.title("آزمایش اتصال به Tindex")
st.caption("منبع داده: Tindex API")

if st.button("آزمایش اتصال"):
    try:
        token = st.secrets["TINDEX_API_TOKEN"]

        url = (
            "https://tindex.app/api/public/"
            "indicators/by-category/precious-metals"
        )

        response = requests.get(
            url,
            params={"lang": "en"},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=20,
        )

        st.write("کد پاسخ سرور:", response.status_code)

        if response.status_code == 200:
            payload = response.json()

            if payload.get("success"):
                data = payload.get("data", {})
                rows = data.get("rows", []) if isinstance(data, dict) else data

                st.success("اتصال موفق است.")
                st.write("زمان آزمایش:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.write("تعداد ردیف‌های دریافتی:", len(rows))

                if rows:
                    st.json(rows)
                else:
                    st.warning("اتصال موفق بود، اما داده‌ای برنگشت.")
            else:
                st.error("API پاسخ ناموفق داده است.")
                st.json(payload)

        else:
            st.error("پاسخ API موفق نبود.")
            st.text(response.text[:1500])

    except KeyError:
        st.error("توکن TINDEX_API_TOKEN در Secrets پیدا نشد.")

    except requests.exceptions.Timeout:
        st.error("اتصال به Tindex بیش از ۲۰ ثانیه طول کشید.")

    except requests.exceptions.RequestException as e:
        st.error(f"خطای اتصال: {type(e).__name__}: {e}")

    except Exception as e:
        st.error(f"خطا: {type(e).__name__}: {e}")
