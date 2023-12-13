from plclient.api.userapi import UserDetail
from plclient.views.fidelityprogramviews import ReadOnlyFidelityProgramView
from plclient.views.shopviews import CustomerShopView
from plclient.views.transactionviews import CustomerTransactionView
from plclient.views.userviews import GenericUserView
from plclient.views.views import UserDashboard
import streamlit as st


if __name__ == '__main__':
    st.set_page_config(
        page_title="Project Loyalty Customer Dashboard",
        page_icon="🤝",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    userdata = UserDetail(url=st.session_state['user_url']).get()
    user_view = GenericUserView(userdata)
    fidelity_program_view = ReadOnlyFidelityProgramView(userdata)
    shop_view = CustomerShopView(fidelity_program_view)
    transaction_view = CustomerTransactionView(userdata, shop_view)
    UserDashboard(
        user_view,
        shop_view,
        fidelity_program_view,
        transaction_view
    ).open_view()
