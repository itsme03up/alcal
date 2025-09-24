import streamlit as st
import pandas as pd

st.set_page_config(page_title="飲み会ドリンク計算", layout="wide")

# Initialize persistent state
if "participants" not in st.session_state:
    st.session_state.participants = []
if "orders" not in st.session_state:
    st.session_state.orders = []

st.title("飲み放題じゃない時のドリンク割り勘ツール")
st.caption("参加者と注文を追加すると自動で金額を集計します。")

with st.sidebar:
    st.header("リセット")
    if st.button("すべての入力をクリア", type="primary"):
        st.session_state.participants = []
        st.session_state.orders = []
        st.success("データをリセットしました。")

st.subheader("参加者の管理")
with st.form("add_participant", clear_on_submit=True):
    new_participant = st.text_input("参加者名を入力", max_chars=30)
    add_participant = st.form_submit_button("参加者を追加")

if add_participant:
    name = new_participant.strip()
    if not name:
        st.warning("名前を入力してください。")
    elif name in st.session_state.participants:
        st.warning("同じ名前の参加者がすでに存在します。")
    else:
        st.session_state.participants.append(name)
        st.success(f"{name} を追加しました。")

if st.session_state.participants:
    cols = st.columns(3)
    for idx, name in enumerate(st.session_state.participants):
        col = cols[idx % len(cols)]
        with col:
            st.markdown(f"- {name}")
            if st.button("削除", key=f"remove_{name}"):
                st.session_state.participants.remove(name)
                for order in st.session_state.orders:
                    if name in order["share_with"]:
                        order["share_with"].remove(name)
                st.experimental_rerun()
else:
    st.info("参加者を追加するとここに表示されます。")

st.subheader("注文の入力")
if not st.session_state.participants:
    st.warning("先に参加者を追加してください。")
else:
    with st.form("add_order", clear_on_submit=True):
        drink_name = st.text_input("ドリンク名", max_chars=50)
        unit_price = st.number_input("単価 (円)", min_value=0.0, step=50.0)
        quantity = st.number_input("杯数", min_value=1, step=1)
        share_with = st.multiselect("割り勘する参加者", st.session_state.participants)
        memo = st.text_input("メモ (任意)", max_chars=60)
        submitted = st.form_submit_button("注文を記録")

    if submitted:
        drink_name = drink_name.strip() or "ドリンク"
        if unit_price <= 0:
            st.warning("単価は0より大きい値にしてください。")
        elif not share_with:
            st.warning("割り勘する参加者を選択してください。")
        else:
            st.session_state.orders.append(
                {
                    "drink_name": drink_name,
                    "unit_price": unit_price,
                    "quantity": quantity,
                    "share_with": share_with,
                    "memo": memo.strip(),
                }
            )
            st.success(f"{drink_name} を記録しました。")

if st.session_state.orders:
    st.subheader("注文一覧")
    order_rows = []
    for idx, order in enumerate(st.session_state.orders, start=1):
        total_price = order["unit_price"] * order["quantity"]
        order_rows.append(
            {
                "#": idx,
                "ドリンク": order["drink_name"],
                "単価": order["unit_price"],
                "数量": order["quantity"],
                "合計金額": total_price,
                "人数": len(order["share_with"]),
                "割り勘する人": ", ".join(order["share_with"]),
                "メモ": order["memo"],
            }
        )

    order_df = pd.DataFrame(order_rows)
    st.dataframe(order_df, use_container_width=True)

    st.subheader("金額集計")
    totals = {name: 0.0 for name in st.session_state.participants}
    for order in st.session_state.orders:
        total_price = order["unit_price"] * order["quantity"]
        if order["share_with"]:
            share = total_price / len(order["share_with"])
            for name in order["share_with"]:
                totals[name] += share

    total_sum = sum(totals.values())
    totals_df = pd.DataFrame(
        {
            "参加者": list(totals.keys()),
            "支払い額": [round(amount, 2) for amount in totals.values()],
        }
    )
    totals_df.sort_values("支払い額", ascending=False, inplace=True)
    st.metric("合計金額 (円)", f"{total_sum:,.0f}")
    st.dataframe(totals_df, use_container_width=True)

    chart_df = totals_df.set_index("参加者")
    st.bar_chart(chart_df)

    st.download_button(
        "集計結果をCSVでダウンロード",
        data=totals_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="drink_totals.csv",
        mime="text/csv",
    )
else:
    st.info("注文が登録されると、ここに一覧と集計が表示されます。")
