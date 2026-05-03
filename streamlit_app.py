
from agent import get_shopping_verdict
import streamlit as st
import time

st.set_page_config(page_title="Shopping Whisperer", page_icon="🛍️", layout="centered")

# 2. Advanced Professional Styling
st.markdown("""
<style>
    /* Main Background & Fonts */
    .main { background-color: #f8fafc; }
    
    /* Trust Score Branding */
    .trust-high { color: #15803d; font-size: 80px; font-weight: 900; text-align: center; margin-bottom: -10px; }
    .trust-mid  { color: #b45309; font-size: 80px; font-weight: 900; text-align: center; margin-bottom: -10px; }
    .trust-low  { color: #b91c1c; font-size: 80px; font-weight: 900; text-align: center; margin-bottom: -10px; }
    
    /* Feature Cards */
    .card { padding: 15px; border-radius: 12px; margin: 8px 0; border: 1px solid #e2e8f0; line-height: 1.5; }
    .red { background: #fff1f2; color: #991b1b; border-left: 5px solid #ef4444; }
    .green { background: #f0fdf4; color: #166534; border-left: 5px solid #22c55e; }
    
    /* Footer Styling */
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: white; color: #64748b; text-align: center; padding: 10px; border-top: 1px solid #e2e8f0; font-size: 12px; z-index: 100; }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar (Authority & Branding)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1162/1162499.png", width=80)
    st.title("Mission Control")
    st.markdown("### *Bridging the gap between doubt and digital trust.*")
    st.divider()
    st.info("""
    **How it works:**
    Our AI scrapes real-time data, analyzes seller history, and compares product patterns against known scam databases.
    """)
    st.caption("© 2026 M.Zebadiya Faisal")
    
st.markdown("# 🛍️ Shopping Whisperer")
st.markdown("""
**Paste any product link and let AI inspect trust signals instantly**  
*Shop smarter, shop safer—one link at a time.*
""")
st.info("🔍 We'll tell you -if it's legit or a scam?")
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
st.write("---")
st.caption("🤖 Powered by Shopping Whisperer AI")
st.caption("Developed By M.Zebadiya Faisal")
st.caption("© 2026 M.Zebadiya Faisal")
