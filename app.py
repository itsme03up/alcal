import streamlit as st
import pandas as pd

# メニュー情報: (ドリンク名, 価格) 価格が未設定の場合はNone
MENU_DATA = {
    "ビール": [
        ("アサヒスーパードライ生中", 638),
        ("ドライゼロ", 539),
        ("ノンアルコールビール", 539),
        ("ホッピーセット（白・黒）", 539),
        ("ホッピー中", 220),
        ("ホッピー外（白・黒）", 363),
    ],
    "ご当地サワー": [
        ("北海道ぶどうサワー", 539),
        ("青森県りんごサワー", 539),
        ("山形県白桃サワー", 539),
        ("高知県生姜おろしサワー", 539),
        ("宮崎県日向夏サワー", 539),
        ("福岡県あまおうサワー", 539),
        ("鹿児島県島みかんサワー", 539),
        ("沖縄県トマトサワー", 539),
    ],
    "サワー": [
        ("モンスターサワー", 590),
        ("黒い1800サワー", 690),
        ("レモンサワー", 649),
        ("最強レモンサワー", 649),
        ("生レモンサワー", 539),
        ("ガリガリ君サワー", 539),
        ("カルピスサワー", 539),
        ("サイダーサワー", 539),
        ("生グレープフルーツサワー", 539),
        ("梅干しサワー", 539),
        ("ドデカミンサワー", 539),
    ],
    "健康茶ハイ": [
        ("プーロン茶ハイ", 539),
        ("ウーロンハイ", 440),
        ("緑茶ハイ", 440),
        ("コーン茶ハイ", 440),
        ("平木さんの親友青汁ハイ", 539),
    ],
    "ハイボール": [
        ("ニッカフロンティアハイボール", 690),
        ("ふたごハイボール", 539),
        ("ジンジャーハイボール", 539),
        ("コーラハイボール", 539),
        ("ドデカミンハイボール", 539),
        ("最強レモンハイボール", 649),
    ],
    "ワイン・スパークリング": [
        ("はみ出るワイン（赤・白）", 649),
        ("ドンペリニヨン", 33000),
        ("カベルネソーヴィニヨンバロンフィリップ", 2959),
        ("カベルネソーヴィニヨン バロンフィリップ", 2690),
        ("シャルドネ バロンフィリップ", 2690),
        ("コレクション", 7990),
        ("ドンペリ祝", 30000),
    ],
    "果実酒": [
        ("濃醇梅酒", 539),
        ("あらごしみかん酒", 539),
        ("バナナ梅酒", 539),
    ],
    "韓国酒": [
        ("黒豆マッコリやかん", 1500),
        ("黒豆マッコリグラス", 490),
        ("セロ", 1400),
        ("セロ（プレミアム）", 1540),
        ("生マッコリやかん", 2200),
        ("マッコリやかん", 1650),
        ("マッコリグラス", 539),
    ],
    "焼酎・日本酒": [
        ("㐂六 ロック", 590),
        ("神の河 ロック", 590),
        ("かのか ロック", 530),
        ("黒霧島（グラス）", 605),
        ("黒霧島（ボトル）一升瓶", 6050),
        ("かのか（ボトル）", 583),
        ("中々（グラス）", 616),
        ("中々（ボトル）一升瓶", 6600),
        ("富乃宝山（グラス）", 649),
        ("富乃宝山（ボトル）一升瓶", 8800),
        ("八海山", 869),
    ],
    "ソフトドリンク": [
        ("モンスター", 390),
        ("ウーロン茶", 319),
        ("緑茶", 319),
        ("コーン茶", 319),
        ("プーロン茶", 319),
        ("平木さんの親友青汁", 319),
        ("オレンジジュース", 319),
        ("アップルジュース", 319),
        ("ジンジャエール", 319),
        ("ドデカミン", 319),
        ("三ツ矢サイダー", 319),
        ("カルピス", 319),
        ("俺じなるヨーグルト", 319),
    ],
}

ALL_MENU_ITEMS = [
    {"カテゴリー": category, "ドリンク": name, "価格": price}
    for category, items in MENU_DATA.items()
    for name, price in items
]

def trigger_rerun() -> None:
    """Streamlit rerun helper compatible with old/new APIs."""
    rerun_func = getattr(st, "experimental_rerun", None) or getattr(st, "rerun", None)
    if rerun_func is None:
        st.warning("このバージョンのStreamlitでは再描画がサポートされていません。")
        return
    rerun_func()

def initialize_order_state() -> None:
    """Ensure order input widgets have sensible defaults."""
    if "order_input_mode" not in st.session_state:
        st.session_state.order_input_mode = "メニューから選ぶ"

    first_category = next(iter(MENU_DATA), None)
    if "order_category" not in st.session_state:
        st.session_state.order_category = first_category or "自由入力"

    if "order_menu_index" not in st.session_state:
        st.session_state.order_menu_index = 0

    if "order_drink_name" not in st.session_state:
        st.session_state.order_drink_name = ""

    if "order_unit_price" not in st.session_state:
        st.session_state.order_unit_price = 0.0

    if "order_quantity" not in st.session_state:
        st.session_state.order_quantity = 1

    if "order_share_with" not in st.session_state:
        st.session_state.order_share_with = []

    if "order_memo" not in st.session_state:
        st.session_state.order_memo = ""

    if "_last_menu_selection" not in st.session_state:
        st.session_state._last_menu_selection = None

    if "_reset_order_pending" not in st.session_state:
        st.session_state._reset_order_pending = False
    if "_reset_order_mode" not in st.session_state:
        st.session_state._reset_order_mode = None

    if st.session_state._reset_order_pending:
        st.session_state.order_quantity = 1
        st.session_state.order_share_with = []
        st.session_state.order_memo = ""
        if st.session_state._reset_order_mode == "自由入力":
            st.session_state.order_drink_name = ""
            st.session_state.order_unit_price = 0.0
        st.session_state._reset_order_pending = False
        st.session_state._reset_order_mode = None
        st.session_state._last_menu_selection = None

    if MENU_DATA and st.session_state._last_menu_selection is None:
        # Align default drink name / price with current category selection.
        category = st.session_state.order_category
        items = MENU_DATA.get(category, [])
        if not items:
            for fallback_category, fallback_items in MENU_DATA.items():
                if fallback_items:
                    category = fallback_category
                    items = fallback_items
                    st.session_state.order_category = fallback_category
                    break
        if items:
            default_index = min(st.session_state.order_menu_index, len(items) - 1)
            name, price = items[default_index]
            st.session_state.order_menu_index = default_index
            st.session_state.order_drink_name = name
            if price is not None:
                st.session_state.order_unit_price = float(price)
            st.session_state._last_menu_selection = (category, default_index)

def reset_order_inputs(input_mode: str) -> None:
    """Reset order form inputs after successful submission."""
    st.session_state._reset_order_pending = True
    st.session_state._reset_order_mode = input_mode

st.set_page_config(page_title="飲み会ドリンク計算", layout="wide")

# Initialize persistent state
if "participants" not in st.session_state:
    st.session_state.participants = []
if "orders" not in st.session_state:
    st.session_state.orders = []

st.title("飲み放題じゃない時のドリンク割り勘ツール")
st.caption("参加者と注文を追加すると自動で金額を集計します。")

if ALL_MENU_ITEMS:
    with st.expander("ドリンクメニュー一覧", expanded=False):
        search_keyword = st.text_input(
            "メニュー検索",
            placeholder="例: レモン / ハイボール",
            key="menu_search_keyword",
        )
        menu_df = pd.DataFrame(ALL_MENU_ITEMS)
        if search_keyword:
            menu_df = menu_df[
                menu_df["ドリンク"].str.contains(search_keyword, case=False, na=False)
                | menu_df["カテゴリー"].str.contains(
                    search_keyword, case=False, na=False
                )
            ]
        menu_display_df = menu_df.copy()
        menu_display_df["価格(円)"] = menu_display_df["価格"].apply(
            lambda v: f"{int(v):,}" if isinstance(v, (int, float)) else "未設定"
        )
        menu_display_df.drop(columns="価格", inplace=True)
        st.dataframe(menu_display_df, use_container_width=True)

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
                trigger_rerun()
else:
    st.info("参加者を追加するとここに表示されます。")

st.subheader("注文の入力")
if not st.session_state.participants:
    st.warning("先に参加者を追加してください。")
else:
    initialize_order_state()

    input_mode = st.radio(
        "ドリンクの選択方法",
        ("メニューから選ぶ", "自由入力"),
        horizontal=True,
        key="order_input_mode",
    )

    category_for_order = "自由入力"

    if input_mode == "メニューから選ぶ" and MENU_DATA:
        category_options = list(MENU_DATA.keys())
        if st.session_state.order_category not in category_options:
            st.session_state.order_category = category_options[0]

        selected_category = st.selectbox(
            "カテゴリー",
            category_options,
            key="order_category",
        )

        menu_items = MENU_DATA.get(selected_category, [])
        if menu_items:
            if st.session_state.order_menu_index >= len(menu_items):
                st.session_state.order_menu_index = 0

            menu_labels = [
                f"{name} ({f'{price:,}円' if price is not None else '価格未設定'})"
                for name, price in menu_items
            ]
            st.selectbox(
                "ドリンク",
                list(range(len(menu_items))),
                key="order_menu_index",
                format_func=lambda idx: menu_labels[idx],
            )

            selected_index = st.session_state.order_menu_index
            drink_name, base_price = menu_items[selected_index]
            st.session_state.order_drink_name = drink_name

            current_selection = (selected_category, selected_index)
            if st.session_state._last_menu_selection != current_selection:
                st.session_state._last_menu_selection = current_selection
                st.session_state.order_unit_price = (
                    float(base_price) if base_price is not None else 0.0
                )

            st.number_input(
                "単価 (円)",
                min_value=0.0,
                step=10.0,
                key="order_unit_price",
                help="価格は必要に応じて調整できます。",
            )
            if base_price is None:
                st.info("このメニューは価格が未設定です。適切な単価を入力してください。")

            category_for_order = selected_category
        else:
            st.warning("このカテゴリーにはメニューがありません。手入力で登録してください。")
            st.session_state.order_drink_name = ""
            st.session_state.order_unit_price = 0.0
            st.number_input(
                "単価 (円)",
                min_value=0.0,
                step=10.0,
                key="order_unit_price",
            )
    else:
        if input_mode == "メニューから選ぶ" and not MENU_DATA:
            st.info("メニューが登録されていません。自由入力をご利用ください。")
        st.text_input("ドリンク名", max_chars=50, key="order_drink_name")
        st.number_input(
            "単価 (円)",
            min_value=0.0,
            step=10.0,
            key="order_unit_price",
        )
        category_for_order = "自由入力"

    st.number_input("杯数", min_value=1, step=1, key="order_quantity")
    st.multiselect(
        "割り勘する参加者",
        st.session_state.participants,
        key="order_share_with",
    )
    st.text_input("メモ (任意)", max_chars=60, key="order_memo")

    submitted = st.button("注文を記録", type="primary")

    if submitted:
        drink_name_value = st.session_state.order_drink_name.strip()
        unit_price_value = float(st.session_state.order_unit_price)
        quantity_value = int(st.session_state.order_quantity)
        share_with_value = st.session_state.order_share_with
        memo_value = st.session_state.order_memo.strip()
        mode_label = "メニュー" if input_mode == "メニューから選ぶ" else "自由入力"

        if not drink_name_value:
            st.warning("ドリンク名を入力または選択してください。")
        elif unit_price_value <= 0:
            st.warning("単価は0より大きい値にしてください。")
        elif not share_with_value:
            st.warning("割り勘する参加者を選択してください。")
        else:
            st.session_state.orders.append(
                {
                    "drink_name": drink_name_value,
                    "unit_price": unit_price_value,
                    "quantity": quantity_value,
                    "share_with": list(share_with_value),
                    "memo": memo_value,
                    "category": category_for_order,
                    "input_mode": mode_label,
                }
            )
            reset_order_inputs(input_mode)
            st.success(f"{drink_name_value} を記録しました。")

if st.session_state.orders:
    st.subheader("注文一覧")
    order_rows = []
    for idx, order in enumerate(st.session_state.orders, start=1):
        total_price = order["unit_price"] * order["quantity"]
        order_rows.append(
            {
                "#": idx,
                "カテゴリー": order.get("category", ""),
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
