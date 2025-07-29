import streamlit as st
import pandas as pd
import io
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4

# ✅ フォント登録（プロジェクト内 fonts フォルダの IPAexGothic.ttf を使う）
pdfmetrics.registerFont(TTFont("Japanese", "fonts/IPAexGothic.ttf"))

# ✅ ページ設定
st.set_page_config(page_title="🔍 学生指導用データベース", layout="wide")
st.title("🔍 学生指導用データベース")

# ✅ データ読み込み
df = pd.read_csv("image7559.csv")

# ✅ 検索バーとヒント
query = st.text_input("問題文・選択肢・分類で検索:")
st.caption("💡 検索語を `&` でつなげるとAND検索ができます（例: レジン & 硬さ）")

# ✅ AND検索ロジック
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

# ✅ ファイル名の接頭辞作成
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
safe_query = query if query else "検索なし"
file_prefix = f"{safe_query}{timestamp}"

# ✅ CSVダウンロード
csv_buffer = io.StringIO()
df_filtered.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 ヒット結果をCSVダウンロード",
    data=csv_buffer.getvalue(),
    file_name=f"{file_prefix}.csv",
    mime="text/csv"
)

# ✅ TEXT整形
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

# ✅ TEXTダウンロード
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

# ✅ PDF生成関数
def create_pdf(records):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    c.setFont("Japanese", 12)
    width, height = A4
    y = height - 40

    for _, row in records.iterrows():
        text = format_record_to_text(row).split("\n")
        for line in text:
            c.drawString(40, y, line)
            y -= 18
            if y < 40:
                c.showPage()
                c.setFont("Japanese", 12)
                y = height - 40
        y -= 20  # レコード間スペース

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# ✅ PDFダウンロード
pdf_data = create_pdf(df_filtered)
st.download_button(
    label="📄 ヒット結果をPDFダウンロード",
    data=pdf_data,
    file_name=f"{file_prefix}.pdf",
    mime="application/pdf"
)

# ✅ インデックス表示
index = st.number_input("表示するレコード番号:", min_value=0, max_value=len(df_filtered)-1, value=0, step=1)
record = df_filtered.iloc[index]

# ✅ 個別表示（画像リンク → 問題文 → 選択肢）
st.markdown("### 🖼️ 画像リンク")
if pd.notna(record.get("リンクURL", None)) and str(record["リンクURL"]).strip() != "":
    st.markdown(f"[画像を表示]({record['リンクURL']})")
else:
    st.write("（画像リンクはありません）")

st.markdown("### 🧪 問題文")
st.write(record["問題文"])

st.markdown("### ✏️ 選択肢")
for i in range(1, 6):
    if pd.notna(record.get(f"選択肢{i}", None)):
        st.write(f"- {record[f'選択肢{i}']}")

st.markdown(f"**✅ 正解:** {record['正解']}")
st.markdown(f"**📚 分類:** {record['科目分類']}")
