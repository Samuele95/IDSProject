import streamlit as st
from plclient.views.views import app_image, BusinessOwnerLogin

if __name__ == '__main__':
    st.set_page_config(
        page_title="Project Loyalty Business Owner Login",
        page_icon="🤝",
        layout="wide",
        initial_sidebar_state="expanded",
    )
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
    BusinessOwnerLogin(
        token=st.session_state['token'],
        user_url=st.session_state['user_url'],
        shop_url=st.session_state['shop_url']
    ).open_view()