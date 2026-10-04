import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Crypto Mall", page_icon="₿", layout="wide")

# Crypto Mall V0.2 — Mock trading only; no real exchange connection or money.
st.title("₿ Crypto Mall")
st.caption("One place. Multiple exchanges. | V0.2 — Mock Trading")
st.warning("โหมดจำลองเท่านั้น: ราคา, สภาพคล่อง และกระเป๋าเงินเป็นข้อมูลทดลอง ไม่มีเงินจริงและไม่มีการส่งคำสั่งไปยัง Exchange")

MARKETS = {
    "BTC/THB": {
        "asset": "BTC",
        "Exchange A": {"bid": 3_099_000, "ask": 3_101_000, "fee": 0.25, "volume": 125.0},
        "Exchange B": {"bid": 3_094_000, "ask": 3_096_000, "fee": 0.20, "volume": 82.0},
        "Exchange C": {"bid": 3_107_000, "ask": 3_109_000, "fee": 0.15, "volume": 44.0},
    },
    "ETH/THB": {
        "asset": "ETH",
        "Exchange A": {"bid": 108_900, "ask": 109_100, "fee": 0.25, "volume": 920.0},
        "Exchange B": {"bid": 108_500, "ask": 108_700, "fee": 0.20, "volume": 610.0},
        "Exchange C": {"bid": 109_200, "ask": 109_400, "fee": 0.15, "volume": 380.0},
    },
}

if "wallet" not in st.session_state:
    st.session_state.wallet = {"THB": 1_000_000.0, "BTC": 0.0, "ETH": 0.0}
if "orders" not in st.session_state:
    st.session_state.orders = []

st.subheader("กระเป๋าเงินจำลอง")
w1, w2, w3 = st.columns(3)
w1.metric("THB คงเหลือ", f"฿{st.session_state.wallet['THB']:,.2f}")
w2.metric("BTC", f"{st.session_state.wallet['BTC']:.8f}")
w3.metric("ETH", f"{st.session_state.wallet['ETH']:.8f}")

st.divider()
market = st.selectbox("เลือกคู่เหรียญ", list(MARKETS))
market_data = MARKETS[market]
asset = market_data["asset"]
venues = list(k for k in market_data if k != "asset")

rows = []
for venue in venues:
    q = market_data[venue]
    mid = (q["bid"] + q["ask"]) / 2
    rows.append({
        "Exchange": venue,
        "Bid (ราคาขาย)": q["bid"],
        "Ask (ราคาซื้อ)": q["ask"],
        "Spread (%)": (q["ask"] - q["bid"]) / mid * 100,
        "Fee (%)": q["fee"],
        "Liquidity (จำลอง)": q["volume"],
    })
df = pd.DataFrame(rows)
best_buy = df.loc[df["Ask (ราคาซื้อ)"].idxmin()]
best_sell = df.loc[df["Bid (ราคาขาย)"].idxmax()]

st.subheader(f"Market Overview — {market}")
m1, m2, m3 = st.columns(3)
m1.metric("ราคาซื้อดีที่สุด", f"฿{best_buy['Ask (ราคาซื้อ)']:,.0f}", str(best_buy["Exchange"]))
m2.metric("ราคาขายดีที่สุด", f"฿{best_sell['Bid (ราคาขาย)']:,.0f}", str(best_sell["Exchange"]))
m3.metric("ส่วนต่างก่อนค่าธรรมเนียม", f"฿{best_sell['Bid (ราคาขาย)'] - best_buy['Ask (ราคาซื้อ)']:,.0f}")

st.dataframe(
    df.style.format({
        "Bid (ราคาขาย)": "฿{:,.0f}",
        "Ask (ราคาซื้อ)": "฿{:,.0f}",
        "Spread (%)": "{:.4f}%",
        "Fee (%)": "{:.2f}%",
        "Liquidity (จำลอง)": "{:,.1f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("ทดลองซื้อขาย (Paper Trading)")
side = st.radio("ประเภทคำสั่ง", ["Buy", "Sell"], horizontal=True)
venue = st.selectbox("เลือก Exchange", venues, key=f"venue_{market}")
quantity = st.number_input(f"จำนวน {asset}", min_value=0.0, value=0.001, step=0.001, format="%.8f")
quote = market_data[venue]
price = quote["ask"] if side == "Buy" else quote["bid"]
fee_rate = quote["fee"] / 100
gross = quantity * price
fee = gross * fee_rate
total_buy = gross + fee
net_sell = gross - fee

if side == "Buy":
    st.write(f"ราคาอ้างอิง: ฿{price:,.2f} / {asset}")
    st.write(f"มูลค่าซื้อ: ฿{gross:,.2f} | ค่าธรรมเนียมจำลอง: ฿{fee:,.2f}")
    st.write(f"ยอดที่ใช้ทั้งหมด: **฿{total_buy:,.2f}**")
    can_submit = quantity > 0 and st.session_state.wallet["THB"] >= total_buy
else:
    st.write(f"ราคาอ้างอิง: ฿{price:,.2f} / {asset}")
    st.write(f"มูลค่าขาย: ฿{gross:,.2f} | ค่าธรรมเนียมจำลอง: ฿{fee:,.2f}")
    st.write(f"ยอดรับสุทธิ: **฿{net_sell:,.2f}**")
    can_submit = quantity > 0 and st.session_state.wallet[asset] >= quantity

if st.button(f"ยืนยัน {side} {asset} (จำลอง)", type="primary", disabled=not can_submit):
    if side == "Buy":
        st.session_state.wallet["THB"] -= total_buy
        st.session_state.wallet[asset] += quantity
    else:
        st.session_state.wallet[asset] -= quantity
        st.session_state.wallet["THB"] += net_sell
    st.session_state.orders.insert(0, {
        "เวลา": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "คู่เหรียญ": market,
        "Side": side,
        "Exchange": venue,
        "จำนวน": quantity,
        "ราคา": price,
        "Fee (THB)": fee,
        "สถานะ": "Filled (จำลอง)",
    })
    st.success("ทำรายการจำลองสำเร็จ")
    st.rerun()

if side == "Buy" and st.session_state.wallet["THB"] < total_buy:
    st.info("ยอด THB ไม่เพียงพอสำหรับคำสั่งนี้")
if side == "Sell" and st.session_state.wallet[asset] < quantity:
    st.info(f"จำนวน {asset} ในกระเป๋าไม่เพียงพอ")

st.divider()
st.subheader("ประวัติคำสั่ง")
if st.session_state.orders:
    st.dataframe(pd.DataFrame(st.session_state.orders), use_container_width=True, hide_index=True)
else:
    st.caption("ยังไม่มีรายการซื้อขาย ลองส่งคำสั่งจำลองด้านบนได้เลย")

with st.expander("หมายเหตุและขั้นตอนถัดไป"):
    st.markdown(
        "- ข้อมูลราคาและค่าธรรมเนียมเป็นค่าตัวอย่างที่กำหนดไว้ในโค้ด\n"
        "- ข้อมูลกระเป๋าและประวัติอยู่ใน Streamlit session; รีสตาร์ตแอปหรือ session ใหม่อาจทำให้ข้อมูลทดลองหาย\n"
        "- V0.3: เชื่อมราคาสาธารณะจาก Exchange โดยยังไม่ส่งคำสั่งซื้อขายจริง\n"
        "- V0.4: คำนวณ Best Execution รวมค่าธรรมเนียมและขนาดคำสั่ง"
    )
