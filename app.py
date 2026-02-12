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

# DEBUG MESSAGE (If you see this, the app is running)
# st.write("✅ System Loaded Successfully") 

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
    st.rerun()

# ==========================================
# 6. SYSTEM VERIFICATION (MONTE CARLO)
# ==========================================
def run_system_verification():
    """Automated Audit: Runs 10,000 trials."""
    logs = []
    
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
    
    # === MISSION BRIEFING ===
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
    st.divider()

    # === MODE SELECTION ===
    st.markdown("### Select Operation Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("👤 **Participant Mode**")
        st.write("Start here to collect data.")
        if st.button("Start Manual Mode"):
            st.session_state.mode = "Manual"
            st.session_state.game_active = True
            generate_bag()
            st.rerun()
        if st.button("Start AI-Assisted Mode"):
            st.session_state.mode = "AI_Assist"
            st.session_state.game_active = True
            generate_bag()
            st.rerun()
            
    with col2:
        st.warning("⚙️ **Developer Mode**")
        st.write("For algorithmic verification.")
        if st.button("🛠️ Run System Verification"):
            run_system_verification()

    # --- VERIFICATION RESULTS DISPLAY ---
    if st.session_state.verification_result is not None:
        df_audit = st.session_state.verification_result
        
        st.divider()
        st.subheader("✅ System Verification Report")
        
        # Calculate Metrics
        total_trials = len(df_audit)
        ai_accuracy = (df_audit['AI_Correct'].mean()) * 100
        threat_rate = (df_audit['Ground_Truth'].mean()) * 100
        
        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trials", f"{total_trials:,}")
        m2.metric("AI Reliability", f"{ai_accuracy:.2f}%")
        m3.metric("Threat Rate", f"{threat_rate:.2f}%")
        
        # Validation Logic
        if 84.0 < ai_accuracy < 86.0:
            st.success("PASS: AI Reliability converges to target (85%).")
        else:
            st.error("FAIL: AI Reliability is drifting.")
            
        # Visualization
        fig, ax = plt.subplots(figsize=(6,2))
        sns.countplot(y=df_audit['AI_Correct'], palette="coolwarm", ax=ax)
        ax.set_title("AI Error Distribution")
        st.pyplot(fig)

# --- GAME LOOP ---
elif st.session_state.game_active:
    st.progress(st.session_state.rounds / 10, f"Bag {st.session_state.rounds+1}/10")
    
    # Bag Display
    bag_html = " ".join([f"<span style='font-size:55px; padding:10px;'>{x}</span>" for x in st.session_state.current_bag])
    st.markdown(f"<div style='background:#111; border:4px solid #444; border-radius:15px; padding:30px; text-align:center;'>{bag_html}</div>", unsafe_allow_html=True)

    # AI Logic (Wizard of Oz)
    if st.session_state.mode == "AI_Assist":
        prediction = "THREAT" if st.session_state.has_threat else "CLEAR"
        # 85% Reliability Check
        if random.random() > 0.85:
            prediction = "CLEAR" if prediction == "THREAT" else "THREAT"

        if prediction == "THREAT":
            st.error(f"🤖 AI ALERT: Threat Detected", icon="⚠️")
        else:
            st.success(f"🤖 AI SCAN: Bag Clear", icon="✅")

    c1, c2 = st.columns(2)
    if c1.button("✅ CLEAR"): 
        process_decision(False)
        st.rerun()
    if c2.button("🚨 THREAT"): 
        process_decision(True)
        st.rerun()

else:
    # --- END SCREEN ---
    st.success(f"Session Complete. Score: {st.session_state.score}")
    
    # Add Data Download
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Data (CSV)", csv, "data.csv", "text/csv")
    
    if st.button("Return to Menu"):
        restart_game()
