from streamlit_extras.switch_page_button import switch_page
from plclient.views.views import CustomerLogin, app_image
import streamlit as st
from st_pages import hide_pages
from sys import exit

if __name__ == '__main__':
    st.set_page_config(
        page_title="Project Loyalty Profile Choose",
        page_icon="🤝",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    hide_pages(['main', 'mainpage', 'businessownerdashboard', 'businessownerloginpage', 'cashierdashboard', 'cashierloginpage', 'customerdashboard', 'customerloginpage'])
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.columns(3)[1].image(app_image)
    with st.form('Choose dashboard'):
        choice = st.selectbox(
            'Choose a profile type',
            ('User', 'Cashier', 'Business owner')
        )
        button = st.form_submit_button('Submit')
        if button:
            match choice:
                case 'User':
                    switch_page('customerloginpage')
                case 'Cashier':
                    switch_page('cashierloginpage')
                case 'Business owner':
                    switch_page('businessownerloginpage')
                case __:
                    exit()
