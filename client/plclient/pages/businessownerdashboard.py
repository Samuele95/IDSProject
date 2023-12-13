from plclient.api.shopapi import ShopDetail
from plclient.api.userapi import UserDetail
from plclient.utils.settings import users_endpoint, shops_endpoint
from st_pages import hide_pages
import streamlit as st

from plclient.views.fidelityprogramviews import CashierFidelityProgramView, BusinessOwnerFidelityProgramView
from plclient.views.shopviews import CashierShopView
from plclient.views.transactionviews import CashierTransactionView
from plclient.views.userviews import GenericUserView
from plclient.views.views import CashierDashboard, BusinessOwnerDashboard

if __name__ == '__main__':
    st.set_page_config(
        page_title="customerdashboard",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    hide_pages(['main', 'mainpage', 'businessownerdashboard', 'businessownerloginpage', 'cashierdashboard', 'cashierloginpage', 'customerdashboard', 'customerloginpage'])
    userdata = UserDetail(url=users_endpoint + 'admin').get()
    shopdata = ShopDetail(url=shops_endpoint + 'Test shop').get()
    user_view = GenericUserView(userdata)
    fidelity_program_view = BusinessOwnerFidelityProgramView(shopdata,user_view)
    shop_view = CashierShopView(shopdata, user_view, fidelity_program_view)
    BusinessOwnerDashboard(
        user_view,
        shop_view,
        fidelity_program_view,
    ).open_view()
