import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="🔍 学生指導用データベース", layout="wide")
st.title("🔍 学生指導用データベース")

# CSV読み込み
df = pd.read_csv("image7559.csv")

# 検索バー
query = st.text_input("問題文・選択肢・分類で検索:")

# 検索処理
if query:
    df_filtered = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]
else:
    df_filtered = df

st.info(f"{len(df_filtered)}件ヒットしました")

# ✅ CSV ダウンロード
csv_buffer = io.StringIO()
df_filtered.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 ヒット結果をCSVダウンロード",
    data=csv_buffer.getvalue(),
    file_name="filtered_results.csv",
    mime="text/csv"
)

# ✅ TEXT ダウンロード（整形）
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
    file_name="filtered_results.txt",
    mime="text/plain"
)

# 表示対象のレコードインデックス指定
index = st.number_input("表示するレコード番号:", min_value=0, max_value=len(df_filtered)-1, value=0, step=1)

# 対象レコードの抽出
record = df_filtered.iloc[index]

# 表示
st.markdown("### 🧪 問題文")
st.write(record["問題文"])

st.markdown("### ✏️ 選択肢")
for i in range(1, 6):
    if pd.notna(record.get(f"選択肢{i}", None)):
        st.write(f"- {record[f'選択肢{i}']}")

st.markdown(f"**✅ 正解:** {record['正解']}")

st.markdown(f"**📚 分類:** {record['科目分類']}")

# 🔗 画像リンク表示（正解の下）
st.markdown("### 🖼️ 画像リンク")
if pd.notna(record.get("リンクURL", None)) and str(record["リンクURL"]).strip() != "":
    st.markdown(f"[画像を表示]({record['リンクURL']})")
else:
    st.write("（画像リンクはありません）")
