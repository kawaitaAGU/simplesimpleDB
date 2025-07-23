import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="📘 学生指導用データベース", layout="wide")
st.title("🔍 学生指導用データベース")

# ✅ 決め打ちでCSVファイル読み込み（ローカルの8560sample.csv）
csv_path = "8560sample.csv"

try:
    df = pd.read_csv(csv_path)
    df.fillna("", inplace=True)
except FileNotFoundError:
    st.error(f"❌ ファイルが見つかりません: {csv_path}")
    st.stop()

# 🔍 検索ボックス
search = st.text_input("問題文・選択肢・分類で検索:", "")

# 🔎 検索処理
if search:
    filtered_df = df[df.apply(
        lambda row: search in str(row["問題文"]) or
                    any(search in str(row.get(f"選択肢{i}", "")) for i in range(1, 6)) or
                    search in str(row.get("科目分類", "")),
        axis=1)]
else:
    filtered_df = df

# 🔢 ヒット件数を表示
st.info(f"{len(filtered_df)} 件ヒットしました")

# ⚠️ ヒットなし
if filtered_df.empty:
    st.warning("該当するレコードがありません。")
    st.stop()

# 🔢 表示するレコード番号
record_idx = st.number_input("表示するレコード番号:", 0, len(filtered_df)-1, 0)

# 📄 該当レコードの取得
record = filtered_df.iloc[record_idx]

# 📌 表示内容
st.markdown("---")
st.markdown(f"### 🧪 問題文")
st.markdown(f"**{record['問題文']}**")

st.markdown("### ✏️ 選択肢")
for i in range(1, 6):
    label = f"選択肢{i}"
    if label in record and pd.notna(record[label]) and record[label].strip() != "":
        st.markdown(f"- {record[label]}")

st.markdown(f"### ✅ 正解: **{record.get('正解', 'N/A')}**")
st.markdown(f"### 🏷️ 分類: **{record.get('科目分類', 'N/A')}**")

# 💬 コメント欄
st.text_area("💬 コメントを記録", "")

# ----------------------------
# 💾 検索結果のダウンロード処理（Web対応）
# ----------------------------

# テキスト形式出力
def generate_txt(filtered_df):
    buffer = io.StringIO()
    for _, row in filtered_df.iterrows():
        buffer.write(f"問題文: {row['問題文']}\n")
        for i in range(1, 6):
            label = f"選択肢{i}"
            if label in row and pd.notna(row[label]) and row[label].strip():
                buffer.write(f"{label}: {row[label]}\n")
        buffer.write(f"正解: {row.get('正解', '')}\n")
        buffer.write(f"分類: {row.get('科目分類', '')}\n")
        buffer.write("-" * 40 + "\n")
    return buffer.getvalue()

# CSV形式出力
def generate_csv(filtered_df):
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    return csv_buffer.getvalue()

# ダウンロードボタン表示（検索語があるとき）
if search:
    st.markdown("### 💾 検索結果のダウンロード")
    today = datetime.now().strftime("%m%d")
    txt_data = generate_txt(filtered_df)
    csv_data = generate_csv(filtered_df)

    st.download_button(
        label="📥 ヒット結果を .txt でダウンロード",
        data=txt_data,
        file_name=f"{search}_{today}.txt",
        mime="text/plain"
    )

    st.download_button(
        label="📥 ヒット結果を .csv でダウンロード",
        data=csv_data,
        file_name=f"{search}_{today}.csv",
        mime="text/csv"
    )
