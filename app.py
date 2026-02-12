import streamlit as st
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
# Sets the browser tab title and layout width
st.set_page_config(page_title="Baggage Inspection Task", page_icon="", layout="centered")

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
# Streamlit re-runs the script on every interaction. We use session_state
# to remember variables (score, current bag, game status) between clicks.

if 'score' not in st.session_state: st.session_state.score = 0
if 'rounds' not in st.session_state: st.session_state.rounds = 0
if 'history' not in st.session_state: st.session_state.history = []  # Stores data for CSV export
if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'current_bag' not in st.session_state: st.session_state.current_bag = []
if 'has_threat' not in st.session_state: st.session_state.has_threat = False
if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'mode' not in st.session_state: st.session_state.mode = "Manual"

# ==========================================
# 3. ASSET LIBRARY (SYMBOLIC DATASET)
# ==========================================
# Instead of static images, we use Unicode emojis.
# This allows for infinite procedural generation (PCG).
SAFE_ITEMS = ['👕', '👖', '👗', '👟', '🎩', '💻', '📷', '📚', '🧸', '🥪', '🕶️']
THREAT_ITEMS = ['🔫', '🔪', '💣', '🧨', '🩸', '☠️']

# ==========================================
# 4. CORE FUNCTIONS
# ==========================================

def generate_bag():
    """
    PROCEDURAL CONTENT GENERATION (PCG) ENGINE:
    Creates a unique bag for every trial to prevent 'Learning Effects'.
    """
    # 1. Randomly sample 4-8 safe items
    items = random.sample(SAFE_ITEMS, k=random.randint(4, 8))
    threat = False
    
    # 2. Inject a threat with 30% probability (Ground Truth)
    if random.random() < 0.30:
        items.append(random.choice(THREAT_ITEMS))
        threat = True
    
    # 3. Shuffle items so the threat isn't always in the same spot
    random.shuffle(items)
    
    # 4. Update State
    st.session_state.current_bag = items
    st.session_state.has_threat = threat
    st.session_state.start_time = time.time() # Start the reaction timer

def process_decision(user_rejected):
    """
    DATA LOGGING & SCORING:
    Calculates Reaction Time (RT) and Accuracy, then saves to history.
    """
    # Calculate Reaction Time (Current Time - Start Time)
    rt = round(time.time() - st.session_state.start_time, 2)
    
    # Check if user was correct (True Positive or True Negative)
    correct = (user_rejected == st.session_state.has_threat)
    result_str = "CORRECT" if correct else "ERROR"
    
    if correct: st.session_state.score += 10

    # Log data for the "Dissertation Dataset"
    st.session_state.history.append({
        "Round": st.session_state.rounds + 1,
        "Mode": st.session_state.mode,
        "Threat": st.session_state.has_threat, # Ground Truth
        "User_Reject": user_rejected,            # User Decision
        "Result": result_str,
        "Time": rt                               # Cognitive Load Metric
    })

    # Advance Round
    st.session_state.rounds += 1
    if st.session_state.rounds < 10:
        generate_bag() # Generate next trial
    else:
        st.session_state.game_active = False # End experiment

def restart_game():
    """Resets the experiment state for a new participant."""
    st.session_state.rounds = 0
    st.session_state.score = 0
    st.session_state.game_active = False

# ==========================================
# 5. UI LAYOUT
# ==========================================
st.title("Baggage Threat Detection System")

# ------------------------------------------
# SCREEN A: MAIN MENU & BRIEFING
# ------------------------------------------
if not st.session_state.game_active and st.session_state.rounds == 0:

    # Mission Briefing (Standardizing the participant mindset)
    st.markdown("### 🛡️ Mission Briefing")
    st.markdown("""
    **Role:** Security Screening Officer
    **Objective:** Inspect luggage X-rays for prohibited items.
    
    
    
    ("Please note that you are testing a prototype of an AI assistant for the security checks. It is meant to identify potential threats. Please examine the luggage and decide, based on your own judgment, whether it is safe or not")

    **⚠️ TARGET THREATS (LOOK FOR THESE):**
    """)

    # Display threat icons prominently
    st.markdown(
        f"<div style='font-size: 40px; text-align: center; background-color: #262730; padding: 10px; border-radius: 10px; margin-bottom: 20px;'>{' '.join(THREAT_ITEMS)}</div>",
        unsafe_allow_html=True
    )

    st.warning("⚡ Performance Metric: Both SPEED and ACCURACY are tracked.")
    st.divider()

    st.info("👇 Select your experimental protocol to begin:")

    # Protocol Selection Buttons
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

    # Dashboard: Show previous session data (if any exists)
    if len(st.session_state.history) > 0:
        st.divider()
        st.subheader("📊 Session Analytics")
        df = pd.DataFrame(st.session_state.history)

        # Visualization 1: Reaction Time (Cognitive Load)
        fig1, ax1 = plt.subplots(figsize=(6, 3))
        sns.barplot(data=df, x="Mode", y="Time", palette="viridis", ax=ax1)
        ax1.set_title("Average Reaction Time (Seconds)")
        st.pyplot(fig1)

        # Visualization 2: Accuracy
        acc_df = df.groupby("Mode")["Result"].apply(lambda x: (x == 'CORRECT').mean() * 100).reset_index()
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        sns.barplot(data=acc_df, x="Mode", y="Result", palette="magma", ax=ax2)
        ax2.set_title("Decision Accuracy (%)")
        ax2.set_ylabel("Accuracy %")
        ax2.set_ylim(0, 100)
        st.pyplot(fig2)

# ------------------------------------------
# SCREEN B: EXPERIMENT INTERFACE
# ------------------------------------------
elif st.session_state.game_active:
    st.progress(st.session_state.rounds / 10, f"Bag {st.session_state.rounds+1}/10")

    # Render the "X-Ray" Bag using HTML/CSS for styling
    bag_html = " ".join([f"<span style='font-size:55px; padding:10px;'>{x}</span>" for x in st.session_state.current_bag])
    st.markdown(f"<div style='background:#111; border:4px solid #444; border-radius:15px; padding:30px; text-align:center;'>{bag_html}</div>", unsafe_allow_html=True)

    # --- WIZARD OF OZ (AI SIMULATION) ---
    if st.session_state.mode == "AI_Assist":
        # 1. Determine the "Perfect" AI answer
        prediction = "THREAT" if st.session_state.has_threat else "CLEAR"
        
        # 2. Inject Stochastic Error (85% Reliability)
        # If random number > 0.85, flip the answer (create False Positive or False Negative)
        if random.random() > 0.85:
            prediction = "CLEAR" if prediction == "THREAT" else "THREAT"

        # 3. Display the AI Advice
        if prediction == "THREAT":
            st.error(f"🤖 AI ALERT: Suspicious Object Detected (Confidence: {random.randint(80,99)}%)", icon="⚠️")
        else:
            st.success(f"🤖 AI SCAN: No Suspicious Object Detected (Confidence: {random.randint(80,99)}%)", icon="✅")
    else:
        # Manual Mode Control Condition
        st.warning("📡 AI SYSTEM OFFLINE: Manual Inspection Required", icon="🛑")

    st.write("")
    
    # Decision Buttons
    c1, c2 = st.columns(2)
    if c1.button("✅ CLEAR BAG", type="primary", use_container_width=True): 
        process_decision(False) # False = User says NO Threat
        st.rerun()
    if c2.button("🚨 REPORT THREAT", type="primary", use_container_width=True): 
        process_decision(True)  # True = User says YES Threat
        st.rerun()

# ------------------------------------------
# SCREEN C: RESULTS & DATA EXPORT
# ------------------------------------------
else:
    st.success(f"🏁 Protocol Complete! Final Score: {st.session_state.score}")

    # Convert session history to Pandas DataFrame
    df = pd.DataFrame(st.session_state.history)

    st.subheader("📈 Performance Report")
    
    # Tab layout for charts
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

    # CSV Download Button for Data Collection Phase
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Full Dataset (CSV)", csv, "skyguard_data.csv", "text/csv")

    if st.button("🔄 Return to Main Menu"):
        restart_game()
        st.rerun()
