import streamlit as st
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. APP CONFIGURATION
# ==========================================
st.set_page_config(page_title="Baggage Inspection Task", page_icon="🛡️", layout="centered")

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if 'score' not in st.session_state: st.session_state.score = 0
if 'rounds' not in st.session_state: st.session_state.rounds = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'game_active' not in st.session_state: st.session_state.game_active = False
if 'current_bag' not in st.session_state: st.session_state.current_bag = []
if 'has_threat' not in st.session_state: st.session_state.has_threat = False
if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'mode' not in st.session_state: st.session_state.mode = "Manual"
if 'verification_result' not in st.session_state: st.session_state.verification_result = None

# ==========================================
# 3. ASSET LIBRARY
# ==========================================
SAFE_ITEMS = ['👕', '👖', '👗', '👟', '🎩', '💻', '📷', '📚', '🧸', '🥪', '🕶️']
THREAT_ITEMS = ['🔫', '🔪', '💣', '🧨', '🩸', '☠️']

# ==========================================
# 4. CORE FUNCTIONS
# ==========================================
def generate_bag():
    """PCG Engine: Creates a unique bag."""
    items = random.sample(SAFE_ITEMS, k=random.randint(4, 8))
    threat = False
    
    # Ground Truth Generation (30% Threat Probability)
    if random.random() < 0.30:
        items.append(random.choice(THREAT_ITEMS))
        threat = True
    
    random.shuffle(items)
    st.session_state.current_bag = items
    st.session_state.has_threat = threat
    st.session_state.start_time = time.time()

def process_decision(user_rejected):
    """Log User Decision."""
    rt = round(time.time() - st.session_state.start_time, 3)
    correct = (user_rejected == st.session_state.has_threat)
    result_str = "CORRECT" if correct else "ERROR"
    
    if correct: st.session_state.score += 10

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
    st.session_state.verification_result = None

# ==========================================
# 6. SYSTEM VERIFICATION (MONTE CARLO)
# ==========================================
def run_system_verification():
    """Automated Audit: Runs 10,000 trials."""
    logs = []
    print("Starting Monte Carlo Simulation...")
    
    progress_bar = st.progress(0)
    
    for i in range(10000):
        # 1. Simulate Ground Truth (30% Threat)
        is_threat = random.random() < 0.30
        
        # 2. Simulate AI Advice Logic
        ai_advice = "THREAT" if is_threat else "CLEAR"
        
        # Inject Error (15% Error Rate / 85% Reliability)
        is_ai_correct = True
        if random.random() > 0.85:
            is_ai_correct = False
            # Flip the advice
            ai_advice = "CLEAR" if ai_advice == "THREAT" else "THREAT"
            
        logs.append({
            "Trial": i,
            "Ground_Truth": is_threat,
            "AI_Advice": ai_advice,
            "AI_Correct": is_ai_correct
        })
        
        if i % 1000 == 0:
            progress_bar.progress(i / 10000)
            
    progress_bar.progress(100)
    st.session_state.verification_result = pd.DataFrame(logs)

# ==========================================
# 5. UI LAYOUT
# ==========================================
st.title("🛡️ Baggage Inspection Task")

# --- MAIN MENU ---
if not st.session_state.game_active and st.session_state.rounds == 0:
    
    # === [ADDED] MISSION BRIEFING SECTION ===
    st.markdown("### 📋 Mission Briefing")
    st.markdown("**Role:** Security Screening Officer | **Objective:** Detect prohibited items.")
    
    st.markdown("#### ⚠️ TARGET THREATS (LOOK FOR THESE):")
    # This creates the dark visual bar with emojis
    threat_html = " ".join([f"<span style='font-size:40px; margin:0 10px;'>{x}</span>" for x in THREAT_ITEMS])
    st.markdown(
        f"<div style='background-color: #262730; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>{threat_html}</div>", 
        unsafe_allow_html=True
    )
    
    st.info("⚡ **Performance Metric:** Both SPEED and ACCURACY are tracked.")
    st.
