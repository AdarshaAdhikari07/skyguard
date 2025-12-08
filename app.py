
import streamlit as st
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURATION ---
st.set_page_config(page_title="SkyGuard Analytics", page_icon="✈️", layout="centered")

# --- SESSION STATE INITIALIZATION ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'rounds' not in st.session_state: st.session_state.rounds = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'current_bag' not in st.session_state: st.session_state.current_bag = []
if 'has_threat' not in st.session_state: st.session_state.has_threat = False
if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'mode' not in st.session_state: st.session_state.mode = "Manual"

# --- ASSETS ---
SAFE_ITEMS = ['👕', '👖', '👗', '👟', '🎩', '💻', '📷', '📚', '🧸', '🥪', '🕶️']
THREAT_ITEMS = ['🔫', '🔪', '💣', '🧨', '🩸', '☠️']

# --- FUNCTIONS ---
def generate_bag():
    items = random.sample(SAFE_ITEMS, k=random.randint(4, 8))
    threat = False
    if random.random() < 0.30:
        items.append(random.choice(THREAT_ITEMS))
        threat = True
    random.shuffle(items)
    st.session_state.current_bag = items
    st.session_state.has_threat = threat
    st.session_state.start_time = time.time()

def process_decision(user_rejected):
    rt = round(time.time() - st.session_state.start_time, 2)
    correct = (user_rejected == st.session_state.has_threat)
    result_str = "CORRECT" if correct else "ERROR"
    if correct: st.session_state.score += 10

    # Save detailed history
    st.session_state.history.append({
        "Round": st.session_state.rounds + 1,
        "Mode": st.session_state.mode,
        "Threat": st.session_state.has_threat,
        "User_Reject": user_rejected,
        "Result": result_str,
        "Time": rt
    })

    st.session_state.rounds += 1
    if st.session_state.rounds < 10:
        generate_bag()
    else:
        st.session_state.game_active = False

def restart_game():
    st.session_state.rounds = 0
    st.session_state.score = 0
    st.session_state.game_active = False

# --- UI START ---
st.title("✈️ SkyGuard Security Interface")

# 1. MAIN MENU (UPDATED WITH MISSION BRIEFING)
if not st.session_state.game_active and st.session_state.rounds == 0:

    # --- NEW: PROFESSIONAL BRIEFING ---
    st.markdown("### 🛡️ Mission Briefing")
    st.markdown("""
    **Role:** Security Screening Officer
    **Objective:** Inspect luggage X-rays for prohibited items.

    **⚠️ TARGET THREATS (LOOK FOR THESE):**
    """)

    # Display the threats large and centered so users memorize them
    st.markdown(
        f"<div style='font-size: 40px; text-align: center; background-color: #262730; padding: 10px; border-radius: 10px; margin-bottom: 20px;'>{' '.join(THREAT_ITEMS)}</div>",
        unsafe_allow_html=True
    )

    st.warning("⚡ Performance Metric: Both SPEED and ACCURACY are tracked.")
    st.divider()

    st.info("👇 Select your experimental protocol to begin:")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛑 START MANUAL MODE", type="primary", use_container_width=True):
            st.session_state.mode = "Manual"
            st.session_state.game_active = True
            generate_bag()
            st.rerun()
    with col2:
        if st.button("🤖 START AI ASSIST MODE", type="primary", use_container_width=True):
            st.session_state.mode = "AI_Assist"
            st.session_state.game_active = True
            generate_bag()
            st.rerun()

    # Show previous data if exists
    if len(st.session_state.history) > 0:
        st.divider()
        st.subheader("📊 Session Analytics")
        df = pd.DataFrame(st.session_state.history)

        # CHART 1: REACTION TIME
        fig1, ax1 = plt.subplots(figsize=(6, 3))
        sns.barplot(data=df, x="Mode", y="Time", palette="viridis", ax=ax1)
        ax1.set_title("Average Reaction Time (Seconds)")
        st.pyplot(fig1)

        # CHART 2: ACCURACY
        # Calculate accuracy percentage per mode
        acc_df = df.groupby("Mode")["Result"].apply(lambda x: (x == 'CORRECT').mean() * 100).reset_index()
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        sns.barplot(data=acc_df, x="Mode", y="Result", palette="magma", ax=ax2)
        ax2.set_title("Decision Accuracy (%)")
        ax2.set_ylabel("Accuracy %")
        ax2.set_ylim(0, 100)
        st.pyplot(fig2)

# 2. GAME INTERFACE
elif st.session_state.game_active:
    st.progress(st.session_state.rounds / 10, f"Bag {st.session_state.rounds+1}/10")

    # X-Ray Display
    bag_html = " ".join([f"<span style='font-size:55px; padding:10px;'>{x}</span>" for x in st.session_state.current_bag])
    st.markdown(f"<div style='background:#111; border:4px solid #444; border-radius:15px; padding:30px; text-align:center;'>{bag_html}</div>", unsafe_allow_html=True)

    # AI Logic
    if st.session_state.mode == "AI_Assist":
        prediction = "THREAT" if st.session_state.has_threat else "CLEAR"
        # 15% Error Rate Logic
        if random.random() > 0.85:
            prediction = "CLEAR" if prediction == "THREAT" else "THREAT"

        if prediction == "THREAT":
            st.error(f"🤖 AI ALERT: Suspicious Object Detected (Confidence: {random.randint(80,99)}%)", icon="⚠️")
        else:
            st.success(f"🤖 AI SCAN: Bag Clear (Confidence: {random.randint(80,99)}%)", icon="✅")
    else:
        st.warning("📡 AI SYSTEM OFFLINE: Manual Inspection Required", icon="🛑")

    st.write("")
    c1, c2 = st.columns(2)
    if c1.button("✅ CLEAR BAG", type="primary", use_container_width=True): process_decision(False); st.rerun()
    if c2.button("🚨 REPORT THREAT", type="primary", use_container_width=True): process_decision(True); st.rerun()

# 3. RESULTS & CHARTS
else:
    st.success(f"🏁 Protocol Complete! Final Score: {st.session_state.score}")

    # Convert data to DataFrame
    df = pd.DataFrame(st.session_state.history)

    # --- AUTOMATIC CHART GENERATION ---
    st.subheader("📈 Performance Report")

    tab1, tab2 = st.tabs(["⏱️ Reaction Time", "🎯 Accuracy"])

    with tab1:
        st.markdown("**Average Time to Decide (Lower is faster)**")
        if not df.empty:
            fig, ax = plt.subplots()
            sns.barplot(data=df, x="Mode", y="Time", hue="Result", ax=ax)
            st.pyplot(fig)

    with tab2:
        st.markdown("**Accuracy by Mode**")
        if not df.empty:
            acc_chart = df.groupby("Mode")["Result"].apply(lambda x: (x == 'CORRECT').mean() * 100)
            st.bar_chart(acc_chart)

    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Full Dataset (CSV)", csv, "skyguard_data.csv", "text/csv")

    if st.button("🔄 Return to Main Menu"):
        restart_game()
        st.rerun()
