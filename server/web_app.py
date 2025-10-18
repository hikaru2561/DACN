"""
Face Recognition Attendance System - Web Interface
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
from PIL import Image
import base64
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

def post_api_data(endpoint, files=None, data=None):
    """Helper function to make API requests"""
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", files=files, data=data, timeout=30)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error_msg = error_data.get('detail', f"API Error: {response.status_code}")
            st.error(f"❌ Error: {error_msg}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return None

def get_api_data(endpoint):
    """Helper function to get API data"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return None

def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">👤 Face Recognition Attendance System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Dashboard", "👤 User Registration", "✅ Check-in", "📊 Attendance Logs", "📈 Statistics", "⚙️ System Status"]
    )
    
    # Main content based on page selection
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👤 User Registration":
        show_registration()
    elif page == "✅ Check-in":
        show_checkin()
    elif page == "📊 Attendance Logs":
        show_attendance_logs()
    elif page == "📈 Statistics":
        show_statistics()
    elif page == "⚙️ System Status":
        show_system_status()

def show_dashboard():
    """Dashboard page"""
    st.header("📊 Dashboard Overview")
    
    # Get system stats
    stats = get_api_data("attendance/stats")
    
    if stats and not isinstance(stats, dict) or 'error' in str(stats):
        st.error("❌ Failed to load statistics")
        stats = None
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Attendance",
                value=stats.get('total_attendance', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Unique Users",
                value=stats.get('unique_users', 0),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Period (Days)",
                value=stats.get('period_days', 30),
                delta=None
            )
        
        with col4:
            avg_daily = stats.get('total_attendance', 0) / max(stats.get('period_days', 1), 1)
            st.metric(
                label="Avg Daily",
                value=f"{avg_daily:.1f}",
                delta=None
            )
        
        # Daily breakdown chart
        if stats.get('daily_breakdown'):
            st.subheader("📈 Daily Attendance Trend")
            df = pd.DataFrame(stats['daily_breakdown'])
            df['date'] = pd.to_datetime(df['date'])
            
            fig = px.line(df, x='date', y='count', title='Daily Attendance Count')
            fig.update_layout(xaxis_title="Date", yaxis_title="Attendance Count")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    logs = get_api_data("attendance/logs")
    
    if logs and not isinstance(logs, list) or 'error' in str(logs):
        st.error("❌ Failed to load attendance logs")
        logs = None
    
    if logs:
        # Flatten the user object for better display
        flattened_logs = []
        for log in logs:
            flattened_log = {
                'user_name': log.get('user', {}).get('name', 'Unknown'),
                'student_code': log.get('user', {}).get('student_code', 'Unknown'),
                'timestamp': log.get('timestamp'),
                'confidence': log.get('confidence'),
                'device_id': log.get('device_id', 'N/A')
            }
            flattened_logs.append(flattened_log)
        
        df_logs = pd.DataFrame(flattened_logs)
        df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
        df_logs = df_logs.sort_values('timestamp', ascending=False).head(10)
        
        # Format confidence as percentage
        df_logs['confidence'] = (df_logs['confidence'] * 100).round(1).astype(str) + '%'
        
        st.dataframe(
            df_logs[['user_name', 'student_code', 'timestamp', 'confidence', 'device_id']],
            use_container_width=True,
            column_config={
                'user_name': 'Tên',
                'student_code': 'Mã SV',
                'timestamp': 'Thời gian',
                'confidence': 'Độ tin cậy',
                'device_id': 'Thiết bị'
            }
        )
    else:
        st.info("No recent activity found")

def show_registration():
    """User registration page"""
    st.header("👤 User Registration")
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="Enter full name")
            student_code = st.text_input("Student Code *", placeholder="Enter student code")
            department = st.text_input("Department", placeholder="Enter department")
        
        with col2:
            uploaded_file = st.file_uploader(
                "Upload Face Image *", 
                type=['jpg', 'jpeg', 'png'],
                help="Upload a clear photo of your face"
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        submitted = st.form_submit_button("Register User", type="primary")
        
        if submitted:
            if not all([name, student_code, uploaded_file]):
                st.error("Please fill in all required fields")
            else:
                with st.spinner("Processing registration..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {
                        'name': name, 
                        'student_code': student_code, 
                        'department': department or ""
                    }
                    
                    result = post_api_data("register", files=files, data=data)
                    
                    if result:
                        st.success("✅ User registered successfully!")
                        st.json(result)

def show_checkin():
    """Check-in page"""
    st.header("✅ Face Recognition Check-in")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Photo for Check-in", 
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo of your face for attendance check-in"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    with col2:
        device_id = st.text_input("Device ID", value="web-interface", help="Optional device identifier")
        
        if st.button("Check-in", type="primary", use_container_width=True):
            if uploaded_file:
                with st.spinner("Processing check-in..."):
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {'device_id': device_id}
                    
                    result = post_api_data("checkin", files=files, data=data)
                    
                    if result and result.get('success'):
                        st.success("✅ Check-in successful!")
                        
                        # Display result in a nice format
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("User", result['user']['name'])
                            st.metric("Student Code", result['user']['student_code'])
                        with col_b:
                            st.metric("Confidence", f"{result['confidence']:.2%}")
                            st.metric("Time", result['timestamp'][:19])
                    else:
                        st.error("❌ Check-in failed. No matching user found.")

def show_attendance_logs():
    """Attendance logs page"""
    st.header("📊 Attendance Logs")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days = st.selectbox("Period", [7, 30, 90, 365], index=1)
    
    with col2:
        limit = st.number_input("Max Records", min_value=10, max_value=1000, value=100)
    
    with col3:
        if st.button("Refresh Data"):
            st.rerun()
    
    # Get attendance logs
    logs = get_api_data(f"attendance/logs?days={days}&limit={limit}")
    
    if logs:
        df = pd.DataFrame(logs)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Flatten user object into separate columns
        if 'user' in df.columns:
            df['user_name'] = df['user'].apply(lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown')
            df['student_code'] = df['user'].apply(lambda x: x.get('student_code', 'Unknown') if isinstance(x, dict) else 'Unknown')
        else:
            # If no user object, create placeholder columns
            df['user_name'] = 'Unknown'
            df['student_code'] = 'Unknown'
        
        # Summary stats
        st.subheader("📈 Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Unique Users", df['user_id'].nunique())
        with col3:
            st.metric("Avg Confidence", f"{df['confidence'].mean():.2%}")
        with col4:
            st.metric("Today's Count", len(df[df['timestamp'].dt.date == datetime.now().date()]))
        
        # Data table
        st.subheader("📋 Detailed Logs")
        display_columns = ['user_name', 'student_code', 'timestamp', 'confidence', 'device_id']
        available_columns = [col for col in display_columns if col in df.columns]
        
        st.dataframe(
            df[available_columns],
            use_container_width=True,
            column_config={
                "user_name": "Tên",
                "student_code": "Mã sinh viên", 
                "timestamp": "Thời gian",
                "confidence": "Độ tin cậy",
                "device_id": "Thiết bị"
            }
        )
        
        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"attendance_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No attendance logs found")

def show_statistics():
    """Statistics page"""
    st.header("📈 Statistics & Analytics")
    
    # Get stats
    stats = get_api_data("attendance/stats")
    
    if stats:
        # Overview metrics
        st.subheader("📊 Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Attendance", stats.get('total_attendance', 0))
        with col2:
            st.metric("Unique Users", stats.get('unique_users', 0))
        with col3:
            st.metric("Period Days", stats.get('period_days', 30))
        
        # Daily breakdown chart
        if stats.get('daily_breakdown'):
            st.subheader("📈 Daily Attendance Trend")
            df = pd.DataFrame(stats['daily_breakdown'])
            df['date'] = pd.to_datetime(df['date'])
            
            fig = px.bar(df, x='date', y='count', title='Daily Attendance Count')
            fig.update_layout(xaxis_title="Date", yaxis_title="Attendance Count")
            st.plotly_chart(fig, use_container_width=True)
            
            # Line chart
            fig2 = px.line(df, x='date', y='count', title='Attendance Trend')
            fig2.update_layout(xaxis_title="Date", yaxis_title="Attendance Count")
            st.plotly_chart(fig2, use_container_width=True)
    
    # User statistics
    st.subheader("👥 User Statistics")
    users = get_api_data("users")
    
    if users:
        df_users = pd.DataFrame(users)
        
        # Department distribution
        if 'department' in df_users.columns:
            dept_counts = df_users['department'].value_counts()
            fig = px.pie(values=dept_counts.values, names=dept_counts.index, title="Users by Department")
            st.plotly_chart(fig, use_container_width=True)
        
        # User table
        st.dataframe(df_users, use_container_width=True)

def show_system_status():
    """System status page"""
    st.header("⚙️ System Status")
    
    # Health check
    health = get_api_data("health")
    
    if health:
        st.success("✅ System is healthy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 Services")
            for service, status in health.get('services', {}).items():
                if status == "OK":
                    st.success(f"✅ {service}: {status}")
                else:
                    st.error(f"❌ {service}: {status}")
        
        with col2:
            st.subheader("ℹ️ System Info")
            st.info(f"**Version:** {health.get('version', 'N/A')}")
            st.info(f"**Status:** {health.get('status', 'N/A')}")
            st.info(f"**Timestamp:** {health.get('timestamp', 'N/A')}")
    else:
        st.error("❌ System health check failed")
    
    # API endpoints info
    st.subheader("🔗 API Endpoints")
    endpoints = [
        ("POST /api/v1/register", "Register new user"),
        ("POST /api/v1/checkin", "Check-in attendance"),
        ("GET /api/v1/users", "Get all users"),
        ("GET /api/v1/attendance/logs", "Get attendance logs"),
        ("GET /api/v1/attendance/stats", "Get attendance statistics"),
        ("GET /api/v1/health", "System health check"),
    ]
    
    for endpoint, description in endpoints:
        st.text(f"{endpoint:<30} - {description}")

if __name__ == "__main__":
    main()