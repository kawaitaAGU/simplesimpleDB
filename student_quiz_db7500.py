import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="🔍 学生指導用データベース", layout="wide")
st.title("🔍 学生指導用データベース")

# CSV読み込み
df = pd.read_csv("image7559.csv")

# 検索バー
query = st.text_input("問題文・選択肢・分類で検索:")

# 🔍 検索ヒントの表示
st.caption("💡 検索語を `&` でつなげるとAND検索ができます（例: レジン & 硬さ）")

# 🔍 AND検索対応
if query:
    keywords = [kw.strip() for kw in query.split("&") if kw.strip()]
    df_filtered = df[df.apply(
        lambda row: all(
            kw.lower() in row.astype(str).str.lower().str.cat(sep=" ")
            for kw in keywords
        ), axis=1)]
else:
    df_filtered = df

st.info(f"{len(df_filtered)}件ヒットしました")

# 🔤 タイムスタンプ + 検索語でファイル名作成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
safe_query = query if query else "検索なし"
file_prefix = f"{safe_query}{timestamp}"

# ✅ CSV ダウンロード
csv_buffer = io.StringIO()
df_filtered.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 ヒット結果をCSVダウンロード",
    data=csv_buffer.getvalue(),
    file_name=f"{file_prefix}.csv",
    mime="text/csv"
)

# ✅ TEXT ダウンロード
def format_record_to_text(row):
    parts = [f"問題文: {row['問題文']}"]
    for i in range(1, 6):
        choice = row.get(f"選択肢{i}", "")
        if pd.notna(choice):
            parts.append(f"選択肢{i}: {choice}")
    parts.append(f"正解: {row['正解']}")
    parts.append(f"分類: {row['科目分類']}")
    if pd.notna(row.get("リンクURL", "")) and str(row["リンクURL"]).strip() != "":
        parts.append(f"画像リンク: {row['リンクURL']}")
    return "\n".join(parts)

txt_buffer = io.StringIO()
for _, row in df_filtered.iterrows():
    txt_buffer.write(format_record_to_text(row))
    txt_buffer.write("\n\n" + "-"*40 + "\n\n")

st.download_button(
    label="📄 ヒット結果をTEXTダウンロード",
    data=txt_buffer.getvalue(),
    file_name=f"{file_prefix}.txt",
    mime="text/plain"
)

# ✅ インデックス指定表示
index = st.number_input("表示するレコード番号:", min_value=0, max_value=len(df_filtered)-1, value=0, step=1)
record = df_filtered.iloc[index]

# 🔗 画像リンク（問題文の上に）
st.markdown("### 🖼️ 画像リンク")
if pd.notna(record.get("リンクURL", None)) and str(record["リンクURL"]).strip() != "":
    st.markdown(f"[画像を表示]({record['リンクURL']})")
else:
    st.write("（画像リンクはありません）")

# ✅ 表示
st.markdown("### 🧪 問題文")
st.write(record["問題文"])

st.markdown("### ✏️ 選択肢")
for i in range(1, 6):
    if pd.notna(record.get(f"選択肢{i}", None)):
        st.write(f"- {record[f'選択肢{i}']}")

st.markdown(f"**✅ 正解:** {record['正解']}")
st.markdown(f"**📚 分類:** {record['科目分類']}")
