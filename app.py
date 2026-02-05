import streamlit as st
import pandas as pd
import math

# Page configuration
st.set_page_config(
    page_title="RC Section Design - ACI/ECP",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        margin-top: -2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.3rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="column"] {
        padding: 2px 5px !important;
    }
    .element-container {
        margin-bottom: 0px !important;
    }
    .katex {
        font-size: 0.95em;
    }
    </style>
""", unsafe_allow_html=True)

# Rebar data table
rebar_data = {
    6: [28.3, 57, 85, 113, 142, 170, 198, 226, 255],
    8: [50.3, 101, 151, 201, 252, 302, 352, 402, 453],
    10: [78.5, 157, 236, 314, 393, 471, 550, 628, 707],
    12: [113.1, 226, 339, 452, 565, 678, 791, 904, 1017],
    14: [153.9, 308, 461, 615, 769, 923, 1077, 1231, 1385],
    16: [201.1, 402, 603, 804, 1005, 1206, 1407, 1608, 1809],
    18: [254.5, 509, 763, 1017, 1272, 1527, 1781, 2036, 2290],
    20: [314.2, 628, 942, 1256, 1570, 1884, 2199, 2513, 2827],
    22: [380.1, 760, 1140, 1520, 1900, 2281, 2661, 3041, 3421],
    25: [490.9, 982, 1473, 1964, 2454, 2945, 3436, 3927, 4418],
    28: [615.8, 1232, 1847, 2463, 3079, 3695, 4310, 4926, 5542],
    32: [804.2, 1609, 2413, 3217, 4021, 4826, 5630, 6434, 7238],
    36: [1017.9, 2036, 3054, 4072, 5089, 6107, 7125, 8143, 9161],
    40: [1256.6, 2513, 3770, 5027, 6283, 7540, 8796, 10053, 11310],
    50: [1963.5, 3928, 5892, 7856, 9820, 11784, 13748, 15712, 17676]
}

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Default values
    st.session_state.fy = 420.0
    st.session_state.fcu = 25.0
    st.session_state.Mu = 100.0
    st.session_state.b = 250.0
    st.session_state.h = 500.0
    st.session_state.cover = 40.0
    st.session_state.phi = 0.90
    st.session_state.jd = 0.90
    st.session_state.beta1 = 0.85

# Reset function
def clear_all_inputs():
    st.session_state.fy = 0.0
    st.session_state.fcu = 0.0
    st.session_state.Mu = 0.0
    st.session_state.b = 0.0
    st.session_state.h = 0.0
    st.session_state.cover = 0.0
    st.session_state.phi = 0.0
    st.session_state.jd = 0.0
    st.session_state.beta1 = 0.0
    st.rerun()

# Title
st.markdown('<h1 class="main-header">🏗️ RC Section Design (ACI/ECP)</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Input Parameters")

# Design Code Selection
design_code = st.sidebar.radio(
    "🌍 Design Code",
    ["ACI 318", "Egyptian Code (ECP 203)"],
    help="Select the design code to use"
)

st.sidebar.markdown("---")

# Clear button
if st.sidebar.button("🗑️ Clear All Inputs", type="secondary", use_container_width=True):
    clear_all_inputs()

st.sidebar.markdown("---")

# Helper function for synchronized input
def sync_input(label, min_val, max_val, step, key, unit="", help_text=None):
    """Create synchronized number input and slider"""
    st.sidebar.markdown(f"**{label}** {unit}")
    
    col1, col2 = st.sidebar.columns([1, 1])
    
    with col1:
        num_val = st.number_input(
            f"{key}_num",
            min_value=min_val,
            max_value=max_val,
            value=st.session_state.get(key, min_val),
            step=step,
            key=f"{key}_number",
            label_visibility="collapsed",
            help=help_text
        )
    
    with col2:
        slider_val = st.slider(
            f"{key}_slider",
            min_value=min_val,
            max_value=max_val,
            value=st.session_state.get(key, min_val),
            step=step,
            key=f"{key}_slider",
            label_visibility="collapsed",
            help=help_text
        )
    
    # Sync logic
    if num_val != st.session_state.get(key, min_val):
        st.session_state[key] = num_val
        st.rerun()
    elif slider_val != st.session_state.get(key, min_val):
        st.session_state[key] = slider_val
        st.rerun()
    
    return st.session_state.get(key, min_val)

# Material Properties
st.sidebar.subheader("Material Properties")

fy = sync_input(
    "Steel Yield Strength, fy",
    0.0, 600.0, 10.0, "fy", "(MPa)",
    "Enter steel yield strength"
)

fcu = sync_input(
    "Concrete Strength, f'c / fcu",
    0.0, 50.0, 2.5, "fcu", "(MPa)",
    "Enter concrete compressive strength"
)

st.sidebar.markdown("---")

# Loading
st.sidebar.subheader("Loading")

Mu = sync_input(
    "Ultimate Moment, Mu",
    0.0, 500.0, 0.5, "Mu", "(kN.m)",
    "Enter ultimate design moment"
)

st.sidebar.markdown("---")

# Section Dimensions
st.sidebar.subheader("Section Dimensions")

b = sync_input(
    "Width, b",
    0.0, 2000.0, 50.0, "b", "(mm)",
    "Enter section width"
)

h = sync_input(
    "Height, h",
    0.0, 1000.0, 10.0, "h", "(mm)",
    "Enter total section height"
)

cover = sync_input(
    "Cover",
    0.0, 75.0, 5.0, "cover", "(mm)",
    "Enter concrete cover to reinforcement"
)

st.sidebar.markdown("---")

# Design Parameters
st.sidebar.subheader("Design Parameters")

if design_code == "ACI 318":
    phi = sync_input(
        "Strength Reduction Factor, φ",
        0.0, 0.9, 0.05, "phi", "",
        "ACI strength reduction factor (typically 0.9)"
    )
    
    jd = sync_input(
        "Moment Arm Factor, jd",
        0.0, 0.95, 0.01, "jd", "",
        "Approximate lever arm factor (d-a/2)/d"
    )
    
    beta1 = sync_input(
        "β₁ Factor",
        0.0, 0.85, 0.05, "beta1", "",
        "Stress block factor (typically 0.85 for f'c ≤ 28 MPa)"
    )
else:  # Egyptian Code
    # For Egyptian Code, we don't need phi, jd, beta1 in the same way
    st.sidebar.info("📘 Egyptian Code parameters are calculated automatically")

# Validation
all_inputs_valid = all([
    fy > 0,
    fcu > 0,
    Mu > 0,
    b > 0,
    h > 0,
    cover >= 0,
    h > cover,
])

if design_code == "ACI 318":
    all_inputs_valid = all_inputs_valid and phi > 0 and jd > 0 and beta1 > 0

if not all_inputs_valid:
    st.warning("⚠️ Please enter all input values to proceed with calculations")
    st.info("💡 Use the number inputs or sliders to set values")
    if h <= cover and h > 0 and cover > 0:
        st.error("❌ Height (h) must be greater than cover")
    st.stop()

# ==================== CALCULATIONS ====================

try:
    # Common calculations
    d = h - cover
    
    if d <= 0:
        st.error("❌ Error: Effective depth d = h - cover must be > 0")
        st.stop()
    
    Mu_Nmm = Mu * 1e6  # kN.m to N.mm
    
    calculations = []
    
    # ==================== ACI 318 CODE ====================
    if design_code == "ACI 318":
        # Step 1: Effective depth
        calculations.append({
            'step': '1',
            'description': 'Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': rf'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm',
            'variable': 'd'
        })
        
        # Step 2: Initial As
        denominator_initial = phi * fy * jd * d
        if denominator_initial == 0:
            st.error("❌ Error: φ * fy * jd * d cannot be zero")
            st.stop()
        
        As_initial = Mu_Nmm / denominator_initial
        
        calculations.append({
            'step': '2',
            'description': 'Initial As',
            'formula': r'A_s = \frac{M_u}{\phi f_y jd \cdot d}',
            'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times {jd:.2f} \times {d:.1f}}}',
            'result': f'{As_initial:.1f} mm²',
            'variable': 'As,init'
        })
        
        # Step 3: Depth of block
        denominator_a = 0.85 * fcu * b
        if denominator_a == 0:
            st.error("❌ Error: 0.85 * f'c * b cannot be zero")
            st.stop()
        
        a_initial = (As_initial * fy) / denominator_a
        
        calculations.append({
            'step': '3',
            'description': 'Depth of Block',
            'formula': r"a = \frac{A_s f_y}{0.85 f'_c b}",
            'substitution': rf'\frac{{{As_initial:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
            'result': f'{a_initial:.2f} mm',
            'variable': 'a'
        })
        
        # Step 4: Refined As
        lever_arm = d - a_initial/2
        if lever_arm <= 0:
            st.error("❌ Error: Lever arm (d - a/2) must be > 0")
            st.stop()
        
        As_calculated = Mu_Nmm / (phi * fy * lever_arm)
        
        calculations.append({
            'step': '4',
            'description': 'Refined As',
            'formula': r'A_s = \frac{M_u}{\phi f_y (d - a/2)}',
            'substitution': rf'\frac{{{Mu*1e6:.2e}}}{{{phi:.2f} \times {fy:.0f} \times ({d:.1f} - {a_initial/2:.2f})}}',
            'result': f'{As_calculated:.1f} mm²',
            'variable': 'As,calc'
        })
        
        # Step 5: Minimum steel
        As_min_1 = (0.25 * math.sqrt(fcu) / fy) * b * d
        As_min_2 = (1.4 / fy) * b * d
        As_min = max(As_min_1, As_min_2)
        
        calculations.append({
            'step': '5',
            'description': 'Minimum As',
            'formula': r'A_{s,min} = \max\left(\frac{0.25\sqrt{f_c^\prime}}{f_y}b_w d, \frac{1.4}{f_y}b_w d\right)',
            'substitution': rf'\max\left(\frac{{0.25 \times {math.sqrt(fcu):.2f}}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}, \frac{{1.4}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}\right)',
            'result': f'{As_min:.1f} mm²',
            'variable': 'As,min'
        })
        
        # Step 6: Required As
        As_required = max(As_calculated, As_min)
        governing = "minimum" if As_required == As_min else "calculated"
        
        calculations.append({
            'step': '6',
            'description': 'Required As',
            'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
            'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing})',
            'variable': 'As,req'
        })
        
        # Step 7: Final a
        a_final = (As_required * fy) / denominator_a
        
        calculations.append({
            'step': '7',
            'description': 'Final a',
            'formula': r"a = \frac{A_{s,req} f_y}{0.85 f'_c b}",
            'substitution': rf'\frac{{{As_required:.1f} \times {fy:.0f}}}{{0.85 \times {fcu:.1f} \times {b:.0f}}}',
            'result': f'{a_final:.2f} mm',
            'variable': 'a,final'
        })
        
        # Step 8: Neutral axis
        c = a_final / beta1
        
        calculations.append({
            'step': '8',
            'description': 'Neutral Axis',
            'formula': r'c = \frac{a}{\beta_1}',
            'substitution': rf'\frac{{{a_final:.2f}}}{{{beta1:.2f}}}',
            'result': f'{c:.2f} mm',
            'variable': 'c'
        })
        
        # Step 9: Steel strain
        if c <= 0:
            st.error("❌ Error: Neutral axis depth c must be > 0")
            st.stop()
        
        es = ((d - c) / c) * 0.003
        
        calculations.append({
            'step': '9',
            'description': 'Steel Strain',
            'formula': r'\varepsilon_s = \frac{d-c}{c} \times 0.003',
            'substitution': rf'\frac{{{d:.1f} - {c:.2f}}}{{{c:.2f}}} \times 0.003',
            'result': f'{es:.5f}',
            'variable': 'εs'
        })
        
        # Step 10: Check strain
        strain_safe = es >= 0.002
        if es >= 0.005:
            strain_status = "Tension ✓"
        elif es >= 0.002:
            strain_status = "Transition ⚠"
        else:
            strain_status = "Compression ✗"
        
        calculations.append({
            'step': '10',
            'description': 'Check εs',
            'formula': r'\varepsilon_s \geq 0.002',
            'substitution': f'{es:.5f} ≥ 0.002',
            'result': f'{"PASS ✓" if strain_safe else "FAIL ✗"} ({strain_status})',
            'variable': 'Check'
        })
        
        # Step 11: Design capacity
        phi_Mn_Nmm = phi * As_required * fy * (d - a_final/2)
        phi_Mn = phi_Mn_Nmm / 1e6
        
        calculations.append({
            'step': '11',
            'description': 'Design Capacity',
            'formula': r'\phi M_n = \phi A_{s,req} f_y (d - a/2)',
            'substitution': rf'{phi:.2f} \times {As_required:.1f} \times {fy:.0f} \times ({d:.1f} - {a_final/2:.2f})',
            'result': f'{phi_Mn:.2f} kN.m',
            'variable': 'φMn'
        })
        
        # Step 12: Capacity check
        capacity_safe = phi_Mn >= Mu
        utilization = (Mu / phi_Mn) * 100 if phi_Mn > 0 else 0
        
        calculations.append({
            'step': '12',
            'description': 'Capacity Check',
            'formula': r'\phi M_n \geq M_u',
            'substitution': f'{phi_Mn:.2f} ≥ {Mu:.2f}',
            'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
            'variable': 'Check'
        })
    
    # ==================== EGYPTIAN CODE ====================
    else:  # Egyptian Code (ECP 203)
        # Step 1: Effective depth
        calculations.append({
            'step': '1',
            'description': 'Effective Depth',
            'formula': r'd = h - \text{cover}',
            'substitution': rf'{h:.0f} - {cover:.0f}',
            'result': f'{d:.1f} mm',
            'variable': 'd'
        })
        
        # Step 2: Calculate C1
        # C1 = J / √(fcu * b)
        # But we need to find J first through iteration
        # Let's assume initial J for C1 calculation
        
        # Step 2a: Calculate C1 from Mu
        # Mu = fcu * b * d² * C1
        # C1 = Mu / (fcu * b * d²)
        
        C1_from_moment = Mu_Nmm / (fcu * b * d * d)
        
        calculations.append({
            'step': '2',
            'description': 'Calculate C₁',
            'formula': r'C_1 = \frac{M_u}{f_{cu} \cdot b \cdot d^2}',
            'substitution': rf'\frac{{{Mu_Nmm:.2e}}}{{{fcu:.1f} \times {b:.0f} \times {d:.1f}^2}}',
            'result': f'{C1_from_moment:.4f}',
            'variable': 'C₁'
        })
        
        # Step 3: Check C1 minimum
        C1_min = 2.76
        C1_check = C1_from_moment <= C1_min
        
        calculations.append({
            'step': '3',
            'description': 'Check C₁',
            'formula': r'C_1 \leq C_{1,min} = 2.76',
            'substitution': f'{C1_from_moment:.4f} ≤ {C1_min}',
            'result': f'{"PASS ✓" if C1_check else "FAIL ✗ (Over-reinforced)"}',
            'variable': 'Check'
        })
        
        # Step 4: Calculate J (lever arm factor)
        # J = (1/1.15) * (0.5 + √(0.25 - 1/(0.9 * C1²)))
        
        discriminant = 0.25 - 1/(0.9 * C1_from_moment * C1_from_moment)
        
        if discriminant < 0:
            st.error("❌ Error: Section is over-reinforced. Reduce moment or increase section size.")
            st.stop()
        
        J_calculated = (1/1.15) * (0.5 + math.sqrt(discriminant))
        
        calculations.append({
            'step': '4',
            'description': 'Calculate J',
            'formula': r'J = \frac{1}{1.15} \left(0.5 + \sqrt{0.25 - \frac{1}{0.9 \cdot C_1^2}}\right)',
            'substitution': rf'\frac{{1}}{{1.15}} \left(0.5 + \sqrt{{0.25 - \frac{{1}}{{0.9 \times {C1_from_moment:.4f}^2}}}}\right)',
            'result': f'{J_calculated:.4f}',
            'variable': 'J'
        })
        
        # Step 5: J max check
        J_max = 0.95
        J_used = min(J_calculated, J_max)
        
        calculations.append({
            'step': '5',
            'description': 'Check J max',
            'formula': r'J \leq J_{max} = 0.95',
            'substitution': f'{J_calculated:.4f} ≤ {J_max}',
            'result': f'{J_used:.4f} ({"used" if J_used == J_calculated else "limited to J_max"})',
            'variable': 'J_used'
        })
        
        # Step 6: Calculate required As
        # As = Mu / (fy * J * d)
        
        As_calculated = Mu_Nmm / (fy * J_used * d)
        
        calculations.append({
            'step': '6',
            'description': 'Calculate As',
            'formula': r'A_s = \frac{M_u}{f_y \cdot J \cdot d}',
            'substitution': rf'\frac{{{Mu_Nmm:.2e}}}{{{fy:.0f} \times {J_used:.4f} \times {d:.1f}}}',
            'result': f'{As_calculated:.1f} mm²',
            'variable': 'As,calc'
        })
        
        # Step 7: Minimum steel (Egyptian Code)
        # As,min = 0.6/fy * b * d (for grade 360/520)
        # or As,min = 0.225 * √fcu / fy * b * d
        
        As_min_1 = (0.6 / fy) * b * d
        As_min_2 = (0.225 * math.sqrt(fcu) / fy) * b * d
        As_min = max(As_min_1, As_min_2)
        
        calculations.append({
            'step': '7',
            'description': 'Minimum As (ECP)',
            'formula': r'A_{s,min} = \max\left(\frac{0.6}{f_y}bd, \frac{0.225\sqrt{f_{cu}}}{f_y}bd\right)',
            'substitution': rf'\max\left(\frac{{0.6}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}, \frac{{0.225 \times {math.sqrt(fcu):.2f}}}{{{fy:.0f}}} \times {b:.0f} \times {d:.1f}\right)',
            'result': f'{As_min:.1f} mm²',
            'variable': 'As,min'
        })
        
        # Step 8: Required As
        As_required = max(As_calculated, As_min)
        governing = "minimum" if As_required == As_min else "calculated"
        
        calculations.append({
            'step': '8',
            'description': 'Required As',
            'formula': r'A_{s,req} = \max(A_s, A_{s,min})',
            'substitution': rf'\max({As_calculated:.1f}, {As_min:.1f})',
            'result': f'{As_required:.1f} mm² ({governing})',
            'variable': 'As,req'
        })
        
        # Step 9: Calculate actual neutral axis
        # x = As * fy / (0.67 * fcu * b)  (for Egyptian Code)
        
        x = (As_required * fy) / (0.67 * fcu * b)
        
        calculations.append({
            'step': '9',
            'description': 'Neutral Axis Depth',
            'formula': r'x = \frac{A_s \cdot f_y}{0.67 \cdot f_{cu} \cdot b}',
            'substitution': rf'\frac{{{As_required:.1f} \times {fy:.0f}}}{{0.67 \times {fcu:.1f} \times {b:.0f}}}',
            'result': f'{x:.2f} mm',
            'variable': 'x'
        })
        
        # Step 10: Check x/d ratio
        x_d_ratio = x / d
        x_d_limit = 0.45  # Egyptian Code limit
        x_d_safe = x_d_ratio <= x_d_limit
        
        calculations.append({
            'step': '10',
            'description': 'Check x/d ratio',
            'formula': r'\frac{x}{d} \leq 0.45',
            'substitution': f'{x_d_ratio:.3f} ≤ {x_d_limit}',
            'result': f'{"PASS ✓" if x_d_safe else "FAIL ✗ (Over-reinforced)"}',
            'variable': 'Check'
        })
        
        # Step 11: Calculate design capacity
        # Mn = As * fy * (d - 0.4*x)  (Egyptian Code)
        
        Mn_Nmm = As_required * fy * (d - 0.4 * x)
        Mn = Mn_Nmm / 1e6
        
        calculations.append({
            'step': '11',
            'description': 'Design Capacity',
            'formula': r'M_n = A_s \cdot f_y \cdot (d - 0.4x)',
            'substitution': rf'{As_required:.1f} \times {fy:.0f} \times ({d:.1f} - 0.4 \times {x:.2f})',
            'result': f'{Mn:.2f} kN.m',
            'variable': 'Mn'
        })
        
        # Step 12: Capacity check (with safety factor γ = 1.15 for Egyptian Code)
        gamma_s = 1.15
        Mu_design = Mu * gamma_s
        capacity_safe = Mn >= Mu_design
        utilization = (Mu_design / Mn) * 100 if Mn > 0 else 0
        
        calculations.append({
            'step': '12',
            'description': 'Capacity Check',
            'formula': r'M_n \geq \gamma_s \cdot M_u',
            'substitution': f'{Mn:.2f} ≥ {gamma_s} × {Mu:.2f} = {Mu_design:.2f}',
            'result': f'{"SAFE ✓" if capacity_safe else "UNSAFE ✗"} ({utilization:.1f}%)',
            'variable': 'Check'
        })
        
        # Set variables for later use
        strain_safe = x_d_safe  # For Egyptian Code
        strain_status = "Within limits ✓" if x_d_safe else "Over-reinforced ✗"
        phi_Mn = Mn  # For compatibility with display
        c = x  # For compatibility
        es = 0.003 * (d - x) / x if x > 0 else 0  # Approximate strain
        a_final = x  # For compatibility

except ZeroDivisionError:
    st.error("❌ Calculation Error: Division by zero detected. Please check your inputs.")
    st.stop()
except Exception as e:
    st.error(f"❌ Calculation Error: {str(e)}")
    st.stop()

# ==================== DISPLAY RESULTS ====================

# Input Summary
st.markdown('<h2 class="section-header">📋 Input Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Design Code", design_code.split()[0])
    st.metric("Mu", f"{Mu:.2f} kN.m")
with col2:
    st.metric("b", f"{b:.0f} mm")
    st.metric("h", f"{h:.0f} mm")
with col3:
    st.metric("cover", f"{cover:.0f} mm")
    st.metric("fy", f"{fy:.0f} MPa")
with col4:
    st.metric("f'c/fcu", f"{fcu:.1f} MPa")
    if design_code == "ACI 318":
        st.metric("φ", f"{phi:.2f}")

# Calculations Display
st.markdown('<h2 class="section-header">🔢 Calculations</h2>', unsafe_allow_html=True)

for calc in calculations:
    col1, col2, col3, col4 = st.columns([0.4, 2.5, 2.5, 1.6])
    
    with col1:
        st.markdown(f"**{calc['step']}**")
    
    with col2:
        st.markdown(f"**{calc['description']}:** ${calc['formula']}$")
    
    with col3:
        st.latex(calc['substitution'])
    
    with col4:
        if 'PASS' in calc['result'] or 'SAFE' in calc['result']:
            st.success(calc['result'])
        elif 'FAIL' in calc['result'] or 'UNSAFE' in calc['result']:
            st.error(calc['result'])
        else:
            st.info(f"**{calc['result']}**")

# Summary
st.markdown("---")
st.markdown('<h2 class="section-header">✅ Design Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📏 Required Steel Area**")
    st.metric("As Required", f"{As_required:.1f} mm²")
    st.metric("Effective Depth", f"{d:.1f} mm")

with col2:
    st.markdown("**🔍 Analysis**")
    if design_code == "ACI 318":
        st.metric("Neutral Axis (c)", f"{c:.2f} mm")
        st.metric("c/d ratio", f"{(c/d):.3f}")
        st.metric("Steel Strain (εs)", f"{es:.5f}")
        st.metric("Section Type", strain_status)
    else:
        st.metric("Neutral Axis (x)", f"{x:.2f} mm")
        st.metric("x/d ratio", f"{x_d_ratio:.3f}")
        st.metric("Lever Arm (J)", f"{J_used:.4f}")
        st.metric("Section Status", strain_status)

with col3:
    st.markdown("**✅ Safety Status**")
    overall_safe = strain_safe and capacity_safe
    
    if overall_safe:
        st.success("### ✅ DESIGN IS SAFE")
    else:
        st.error("### ❌ DESIGN FAILED")
    
    st.markdown("**Checks:**")
    if design_code == "ACI 318":
        st.markdown(f"{'✅' if strain_safe else '❌'} Steel Strain: {es:.5f} {'≥' if strain_safe else '<'} 0.002")
        st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: φMn={phi_Mn:.2f} {'≥' if capacity_safe else '<'} Mu={Mu:.2f}")
    else:
        st.markdown(f"{'✅' if x_d_safe else '❌'} x/d ratio: {x_d_ratio:.3f} {'≤' if x_d_safe else '>'} 0.45")
        st.markdown(f"{'✅' if capacity_safe else '❌'} Capacity: Mn={Mn:.2f} {'≥' if capacity_safe else '<'} {gamma_s}×Mu={Mu_design:.2f}")
    st.markdown(f"{'✅' if As_required >= As_min else '❌'} Minimum Steel")
    
    if design_code == "ACI 318":
        st.metric("Capacity Ratio", f"{phi_Mn/Mu:.2f}")
    else:
        st.metric("Capacity Ratio", f"{Mn/Mu_design:.2f}")

# Reinforcement Selection Section
st.markdown("---")
st.markdown('<h2 class="section-header">🔧 Reinforcement Selection</h2>', unsafe_allow_html=True)

# Auto suggestions
st.markdown("### 💡 Automatic Suggestions")
col1, col2, col3 = st.columns(3)

suggestion_count = 0
for diameter in [10, 12, 14, 16, 18, 20, 22, 25]:
    area_per_bar = rebar_data[diameter][0]
    num_bars = math.ceil(As_required / area_per_bar)
    
    if num_bars <= 9 and suggestion_count < 6:
        total_area = rebar_data[diameter][num_bars - 1]
        excess = ((total_area - As_required) / As_required) * 100
        
        if suggestion_count % 3 == 0:
            with col1:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        elif suggestion_count % 3 == 1:
            with col2:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        else:
            with col3:
                st.info(f"**{num_bars}Ø{diameter}**\nAs = {total_area:.0f} mm²\n(+{excess:.1f}%)")
        
        suggestion_count += 1

# Manual Selection
st.markdown("---")
st.markdown("### 🎯 Manual Selection & Verification")

col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    selected_diameter = st.selectbox(
        "Bar Diameter (mm)",
        options=list(rebar_data.keys()),
        index=list(rebar_data.keys()).index(16)
    )

with col2:
    selected_num_bars = st.selectbox(
        "Number of Bars",
        options=list(range(1, 10)),
        index=3
    )

# Get selected reinforcement area
selected_As = rebar_data[selected_diameter][selected_num_bars - 1]

# Verify selected reinforcement
st.markdown("---")
st.markdown("### ✅ Selected Reinforcement Verification")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Selected Config", f"{selected_num_bars}Ø{selected_diameter}")

with col2:
    st.metric("Provided As", f"{selected_As:.1f} mm²")
    excess_percentage = ((selected_As - As_required) / As_required) * 100
    st.caption(f"Excess: {excess_percentage:+.1f}%")

with col3:
    check_As = selected_As >= As_required
    if check_As:
        st.success(f"✓ As Check\n{selected_As:.0f} ≥ {As_required:.0f}")
    else:
        st.error(f"✗ As Check\n{selected_As:.0f} < {As_required:.0f}")

with col4:
    # Re-calculate capacity with selected As
    if design_code == "ACI 318":
        a_selected = (selected_As * fy) / (0.85 * fcu * b)
        c_selected = a_selected / beta1
        es_selected = ((d - c_selected) / c_selected) * 0.003
        phi_Mn_selected = (phi * selected_As * fy * (d - a_selected/2)) / 1e6
        check_capacity = phi_Mn_selected >= Mu
        capacity_display = phi_Mn_selected
    else:  # Egyptian Code
        x_selected = (selected_As * fy) / (0.67 * fcu * b)
        Mn_selected = (selected_As * fy * (d - 0.4 * x_selected)) / 1e6
        check_capacity = Mn_selected >= Mu_design
        capacity_display = Mn_selected
    
    if check_capacity:
        st.success(f"✓ Capacity Check\nMn = {capacity_display:.2f} kN.m")
    else:
        st.error(f"✗ Capacity Check\nMn = {capacity_display:.2f} kN.m")

# Detailed verification
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Analysis with Selected Steel**")
    if design_code == "ACI 318":
        st.metric("a (selected)", f"{a_selected:.2f} mm")
        st.metric("c (selected)", f"{c_selected:.2f} mm")
        st.metric("c/d ratio", f"{(c_selected/d):.3f}")
    else:
        st.metric("x (selected)", f"{x_selected:.2f} mm")
        st.metric("x/d ratio", f"{(x_selected/d):.3f}")

with col2:
    st.markdown("**⚡ Strain Analysis**")
    if design_code == "ACI 318":
        st.metric("εs (selected)", f"{es_selected:.5f}")
        
        if es_selected >= 0.005:
            st.success("✓ Tension Controlled")
        elif es_selected >= 0.002:
            st.warning("⚠ Transition Zone")
        else:
            st.error("✗ Compression Controlled")
    else:
        x_d_selected = x_selected / d
        st.metric("x/d (selected)", f"{x_d_selected:.3f}")
        
        if x_d_selected <= 0.45:
            st.success("✓ Within ECP Limits")
        else:
            st.error("✗ Exceeds ECP Limits")

with col3:
    st.markdown("**🎯 Final Status**")
    if design_code == "ACI 318":
        final_safe = check_As and check_capacity and (es_selected >= 0.002)
    else:
        final_safe = check_As and check_capacity and (x_d_selected <= 0.45)
    
    if final_safe:
        st.success("### ✅ SELECTED CONFIG IS SAFE")
    else:
        st.error("### ❌ SELECTED CONFIG FAILED")
    
    if design_code == "ACI 318":
        st.metric("Utilization", f"{(Mu/phi_Mn_selected)*100:.1f}%")
    else:
        st.metric("Utilization", f"{(Mu_design/Mn_selected)*100:.1f}%")

# Rebar Table
st.markdown("---")
st.markdown("### 📋 Complete Rebar Area Table")

df_data = []
for diameter, areas in rebar_data.items():
    row = [diameter] + areas
    df_data.append(row)

df = pd.DataFrame(df_data, columns=['Ø (mm)', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
df = df.set_index('Ø (mm)')

st.dataframe(df, use_container_width=True)
st.caption("📝 Note: All areas in mm²")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🏗️ **Code**: {design_code}")
with col2:
    st.caption("📐 **Type**: Rectangular Beam")
with col3:
    st.caption("🔧 **Analysis**: Flexural Design")
