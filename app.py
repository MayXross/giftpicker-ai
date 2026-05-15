import anthropic
import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

load_dotenv()

# Page config
st.set_page_config(
    page_title="GiftPicker AI",
    page_icon="🎁",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

    .stApp {
        background: #faf9f7;
        font-family: 'DM Sans', sans-serif;
        font-size: 1.15rem;
    }
    .hero-wrap {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 28px;
        padding: 5rem 3rem 4rem;
        text-align: center;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255,200,100,0.08) 0%, transparent 50%),
                    radial-gradient(circle at 70% 30%, rgba(100,150,255,0.08) 0%, transparent 50%);
        pointer-events: none;
    }
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 4.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.75rem;
        letter-spacing: -1px;
    }
    .main-title span {
        color: #ffd166;
    }
    .subtitle {
        color: rgba(255,255,255,0.65);
        font-size: 1.5rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 400;
    }
    .gift-name {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .gift-reason {
        color: #666;
        font-size: 1.1rem;
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    .gift-price {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0f3460;
    }
    .gift-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #eeece8;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s;
    }
    .gift-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1a1a2e, #0f3460) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 1.1rem 2rem !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        font-family: 'DM Sans', sans-serif !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }
    .stTextInput label, .stSelectbox label, .stSlider label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #1a1a2e !important;
    }
    .stTextInput > div > div > input {
        border-radius: 12px !important;
        border: 1.5px solid #e5e2dc !important;
        background: #faf9f7 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0f3460 !important;
        box-shadow: 0 0 0 3px rgba(15,52,96,0.1) !important;
    }
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1.5px solid #e5e2dc !important;
        background: #faf9f7 !important;
        font-size: 1.1rem !important;
    }
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        color: #0f3460 !important;
        font-size: 1.1rem !important;
    }
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: #0f3460 !important;
        border-color: #0f3460 !important;
        width: 22px !important;
        height: 22px !important;
    }
    .stSlider [data-baseweb="slider"] > div > div:first-child {
        background: #0f3460 !important;
        height: 6px !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stSidebar {
        background: white !important;
        border-right: 1px solid #eeece8 !important;
        font-size: 1.05rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "request_count" not in st.session_state:
    st.session_state.request_count = 0
    st.session_state.reset_time = datetime.now() + timedelta(hours=1)
if "gifts" not in st.session_state:
    st.session_state.gifts = []
if "recipient" not in st.session_state:
    st.session_state.recipient = ""
if "budget" not in st.session_state:
    st.session_state.budget = ""

def check_rate_limit():
    if datetime.now() > st.session_state.reset_time:
        st.session_state.request_count = 0
        st.session_state.reset_time = datetime.now() + timedelta(hours=1)
    if st.session_state.request_count >= 10:
        st.error("Hourly limit reached. Please try again later.")
        return False
    return True

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Supported languages
LANGUAGES = [
    "English", "Slovak", "Czech", "German", "Spanish", "French",
    "Italian", "Portuguese", "Polish", "Hungarian", "Romanian",
    "Japanese", "Chinese", "Korean", "Arabic"
]

# Supported languages
LANGUAGES = [
    "English", "Slovak", "Czech", "German", "Spanish", "French",
    "Italian", "Portuguese", "Polish", "Hungarian", "Romanian",
    "Japanese", "Chinese", "Korean", "Arabic"
]

# Sidebar
with st.sidebar:
    st.markdown("### About GiftPicker AI")
    st.markdown("AI-powered gift finder. Enter who the gift is for, their interests and budget — get personalized ideas instantly.")
    st.divider()
    remaining = max(0, 10 - st.session_state.request_count)
    st.markdown("### 🔢 Requests left this hour")
    st.progress(remaining / 10)
    st.markdown(f"""
    <div style="text-align:center; font-size:2.5rem; font-weight:800; color:#0f3460;">
        {remaining}<span style="font-size:1rem; color:#999;">/10</span>
    </div>
    """, unsafe_allow_html=True)
    if remaining == 0:
        reset_in = st.session_state.reset_time - datetime.now()
        mins = int(reset_in.total_seconds() / 60)
        st.warning(f"⏱ Reset in ~{mins} min")
    st.divider()
    st.markdown("""
    <p style="font-size:11px; color:#999;">
    © 2026 GiftPicker AI
    </p>
    """, unsafe_allow_html=True)

amazon_store = "amazon.com"

# Header
st.markdown("""
<div class="hero-wrap">
    <div class="main-title">🎁 Gift<span>Picker</span> AI</div>
    <div class="subtitle">Find the perfect gift for anyone — in seconds</div>
</div>
""", unsafe_allow_html=True)

# Formular
col1, col2 = st.columns(2)
with col1:
    recipient = st.text_input("Who is the gift for?", placeholder="e.g. mom, boyfriend, teacher")
    interests = st.text_input("Their interests?", placeholder="e.g. cooking, travel, gaming")
with col2:
    budget = st.selectbox("Budget", ["Under $20", "Under $50", "Under $100", "Under $200", "Under $500", "$500+"])
    language = st.selectbox("🌍 Gift language", LANGUAGES)

category = st.selectbox("🎯 Gift category (optional)", [
    "Any category",
    "🎮 Electronics & Gaming",
    "👗 Fashion & Accessories",
    "🏠 Home & Decor",
    "📚 Books & Stationery",
    "🌿 Wellness & Beauty",
    "🍫 Food & Drinks",
    "🎨 Art & Crafts",
    "🏋️ Sports & Outdoors",
    "🧸 Toys & Games",
    "✈️ Travel & Experiences",
    "🎵 Music & Entertainment",
    "🐾 Pets",
])

occasion = st.selectbox("🎉 Occasion (optional)", [
    "Just a gift",
    "🎂 Birthday",
    "🎄 Christmas",
    "💝 Valentine's Day",
    "👩 Mother's Day",
    "👨 Father's Day",
    "🎓 Graduation",
    "💍 Wedding / Anniversary",
    "🏠 Housewarming",
    "👶 Baby Shower",
    "🎊 Retirement",
    "🤒 Get Well Soon",
    "🙏 Thank You",
])

gift_count = st.slider("🎁 How many gift ideas?", min_value=3, max_value=10, value=5, step=1)

st.divider()

# Generate
if st.button("🎁 Generate Gift Ideas"):
    if not check_rate_limit():
        st.stop()
    if recipient and interests:
        st.session_state.request_count += 1
        st.session_state.language = language
        st.session_state.occasion = occasion
        with st.spinner("Finding perfect gifts..."):
            try:
                category_text = f" in the category: {category}" if category != "Any category" else ""
                occasion_text = f" for the occasion: {occasion}" if occasion != "Just a gift" else ""
                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2500,
                    system=f"""You are an expert gift advisor.
                    Always respond in {language}.
                    Suggest exactly {gift_count} unique personalized gifts{category_text}{occasion_text}.
                    Also generate a short heartfelt dedication message for this occasion.
                    Respond ONLY in this exact JSON format, nothing else:
                    {{
                      "dedication": "A short heartfelt 1-2 sentence dedication message for {occasion}",
                      "gifts": [
                        {{
                          "name": "Product Name",
                          "reason": "Why perfect in one sentence",
                          "price": "$20-30",
                          "amazon_search": "exact search term",
                          "emoji": "one relevant emoji",
                          "category": "product category"
                        }}
                      ]
                    }}
                    Be SPECIFIC. ONLY valid JSON, no extra text.""",
                    messages=[{
                        "role": "user",
                        "content": f"Find {gift_count} gifts for: {recipient}, interests: {interests}, budget: {budget}{category_text}{occasion_text}"
                    }]
                )
                raw = message.content[0].text.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                result = json.loads(raw)
                gifts = result.get("gifts", result) if isinstance(result, dict) else result
                dedication = result.get("dedication", "") if isinstance(result, dict) else ""
                st.session_state.gifts = gifts
                st.session_state.dedication = dedication
                st.session_state.recipient = recipient
                st.session_state.budget = budget
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()
    else:
        st.warning("Please fill in all fields!")

# Vysledky
if st.session_state.gifts:
    st.markdown("### Your Gift Ideas")
    st.divider()

    # Zobraz venovanie ak existuje
    saved_dedication = st.session_state.get("dedication", "")
    if saved_dedication:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #0f3460); border-radius: 16px; 
                    padding: 1.5rem; margin-bottom: 1.5rem; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💌</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-bottom: 0.5rem;">Personal dedication</div>
            <div style="color: #ffd166; font-size: 1rem; font-style: italic;">"{saved_dedication}"</div>
        </div>
        """, unsafe_allow_html=True)

    affiliate = "giftpickera00-20"
    ebay_campaign = "5339153077"
    ebay_publisher = "7298517"
    saved_language = st.session_state.get("language", "English")

    for i, gift in enumerate(st.session_state.gifts):
        search = gift['amazon_search'].replace(' ', '+')
        amazon_url = f"https://{amazon_store}/s?k={search}&tag={affiliate}&language=en_US"
        ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={search}&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid={ebay_campaign}&customid=&toolid=10001&mkevt=1&pub={ebay_publisher}"

        with st.container():
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"""
                    <a href="{amazon_url}" target="_blank" style="text-decoration:none;">
                        <div style="font-size:80px; text-align:center; background:#f8f9ff;
                                    border-radius:16px; padding:20px; cursor:pointer;
                                    border:2px solid #e8eaff;">
                            {gift.get('emoji', '🎁')}
                        </div>
                        <p style="font-size:11px; color:#999; text-align:center; margin-top:5px;">
                            Click to shop
                        </p>
                    </a>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f'<div class="gift-name">🎁 {gift["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="gift-reason">💡 {gift["reason"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="gift-price">💰 {gift["price"]}</div>', unsafe_allow_html=True)
                st.link_button("🛒 View on Amazon", amazon_url)
                st.link_button("🛍️ View on eBay", ebay_url)

                if st.button("🔄 Show alternatives", key=f"alt_{i}"):
                    st.session_state[f"show_alt_{i}"] = True

            if st.session_state.get(f"show_alt_{i}"):
                with st.spinner("Finding alternatives..."):
                    gift_names = [g['name'] for g in st.session_state.gifts]
                    try:
                        alt_msg = client.messages.create(
                            model="claude-sonnet-4-6",
                            max_tokens=600,
                            system=f"""Gift advisor. Respond in {saved_language}.
                            Return 3 alternatives as JSON array:
                            [{{"name":"...","price":"...","amazon_search":"...","reason":"...","emoji":"..."}}]
                            ONLY valid JSON, no extra text.""",
                            messages=[{
                                "role": "user",
                                "content": f"3 alternatives to: {gift['name']} for: {st.session_state.recipient}, budget: {st.session_state.budget}, NOT these: {gift_names}"
                            }]
                        )
                        raw_alt = alt_msg.content[0].text.strip()
                        if raw_alt.startswith("```"):
                            raw_alt = raw_alt.split("```")[1]
                            if raw_alt.startswith("json"):
                                raw_alt = raw_alt[4:]
                        alts = json.loads(raw_alt)
                        st.markdown("**Alternatives:**")
                        for j, alt in enumerate(alts):
                            alt_s = alt['amazon_search'].replace(' ', '+')
                            alt_url = f"https://{amazon_store}/s?k={alt_s}&tag={affiliate}"
                            st.write(f"{alt.get('emoji','🎁')} **{alt['name']}** — {alt['price']}")
                            st.write(f"  {alt['reason']}")
                            st.link_button(f"🛒 {alt['name'][:25]}", alt_url, key=f"buy_{i}_{j}")
                    except Exception as e:
                        st.error(f"Could not load alternatives: {e}")

            st.divider()

# Footer
st.markdown("""
<div style="background:#f8f9ff; border-radius:12px; padding:1rem; margin-top:1rem;">
    <p style="font-size:12px; color:#999; text-align:center; margin:0;">
        <b>Affiliate Disclosure:</b> GiftPicker AI participates in the Amazon Associates Program 
        and eBay Partner Network. Links marked with 🛒 and 🛍️ are affiliate links. 
        If you make a purchase we may earn a small commission at no extra cost to you.<br><br>
        <b>Contact:</b> mayxross1@gmail.com
    </p>
</div>
""", unsafe_allow_html=True)
