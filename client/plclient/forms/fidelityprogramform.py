from typing import Any

from plclient.api.catalogueapi import CatalogueDetail
from plclient.api.productapi import ProductDetail
from plclient.api.userapi import UserDetail
from plclient.forms.forms import Form, Table
from plclient.api.fidelityprogramapi import FidelityProgramDetail
from plclient.api.shopapi import ShopDetail, ShopList
import streamlit as st

from plclient.forms.productforms import ProductCreateForm
from plclient.utils.settings import coefficient_limits


class FidelityProgramForm(Form):
    element: FidelityProgramDetail

    def __init__(self, element: FidelityProgramDetail, prize_list: Table, read_only: bool = True) -> None:
        if element.url is None or element.name is None:
            raise ValueError('No fidelity program available')
        self.element = element
        self.read_only = read_only
        self.prize_list = prize_list
        self.program_name = None
        self.program_type = None
        self.program_des = None

    def show(self) -> Any:
        match self.element.program_type:
            case "CASHBACK":
                box_index = 0
            case "LEVELS":
                box_index = 1
            case "POINTS":
                box_index = 2
            case _:
                box_index = 3
        tab1, tab2, tab3 = st.tabs(["Info", "Prizes", "Joined Shops"])
        with tab1:
            self.program_name = st.text_input(
                label="Program name",
                value=self.element.name,
                placeholder="enter program name",
                disabled=True,
                key=str(self.element) + '1',
            )
            self.program_type = st.selectbox(
                label="Program Type",
                options=("CASHBACK", "LEVELS", "POINTS", "GENERIC"),
                index=box_index,
                disabled=True,
                key=str(self.element) + '2',
            )

            self.program_des = st.text_area(
                label="Bio",
                value=self.element.description,
                placeholder="enter a small description",
                disabled=self.read_only,
                key=str(self.element) + '3',
            )

        with tab2:
            self.prize_list.show()
        with tab3:
            Table(
                element=ShopList(data=self.element.shop_list, datainstance=ShopDetail),
                columns=['url', 'name', 'location'],
                hidden_columns=['url']
            )
        return tab1, tab2, tab3




class CashierFidelityProgramForm(Form):
    element: FidelityProgramDetail

    def __init__(self, element: FidelityProgramDetail, prize_list: Table, user_list: Table) -> None:
        if element.url is None or element.name is None:
            raise ValueError('No fidelity program available')
        self.element = element
        self.prize_list = prize_list
        self.user_list = user_list
        self.program_name = None
        self.program_type = None
        self.program_des = None

    def show(self) -> Any:
        match self.element.program_type:
            case "CASHBACK":
                box_index = 0
            case "LEVELS":
                box_index = 1
            case "POINTS":
                box_index = 2
            case _:
                box_index = 3
        tab1, tab2, tab3, tab4 = st.tabs(["Info", "Prizes", "Joined Shops", "Joined Users"])
        with tab1:
            self.program_name = st.text_input(
                label="Program name",
                value=self.element.name,
                placeholder="enter program name",
                disabled=True,
                key=str(self.element) + '1',
            )
            self.program_type = st.selectbox(
                label="Program Type",
                options=("CASHBACK", "LEVELS", "POINTS", "GENERIC"),
                index=box_index,
                key=str(self.element) + '2',
            )

            self.program_des = st.text_area(
                label="Bio",
                value=self.element.description,
                placeholder="enter a small description",
                key=str(self.element) + '3',
            )

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                prizes = self.prize_list.show()
                if len(prizes.selected_rows) > 0:
                    delete_user_button = st.button('Remove prize from fidelity program')
                    if delete_user_button:
                        ProductDetail(url=prizes.selected_rows[0]['url']).delete()
        with tab3:
            shops = Table(
                element =ShopList(
                    data=self.element.shop_list,
                    datainstance=ShopDetail
                ),
                columns=['url', 'name', 'location'],
                hidden_columns=['url']
            ).show()
        with tab4:
            users = self.user_list.show()
            if len(users.selected_rows) > 0:
                delete_user_button = st.button('Remove user from fidelity program')
                if delete_user_button:
                    UserDetail(url=users.selected_rows[0]['url']).delete()
        return tab1, tab2, tab3, tab4, col1, col2


class AddPrizesOrUsersToFidelityProgram(Form):
    element: FidelityProgramDetail

    def __init__(self, decorated: CashierFidelityProgramForm, shop: ShopDetail, all_users: Table) -> None:
        if shop.url is None or shop.name is None:
            raise ValueError('Cannot access to shop data')
        self.decorated = decorated
        self.element = decorated.element
        self.shop = shop
        self.all_users = all_users

    def show(self) -> Any:
        tab1, tab2, tab3, tab4, col1, col2 = self.decorated.show()
        with col2:
            ProductCreateForm(
                shop=self.shop,
                fidelity_programs_data=self.element
            ).show()
        with tab4:
            with st.expander('Add user to program'):
                selected_users = self.all_users.show()
                add_user = st.button('Add the selected user')
                if add_user and len(selected_users.selected_rows) > 0:
                    CatalogueDetail(
                        customer=selected_users.selected_rows[0]['url'],
                        fidelity_program=self.element.url
                    ).create_or_update()
        return tab1, tab2, tab3, tab4, col1, col2


class JoinOrLeaveFidelityProgramAsBusiness(Form):
    element: FidelityProgramDetail

    def __init__(self, decorated: CashierFidelityProgramForm, shop: ShopDetail, is_joined: bool) -> None:
        if shop.url is None or shop.name is None:
            raise ValueError('Cannot access to shop data')
        self.decorated = decorated
        self.element = self.decorated.element
        self.shop = shop
        self.is_joined = is_joined

    def show(self) -> Any:
        tab1, tab2, tab3, tab4, col1, col2 = self.decorated.show()
        with tab1:
            button = st.button('Join') if not self.is_joined else st.button('Leave')
            if button:
                if not self.is_joined:
                    FidelityProgramDetail(
                        url=self.element.url,
                        name=self.element.name,
                        program_type=self.element.program_type,
                        description=self.element.description,
                        points_coefficient=self.element.points_coefficient,
                        prize_coefficient=self.element.prize_coefficient,
                        shop_list=self.element.shop_list + [self.shop.url]
                    ).create_or_update()
                else:
                    FidelityProgramDetail(
                        url=self.element.url,
                        name=self.element.name,
                        program_type=self.element.program_type,
                        description=self.element.description,
                        points_coefficient=self.element.points_coefficient,
                        prize_coefficient=self.element.prize_coefficient,
                        shop_list=[shop for shop in self.element.shop_list if shop != self.shop.url]
                    ).create_or_update()
        return tab1, tab2, tab3, tab4, col1, col2


class FidelityProgramCreateForm(Form):
    element: FidelityProgramDetail | None

    def __init__(self, founder_shop: ShopDetail) -> None:
        if founder_shop.url is None or founder_shop.name is None:
            raise ValueError('Cannot create a fidelity program without a shop')
        self.element = None
        self.founder_shop = founder_shop
        self.name = None
        self.ptype = None
        self.desc = None
        self.points_coefficient = None
        self.prize_coefficient = None

    def show(self) -> Any:
        with st.container():
            self.ptype = st.selectbox(
                label="Fidelity program type",
                options=["GENERIC", "CASHBACK", "POINTS", "LEVELS", "MEMBERSHIP"],
            )
            self.name = st.text_input(
                label="Fidelity program name",
                placeholder="enter program name",
            )
            self.desc = st.text_area(label="Description", placeholder="enter a description")
            min_lim, max_lim = coefficient_limits(self.ptype)
            if min_lim != max_lim:
                self.points_coefficient = st.slider(
                    label="Points coefficient",
                    min_value=min_lim,
                    max_value=max_lim,
                    value=(min_lim + max_lim) / 2,
                    step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
                    format="%.4f",
                )
                self.prize_coefficient = st.slider(
                    label="Prize coefficient",
                    min_value=min_lim,
                    max_value=max_lim,
                    value=(min_lim + max_lim) / 2,
                    step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
                    format="%.4f",
                )
            submitted = st.button("Submit")
            if submitted:
                self.element = FidelityProgramDetail(
                    name=self.name,
                    program_type=self.ptype,
                    description=self.desc,
                    points_coefficient=self.points_coefficient / 100,
                    prize_coefficient=self.prize_coefficient / 100,
                    shop_list=[self.founder_shop.url],
                ).create_or_update()
