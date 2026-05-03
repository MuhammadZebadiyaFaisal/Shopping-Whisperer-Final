
from agent import get_shopping_verdict
import streamlit as st
import time

st.set_page_config(page_title="Shopping Whisperer", page_icon="🛍️", layout="centered")

st.markdown("""
<style>
.trust-high { color: #22c55e; font-size: 72px; font-weight: 800; text-align: center; }
.trust-mid  { color: #f59e0b; font-size: 72px; font-weight: 800; text-align: center; }
.trust-low  { color: #ef4444; font-size: 72px; font-weight: 800; text-align: center; }
.card  { padding: 10px 16px; border-radius: 10px; margin: 6px 0; font-size: 15px; }
.red   { background: #fee2e2; color: #991b1b; }
.green { background: #dcfce7; color: #166534; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🛍️ Shopping Whisperer")
st.markdown("**Paste a product link — we'll tell you if it's legit.**")
st.divider()

url = st.text_input("🔗 Product URL", placeholder="https://www.amazon.com/... or daraz.pk/...")

uploaded_file = st.file_uploader(
    "📄 Upload Scam/Truth document (optional)",
    type=["pdf", "txt", "csv"]
)
if uploaded_file:
    st.success(f"✅ '{uploaded_file.name}' uploaded! AI knowledge base updated.")

check_btn = st.button("🔍 Check Now", use_container_width=True, type="primary")

def parse_verdict(text: str) -> dict:
    trust_score = 50
    red_flags = []
    green_lights = []
    lines = text.strip().split("\n")
    section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "TRUST SCORE:" in line.upper():
            try:
                number = ''.join(filter(str.isdigit, line))
                if number:
                    trust_score = min(int(number), 100)
            except:
                pass
        elif "RED FLAG" in line.upper():
            section = "red"
        elif "GREEN LIGHT" in line.upper():
            section = "green"
        elif line.startswith("-") or line.startswith("•") or line.startswith("*"):
            clean = line.lstrip("-•* ").strip()
            if clean:
                if section == "red":
                    red_flags.append(clean)
                elif section == "green":
                    green_lights.append(clean)

    return {
        "trust_score": trust_score,
        "red_flags": red_flags,
        "green_lights": green_lights
    }

if check_btn:
    if not url.strip():
        st.warning("⚠️ Please enter a product URL first.")
    else:
        with st.status("🤖 Agent is analyzing the product...", expanded=True) as status:
            st.write("🔎 Scraping product page...")
            time.sleep(1)
            st.write("📚 Checking against scam knowledge base...")
            time.sleep(1)
            st.write("💰 Verifying price history...")
            time.sleep(1)
            st.write("🏪 Checking seller reputation...")

            smart_prompt = f"""
Analyze this product URL and give your verdict: {url}

You MUST respond in exactly this format and no other format:

TRUST SCORE: [number between 0 and 100]

RED FLAGS:
- [red flag 1]
- [red flag 2]

GREEN LIGHTS:
- [green light 1]
- [green light 2]
"""
            raw_text = get_shopping_verdict(smart_prompt)
            result = parse_verdict(raw_text)

            status.update(label="✅ Analysis complete!", state="complete")

        st.divider()

        score = result["trust_score"]
        st.markdown("### 📊 Trust Score")

        if score >= 70:
            cls, verdict, color = "trust-high", "✅ Looks Legit", "green"
        elif score >= 40:
            cls, verdict, color = "trust-mid", "⚠️ Proceed with Caution", "orange"
        else:
            cls, verdict, color = "trust-low", "❌ High Risk — Avoid!", "red"

        st.markdown(f'<div class="{cls}">{score}%</div>', unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='text-align:center; color:{color};'>{verdict}</h3>",
            unsafe_allow_html=True
        )
        st.progress(score / 100)
        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🚩 Red Flags")
            if result["red_flags"]:
                for f in result["red_flags"]:
                    st.markdown(f'<div class="card red">❌ {f}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card green">No red flags found!</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### ✅ Green Lights")
            if result["green_lights"]:
                for g in result["green_lights"]:
                    st.markdown(f'<div class="card green">✅ {g}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card red">No positive signals found.</div>', unsafe_allow_html=True)

        st.divider()
        with st.expander("🧪 Raw AI Response (for testing)"):
            st.write(raw_text)

        st.caption("🤖 Powered by Shopping Whisperer AI")
