import streamlit as st
from plclient.views.views import CashierLogin, app_image

if __name__ == '__main__':
    st.set_page_config(
        page_title="Project Loyalty Customer Login",
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
    CashierLogin(
        token=st.session_state['token'],
        user_url=st.session_state['user_url'],
        shop_url=st.session_state['shop_url']
    ).open_view()
