from plclient.api.shopapi import ShopDetail
from plclient.api.userapi import UserDetail
from plclient.utils.settings import users_endpoint, shops_endpoint
import streamlit as st

from plclient.views.fidelityprogramviews import ReadOnlyFidelityProgramView, CashierFidelityProgramView
from plclient.views.shopviews import CashierShopView
from plclient.views.transactionviews import CustomerTransactionView, CashierTransactionView
from plclient.views.userviews import GenericUserView
from plclient.views.views import CashierDashboard

if __name__ == '__main__':
    st.set_page_config(
        page_title="customerdashboard",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    userdata = UserDetail(url=st.session_state['user_url']).get()
    shopdata = ShopDetail(url=st.session_state['shop_url']).get()
    user_view = GenericUserView(userdata)
    fidelity_program_view = CashierFidelityProgramView(shopdata, user_view)
    shop_view = CashierShopView(shopdata, user_view, fidelity_program_view)
    transaction_view = CashierTransactionView(shop=shopdata, users=user_view)
    # transaction_view = CustomerTransactionView(userdata, shop_view)
    CashierDashboard(
        user_view,
        shop_view,
        fidelity_program_view,
        transaction_view
    ).open_view()
