from typing import Any

from plclient.api.catalogueapi import CatalogueList
from plclient.api.fidelityprogramapi import FidelityProgramDetail
from plclient.api.productapi import ProductDetail, ProductList
from plclient.forms.catalogueforms import CatalogueCreateForm
from plclient.forms.fidelityprogramform import CashierFidelityProgramForm
from plclient.forms.forms import Form, Table
from plclient.api.shopapi import ShopDetail
from plclient.api.userapi import UserDetail
import streamlit as st

from plclient.forms.productforms import ProductUpdateForm, ProductForm, ProductDeleteForm, PrizeDeleteForm, \
    PrizeUpdateForm, PrizeForm, ProductCreateForm
from plclient.utils.settings import product_endpoint, catalogue_endpoint


class ShopForm(Form):
    element: ShopDetail
    read_only: bool = True

    def __init__(self, element: ShopDetail, product_list: Table,
                 fidelity_programs: Table, read_only: bool = True) -> None:
        if element.url is None:
            raise ValueError('No shop available')
        self.element = element
        self.product_list = product_list
        self.fidelity_programs = fidelity_programs
        self.read_only = read_only
        self.shop_name = None
        self.shop_location = None
        self.shop_number = None

    def show(self) -> Any:
        global products
        global programs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Info", "Products", "Reviews", "Contact us", "Joined Fidelity Programs"]
        )
        with tab1:
            self.shop_name = st.text_input(
                label="Shop name",
                value=self.element.name,
                placeholder="enter shop name",
                disabled=self.read_only,
                key=str(self.element) + '1',
            )

            self.shop_location = st.text_area(
                label="Location",
                value=self.element.location,
                placeholder="enter shop location",
                disabled=self.read_only,
                key=str(self.element) + '2',
            )

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                products = self.product_list.show()

        with tab4:
            with st.expander("Phone"):
                self.shop_number = st.text_input(
                    label="Phone number",
                    value=self.element.phone,
                    placeholder="enter phone number",
                    disabled=self.read_only,
                    key=str(self.element) + '3',
                    label_visibility="collapsed",
                )

        with tab5:
            programs = self.fidelity_programs.show()
        return tab1, tab2, tab3, tab4, tab5, col1, col2


class ShopUpdateForm(Form):
    element: ShopDetail

    def __init__(self, decorated: ShopForm, user_list: Table) -> None:
        if decorated.read_only:
            decorated.read_only = False
        self.decorated = decorated
        self.element = self.decorated.element
        self.user_list = user_list

    def show(self) -> Any:
        tab1, tab2, tab3, tab4, tab5, col1, col2 = self.decorated.show()
        with tab2:
            with col2:
                selected_products = products.selected_rows
                if len(selected_products) > 0:
                    product = selected_products[0]
                    if product['fidelity_program'] is None:
                        ProductDeleteForm(ProductUpdateForm(ProductForm(ProductDetail(url=product['url']).get()))).show()
                    else:
                        PrizeDeleteForm(PrizeUpdateForm(PrizeForm(ProductForm(ProductDetail(url=product['url']).get())))).show()
            with col1:
                with st.expander('Add product to show'):
                    ProductCreateForm(
                        shop=self.element,
                        fidelity_programs_data=Table(
                            element=self.decorated.fidelity_programs.element,
                            columns=self.decorated.fidelity_programs.columns,
                            hidden_columns=self.decorated.fidelity_programs.hidden_columns,
                            key='Fidelity program table for product creation form'
                        )).show()
        with tab5:
            selected_programs = programs.selected_rows
            if len(selected_programs) > 0:
                with st.expander('Show program details'):
                    fidelity_program = FidelityProgramDetail(url=selected_programs[0]['url']).get()
                    CashierFidelityProgramForm(
                        element=fidelity_program,
                        prize_list=Table(
                            element=ProductList(api_endpoint=product_endpoint + 'byprogram/' + fidelity_program.name),
                            columns=['url', 'name', 'value'],
                            hidden_columns=['url'],
                            selection_mode='multiple'
                        ),
                        user_list=Table(
                            element=CatalogueList(api_endpoint=catalogue_endpoint + 'byprogram/' + fidelity_program.name),
                            columns=['url', 'customer'],
                            hidden_columns=['url']
                        )
                    ).show()
                with st.expander('Add user to the selected program'):
                    CatalogueCreateForm(
                        fidelity_program=FidelityProgramDetail(url=selected_programs[0]['url']).get(),
                        user_data=self.user_list
                    ).show()
        return tab1, tab2, tab3, tab4, tab5


class ShopCreateForm(Form):
    element: ShopDetail | None

    def __init__(self, owner: UserDetail):
        if owner.url is None or owner.username is None:
            raise ValueError('Cannot create a shop without an owner')
        self.element = None
        self.owner = owner
        self.name = None
        self.email = None

    def show(self) -> Any:
        with st.form("Shop init profile"):
            self.name = st.text_input(
                label="Shop name",
                placeholder="enter shop name",
            )
            self.email = st.text_input(
                label="Email address",
                placeholder="enter shop email address",
            )
            st.write(f'Owner name: {self.owner.username}')
            create_button = st.form_submit_button("Create shop")
            if create_button:
                self.element = ShopDetail(
                    api_endpoint=self.element.api_endpoint,
                    name=self.name,
                    email=self.email,
                    owner=self.owner.url,
                ).create_or_update()
