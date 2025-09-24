from __future__ import annotations

import sqlite3
from pathlib import Path

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

DB_PATH = Path(__file__).resolve().parent / "drink_orders.db"


@st.cache_resource(show_spinner=False)
def get_connection(path: str):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drink_name TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            memo TEXT,
            category TEXT,
            input_mode TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS order_shares (
            order_id INTEGER NOT NULL,
            participant_id INTEGER NOT NULL,
            PRIMARY KEY (order_id, participant_id),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (participant_id) REFERENCES participants(id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()


def fetch_participants(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT id, name FROM participants ORDER BY LOWER(name) COLLATE NOCASE"
    ).fetchall()
    return [dict(row) for row in rows]


def fetch_orders(conn: sqlite3.Connection) -> list[dict]:
    order_rows = conn.execute(
        "SELECT id, drink_name, unit_price, quantity, memo, category, input_mode FROM orders ORDER BY created_at"
    ).fetchall()

    share_rows = conn.execute(
        """
        SELECT os.order_id, p.id as participant_id, p.name
        FROM order_shares os
        JOIN participants p ON p.id = os.participant_id
        ORDER BY os.order_id, LOWER(p.name) COLLATE NOCASE
        """
    ).fetchall()

    share_map: dict[int, dict[str, list]] = {}
    for row in share_rows:
        entry = share_map.setdefault(row["order_id"], {"names": [], "ids": []})
        entry["names"].append(row["name"])
        entry["ids"].append(row["participant_id"])

    orders: list[dict] = []
    for row in order_rows:
        shares = share_map.get(row["id"], {"names": [], "ids": []})
        orders.append(
            {
                "id": row["id"],
                "drink_name": row["drink_name"],
                "unit_price": float(row["unit_price"]),
                "quantity": int(row["quantity"]),
                "memo": row["memo"] or "",
                "category": row["category"] or "",
                "input_mode": row["input_mode"] or "",
                "share_with": shares["names"],
                "share_with_ids": shares["ids"],
            }
        )

    return orders


def add_participant(conn: sqlite3.Connection, name: str) -> tuple[bool, str | None]:
    try:
        conn.execute("INSERT INTO participants(name) VALUES (?)", (name,))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "同じ名前の参加者がすでに存在します。"


def remove_participant(conn: sqlite3.Connection, participant_id: int) -> None:
    conn.execute("DELETE FROM participants WHERE id = ?", (participant_id,))
    # Clean up orders that no longer have any participants.
    conn.execute(
        """
        DELETE FROM orders
        WHERE id IN (
            SELECT o.id
            FROM orders o
            LEFT JOIN order_shares os ON o.id = os.order_id
            GROUP BY o.id
            HAVING COUNT(os.order_id) = 0
        )
        """
    )
    conn.commit()


def add_order(
    conn: sqlite3.Connection,
    *,
    drink_name: str,
    unit_price: float,
    quantity: int,
    memo: str,
    category: str,
    input_mode: str,
    participant_ids: list[int],
) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO orders (drink_name, unit_price, quantity, memo, category, input_mode)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (drink_name, unit_price, quantity, memo, category, input_mode),
    )
    order_id = cursor.lastrowid
    cursor.executemany(
        "INSERT INTO order_shares (order_id, participant_id) VALUES (?, ?)",
        [(order_id, pid) for pid in participant_ids],
    )
    conn.commit()


def refresh_data(conn: sqlite3.Connection) -> None:
    st.session_state.participants = fetch_participants(conn)
    st.session_state.orders = fetch_orders(conn)

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

    available_names = {p["name"] for p in st.session_state.get("participants", [])}
    if available_names:
        st.session_state.order_share_with = [
            name for name in st.session_state.order_share_with if name in available_names
        ]
    else:
        st.session_state.order_share_with = []

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

conn = get_connection(str(DB_PATH))
init_db(conn)
refresh_data(conn)

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
        conn.execute("DELETE FROM order_shares")
        conn.execute("DELETE FROM orders")
        conn.execute("DELETE FROM participants")
        conn.commit()
        refresh_data(conn)
        reset_order_inputs(st.session_state.get("order_input_mode", "自由入力"))
        st.success("データをリセットしました。")

st.subheader("参加者の管理")
with st.form("add_participant", clear_on_submit=True):
    new_participant = st.text_input("参加者名を入力", max_chars=30)
    add_participant = st.form_submit_button("参加者を追加")

if add_participant:
    name = new_participant.strip()
    if not name:
        st.warning("名前を入力してください。")
    else:
        success, error_msg = add_participant(conn, name)
        if success:
            refresh_data(conn)
            st.success(f"{name} を追加しました。")
        else:
            st.warning(error_msg or "参加者の追加に失敗しました。")

participants_data = st.session_state.participants
if participants_data:
    cols = st.columns(3)
    for idx, participant in enumerate(participants_data):
        col = cols[idx % len(cols)]
        name = participant["name"]
        participant_id = participant["id"]
        with col:
            st.markdown(f"- {name}")
            if st.button("削除", key=f"remove_{participant_id}"):
                remove_participant(conn, participant_id)
                refresh_data(conn)
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
    participant_names = [participant["name"] for participant in participants_data]
    st.multiselect(
        "割り勘する参加者",
        participant_names,
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
            name_to_id = {p["name"]: p["id"] for p in participants_data}
            try:
                participant_ids = [name_to_id[name] for name in share_with_value]
            except KeyError:
                st.error("参加者の取得に失敗しました。ページを更新してください。")
                participant_ids = []

            if participant_ids:
                add_order(
                    conn,
                    drink_name=drink_name_value,
                    unit_price=unit_price_value,
                    quantity=quantity_value,
                    memo=memo_value,
                    category=category_for_order,
                    input_mode=mode_label,
                    participant_ids=participant_ids,
                )
                refresh_data(conn)
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
    totals = {participant["name"]: 0.0 for participant in st.session_state.participants}
    for order in st.session_state.orders:
        total_price = order["unit_price"] * order["quantity"]
        if order["share_with"]:
            share = total_price / len(order["share_with"])
            for name in order["share_with"]:
                if name in totals:
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
