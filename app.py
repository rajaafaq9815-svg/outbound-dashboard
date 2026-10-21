import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Outbound Operations Performance Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Outbound Operations Performance Dashboard")
st.write("Upload your daily performance Excel file below to instantly generate your single-screen operational dashboard.")

uploaded_file = st.file_uploader("Upload Daily Performance Excel (.xlsx)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        if 'User name' in df.columns:
            df_staff = df[df['User name'] != 'Total'].copy()
        else:
            df_staff = df.copy()

        df_staff['Picking Items'] = df_staff['Zone Picking Item'] + df_staff['Normal Orders Item']
        df_staff['Sorting Items'] = df_staff['Sorter Picking Item']
        df_staff['Packing Items'] = df_staff['Item Packed']
        
        total_packed = int(df_staff['Packing Items'].sum())
        total_pick = int(df_staff['Picking Items'].sum())
        total_sort = int(df_staff['Sorting Items'].sum())
        
        df_staff['Earned Hours'] = (df_staff['Picking Items'] / 100.0) + (df_staff['Sorting Items'] / 175.0) + (df_staff['Packing Items'] / 100.0)
        shift_hours = 12.0
        df_staff['Achievement %'] = (df_staff['Earned Hours'] / shift_hours) * 100.0
        df_staff = df_staff.sort_values(by='Achievement %', ascending=False).reset_index(drop=True)
        
        overall_ach = (df_staff['Earned Hours'].sum() / (len(df_staff) * shift_hours)) * 100.0
        
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(16, 9), facecolor='#0b0f19')

        plt.figtext(0.04, 0.93, "DAILY OPERATIONS  •  PACKING (OUTBOUND) SHIFT PERFORMANCE", fontsize=11, fontweight='bold', color='#94a3b8')
        plt.figtext(0.04, 0.87, "Performance Dashboard", fontsize=26, fontweight='bold', color='#ffffff')
        plt.figtext(0.04, 0.84, f"Shifts: 07:00–19:00 & 19:00–07:00 (12 hrs)  •  {len(df_staff)} staff on floor", fontsize=10, color='#94a3b8')

        plt.figtext(0.96, 0.88, f"{overall_ach:.1f}%", fontsize=36, fontweight='bold', color='#38bdf8', ha='right')
        plt.figtext(0.96, 0.84, "OVERALL SITE ACHIEVEMENT", fontsize=9, fontweight='bold', color='#64748b', ha='right')

        achievements = df_staff['Achievement %'].tolist()
        c_gt_80 = sum(1 for v in achievements if v >= 80)
        c_60_80 = sum(1 for v in achievements if 60 <= v < 80)
        c_40_60 = sum(1 for v in achievements if 40 <= v < 60)
        c_20_40 = sum(1 for v in achievements if 20 <= v < 40)

        kpis = [
            (f"{total_packed:,}", "Total Items Packed", "#ffffff", 0.04, 0.17),
            (str(c_gt_80), "Staff Above 80%", "#4ade80", 0.23, 0.17),
            (str(c_60_80), "Staff 60–80%", "#38bdf8", 0.42, 0.17),
            (str(c_40_60), "Staff 40–60%", "#facc15", 0.61, 0.17),
            (str(c_20_40), "Staff 20–40%", "#fb923c", 0.80, 0.16),
        ]

        for val, label, col, x_pos, w in kpis:
            ax_k = fig.add_axes([x_pos, 0.72, w, 0.095], facecolor='#131c2e')
            ax_k.text(0.08, 0.55, val, fontsize=22, fontweight='bold', color=col)
            ax_k.text(0.08, 0.20, label, fontsize=8.5, color='#94a3b8')
            ax_k.axis('off')

        ax_staff = fig.add_axes([0.04, 0.08, 0.58, 0.61], facecolor='#131c2e')
        ax_staff.axis('off')
        ax_staff.text(0.03, 0.94, "Staff Achievement — % of Blended Target (12-hr Shift)", fontsize=12, fontweight='bold', color='#ffffff')

        names = df_staff['User name'].tolist()
        num_staff = len(names)
        half_staff = (num_staff + 1) // 2
        y_rows = np.linspace(0.81, 0.04, max(12, half_staff))

        def get_tier_color(val):
            if val >= 80: return '#4ade80'
            elif val >= 60: return '#38bdf8'
            elif val >= 40: return '#facc15'
            elif val >= 20: return '#fb923c'
            else: return '#f87171'

        for i in range(min(half_staff, len(y_rows))):
            name1, val1 = names[i], achievements[i]
            col1 = get_tier_color(val1)
            ax_staff.text(0.03, y_rows[i], f"{name1[:10]:<10}", fontsize=8.5, color='#ffffff', fontweight='bold', va='center')
            ax_staff.add_patch(plt.Rectangle((0.18, y_rows[i]-0.018), 0.20, 0.024, color='#1e293b'))
            ax_staff.add_patch(plt.Rectangle((0.18, y_rows[i]-0.018), min(0.20, (val1 / 100.0) * 0.20), 0.024, color=col1))
            ax_staff.text(0.40, y_rows[i], f"{val1:.1f}%", fontsize=8.5, color=col1, fontweight='bold', va='center')

            if i + half_staff < num_staff:
                name2, val2 = names[i + half_staff], achievements[i + half_staff]
                col2 = get_tier_color(val2)
                ax_staff.text(0.51, y_rows[i], f"{name2[:10]:<10}", fontsize=8.5, color='#ffffff', fontweight='bold', va='center')
                ax_staff.add_patch(plt.Rectangle((0.66, y_rows[i]-0.018), 0.20, 0.024, color='#1e293b'))
                ax_staff.add_patch(plt.Rectangle((0.66, y_rows[i]-0.018), min(0.20, (val2 / 100.0) * 0.20), 0.024, color=col2))
                ax_staff.text(0.88, y_rows[i], f"{val2:.1f}%", fontsize=8.5, color=col2, fontweight='bold', va='center')

        ax_task = fig.add_axes([0.65, 0.08, 0.31, 0.61], facecolor='#131c2e')
        ax_task.axis('off')
        ax_task.text(0.06, 0.94, "Packed Volume Share by Task", fontsize=12, fontweight='bold', color='#ffffff')

        ax_donut = fig.add_axes([0.68, 0.38, 0.25, 0.35], facecolor='none')
        volumes = [total_pick, total_sort, total_packed]
        colors = ['#facc15', '#38bdf8', '#c084fc']

        ax_donut.pie(
            volumes, 
            autopct='%1.1f%%',
            pctdistance=0.70,
            colors=colors,
            startangle=140,
            textprops=dict(color='#ffffff', fontweight='bold', fontsize=8.5)
        )
        centre_circle = plt.Circle((0,0), 0.58, fc='#131c2e')
        ax_donut.add_artist(centre_circle)

        ax_task.text(0.08, 0.28, "● Picking (target 100/hr)", color='#facc15', fontsize=9, fontweight='bold')
        ax_task.text(0.88, 0.28, f"{total_pick:,}", color='#ffffff', fontsize=9, fontweight='bold', ha='right')

        ax_task.text(0.08, 0.19, "● Sorting (target 175/hr)", color='#38bdf8', fontsize=9, fontweight='bold')
        ax_task.text(0.88, 0.19, f"{total_sort:,}", color='#ffffff', fontsize=9, fontweight='bold', ha='right')

        ax_task.text(0.08, 0.10, "● Packing (target 100/hr)", color='#c084fc', fontsize=9, fontweight='bold')
        ax_task.text(0.88, 0.10, f"{total_packed:,}", color='#ffffff', fontsize=9, fontweight='bold', ha='right')

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
