import streamlit as st
import time
from datetime import datetime
import joblib
import numpy as np

# -----------------------------
# LOAD REAL ML MODEL
# -----------------------------
model = joblib.load("fraud_model.pkl")
scaler = joblib.load("scaler.pkl")

# -----------------------------
# SESSION STATE
# -----------------------------
if "balance" not in st.session_state:
    st.session_state.balance = 125.45

if "tx_history" not in st.session_state:
    st.session_state.tx_history = []

if "previous_destinations" not in st.session_state:
    st.session_state.previous_destinations = {}

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "otp_pending" not in st.session_state:
    st.session_state.otp_pending = False

if "otp_code" not in st.session_state:
    st.session_state.otp_code = None

if "otp_amount" not in st.session_state:
    st.session_state.otp_amount = 0

if "otp_to" not in st.session_state:
    st.session_state.otp_to = None

# -----------------------------
# REAL ML FUNCTION
# -----------------------------
def run_fraud_model(amount):
    X = np.zeros(30)
    X[-1] = amount
    X_scaled = scaler.transform(X.reshape(1, -1))
    prob = model.predict_proba(X_scaled)[0][1]
    return prob  # 0–1

# -----------------------------
# RULE ENGINE
# -----------------------------
def run_rule_engine(amount, balance, to_addr):
    rule_risk = 0
    reasons = []

    # Rule 1: Late night
    hour = datetime.now().hour
    if hour < 6 or hour >= 22:
        rule_risk += 0.15
        reasons.append("Late night transaction (+15%)")

    # Rule 2: Wallet drain %
    drain_ratio = amount / balance
    if drain_ratio > 0.8:
        rule_risk += 0.30
        reasons.append("Wallet drain > 80% (+30%)")
    elif drain_ratio >= 0.4:
        rule_risk += 0.20
        reasons.append("Wallet drain 40%–80% (+20%)")

    # Rule 3: New wallet
    if to_addr not in st.session_state.previous_destinations:
        rule_risk += 0.20
        reasons.append("New destination wallet (+20%)")

    # Rule 4: Frequency spike
    recent_tx_count = len(st.session_state.tx_history)
    if recent_tx_count >= 5:
        rule_risk += 0.15
        reasons.append("High transaction frequency (+15%)")

    # Rule 5: First-time big amount
    max_past = max(st.session_state.previous_destinations.values()) if st.session_state.previous_destinations else 0
    if amount > 30 and amount > max_past:
        rule_risk += 0.15
        reasons.append("First-time high amount (+15%)")

    return rule_risk, reasons

# -----------------------------
# FINAL ENGINE
# -----------------------------
def analyze_transaction(amount, balance, to_addr):
    ml_risk = run_fraud_model(amount)
    rule_risk, reasons = run_rule_engine(amount, balance, to_addr)

    final_risk = (0.6 * ml_risk) + (0.4 * rule_risk)

    # SAFETY OVERRIDE (rules must not be ignored)
    if rule_risk >= 0.4:
        final_risk = max(final_risk, rule_risk)

    if final_risk < 0.4:
        status = "VERIFIED"
    elif final_risk < 0.7:
        status = "REVIEW (OTP)"
    else:
        status = "FROZEN"

    return {
        "ml_risk": ml_risk,
        "rule_risk": rule_risk,
        "final_risk": final_risk,
        "status": status,
        "reasons": reasons
    }

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Smart Crypto Wallet", layout="centered")
st.title("🪙Crypto Fraud Detection System")

st.write("### Wallet Balance:", st.session_state.balance, "KAS")

to_addr = st.text_input("To Address")
amount = st.number_input("Amount", min_value=0.0)

# -----------------------------
# SEND BUTTON
# -----------------------------
if st.button("SEND"):
    if not to_addr:
        st.warning("Enter destination address")
    elif amount <= 0:
        st.warning("Enter valid amount")
    elif amount > st.session_state.balance:
        st.error("Insufficient balance")
    else:
        with st.spinner("Running fraud analysis..."):
            time.sleep(1)
            result = analyze_transaction(amount, st.session_state.balance, to_addr)

        # Save result
        st.session_state.last_result = result

        # Update memory
        st.session_state.tx_history.append(to_addr)
        if to_addr in st.session_state.previous_destinations:
            st.session_state.previous_destinations[to_addr] += amount
        else:
            st.session_state.previous_destinations[to_addr] = amount

        # Decision handling
        if result["status"] == "VERIFIED":
            st.session_state.balance -= amount
            st.rerun()

        elif result["status"] == "REVIEW (OTP)":
            otp = np.random.randint(1000, 9999)
            st.session_state.otp_pending = True
            st.session_state.otp_code = otp
            st.session_state.otp_amount = amount
            st.session_state.otp_to = to_addr
            st.info(f"OTP sent: {otp}")

        else:  # FROZEN
            st.warning("Transaction Frozen")

# -----------------------------
# OTP VERIFICATION BLOCK
# -----------------------------
if st.session_state.otp_pending:
    st.subheader("🔐 OTP Verification")
    user_otp = st.text_input("Enter OTP")

    if st.button("Verify OTP"):
        if user_otp == str(st.session_state.otp_code):
            st.success("OTP Verified. Transaction Completed!")

            # Deduct balance
            st.session_state.balance -= st.session_state.otp_amount

            # Clear OTP state
            st.session_state.otp_pending = False
            st.session_state.otp_code = None
            st.session_state.otp_amount = 0
            st.session_state.otp_to = None

            st.rerun()
        else:
            st.error("Wrong OTP. Transaction Frozen.")
            st.session_state.otp_pending = False

# -----------------------------
# DISPLAY RESULT
# -----------------------------
if st.session_state.last_result:
    result = st.session_state.last_result

    st.subheader("📊 Final Decision")
    st.metric("Final Fraud Risk", f"{result['final_risk']*100:.2f} %")
    st.write("Decision:", result["status"])

    st.subheader("🔍 How this score was calculated")
    st.write("ML Risk:", f"{result['ml_risk']*100:.2f} %")
    st.write("Rule Risk:", f"{result['rule_risk']*100:.2f} %")

    st.code(f"""
Final Risk = (0.6 × ML Risk) + (0.4 × Rule Risk)
           = (0.6 × {result['ml_risk']*100:.2f}) + (0.4 × {result['rule_risk']*100:.2f})
           = {result['final_risk']*100:.2f} %
""")

    st.subheader("🚩 Rules Triggered")
    for r in result["reasons"]:
        st.write("•", r)
