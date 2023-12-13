from __future__ import annotations
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from plclient.api.catalogueapi import CatalogueDetail
from plclient.api.fidelityprogramapi import FidelityProgramDetail, FidelityProgramList
from plclient.api.shopapi import ShopDetail, ShopList
from plclient.api.userapi import UserDetail
from plclient.forms.fidelityprogramform import FidelityProgramForm, AddPrizesOrUsersToFidelityProgram, \
    CashierFidelityProgramForm, FidelityProgramCreateForm, JoinOrLeaveFidelityProgramAsBusiness
from plclient.forms.forms import Table
from plclient.utils.settings import fidelity_programs_endpoint, catalogue_endpoint
import streamlit as st
import requests

from plclient.views.catalogueviews import FidelityProgramCatalogueView
from plclient.views.productviews import CustomerProductView
from plclient.views.userviews import NoUserView


@runtime_checkable
class FidelityProgramView(Protocol):

    def open_view(self):
        ...

    def close_view(self):
        ...

    def get_fidelity_program(self, program: FidelityProgramDetail):
        ...

    def create_fidelity_program(self):
        ...

    def get_all_fidelity_programs(self):
        ...

    def get_all_fidelity_programs_by_shop(self, shopname: str):
        ...


class ReadOnlyFidelityProgramView:

    def __init__(self, user: UserDetail):
        if user.url is None or user.username is None:
            raise ValueError('User data is required')
        self.user = user

    def open_view(self):
        with st.container() as container:
            fprog_col1, fprog_col2 = st.columns(spec=2, gap='large')
            fprograms = None
            with fprog_col1:
                if fprograms is None:
                    fprograms = self.get_all_fidelity_programs().show()
                if len(fprograms.selected_rows) > 0:
                    programname = fprograms.selected_rows[0]['url']
                    if not self.user_is_joined(programname):
                        button = st.button('Join')
                        if button:
                            self.join_fidelity_program(fprograms.selected_rows[0]['url'])
                    else:
                        leave_button = st.button('Leave')
                        if leave_button:
                            self.leave_fidelity_program(programname)
            with fprog_col2:
                if len(fprograms.selected_rows) > 0:
                    programname = fprograms.selected_rows[0]['url']
                    self.get_fidelity_program(FidelityProgramDetail(url=programname).get()).show()

    def close_view(self):
        raise NotImplementedError

    def get_all_fidelity_programs(self):
        return Table(
            element=FidelityProgramList(),
            columns=['url', 'name', 'program_type'],
            hidden_columns=['url']
        )

    def get_all_fidelity_programs_by_shop(self, shopname: str):
        return Table(
            element=FidelityProgramList(api_endpoint=fidelity_programs_endpoint + 'byshop/' + shopname),
            columns=['url', 'name', 'program_type'],
            hidden_columns=['url'],
        )

    def create_fidelity_program(self):
        raise NotImplementedError

    def get_fidelity_program(self, program: FidelityProgramDetail):
        if program.url is None:
            raise ValueError('You must give a valid fidelity program')
        return FidelityProgramForm(
            element=program,
            prize_list=CustomerProductView(fidelity_program=program).get_all_products_by_program()
        )

    def user_is_joined(self, programurl: str) -> bool:
        program = FidelityProgramDetail(url=programurl).get()
        return CatalogueDetail(url=catalogue_endpoint + self.user.username + '/' + program.name).get().error is None

    def join_fidelity_program(self, programurl: str):
        try:
            CatalogueDetail(customer=self.user.url, fidelity_program=programurl).create_or_update()
            st.success('Fidelity program joined!')
        except requests.HTTPError as ex:
            return st.error(str(ex))

    def leave_fidelity_program(self, programurl: str):
        try:
            program = FidelityProgramDetail(url=programurl).get()
            CatalogueDetail(url=catalogue_endpoint + self.user.username + '/' + program.name).get().delete()
            st.success('Fidelity program left')
        except requests.HTTPError as ex:
            return st.error(str(ex))




class CashierFidelityProgramView:

    def __init__(self, shop: ShopDetail, user_view: NoUserView):
        if shop.url is None or shop.name is None:
            raise ValueError('User data is required')
        self.shop = shop
        self.user_view=user_view

    def open_view(self):
        with st.container() as container:
            fprograms = self.get_all_joined_fidelity_programs_by_business().show()
            if len(fprograms.selected_rows) > 0:
                programname = fprograms.selected_rows[0]['url']
                self.get_fidelity_program(FidelityProgramDetail(url=programname).get()).show()

    def close_view(self):
        raise NotImplementedError

    def get_all_fidelity_programs(self):
        return Table(
            element=FidelityProgramList(),
            columns=['url', 'name', 'program_type'],
            hidden_columns=['url']
        )

    def get_all_joined_fidelity_programs_by_business(self):
        return self.get_all_fidelity_programs_by_shop(self.shop.name)


    def get_all_fidelity_programs_by_shop(self, shopname: str):
        return Table(
            element=FidelityProgramList(api_endpoint=fidelity_programs_endpoint + 'byshop/' + shopname),
            columns=['url', 'name', 'program_type'],
            hidden_columns=['url'],
        )

    def create_fidelity_program(self):
        raise NotImplementedError

    def get_fidelity_program(self, program: FidelityProgramDetail):
        if program.url is None or program.name is None:
            raise ValueError('You must give a valid fidelity program')
        return AddPrizesOrUsersToFidelityProgram(
            decorated=CashierFidelityProgramForm(
                element=program,
                prize_list=CustomerProductView(fidelity_program=program).get_all_products_by_program(),
                user_list=FidelityProgramCatalogueView(program=program).get_all_catalogue_elements_by_fidelity_program()
            ),
            shop=self.shop,
            all_users=self.user_view.get_all_users()
        )


    def join_fidelity_program(self, programurl: str):
        raise NotImplementedError

    def leave_fidelity_program(self, programname: str):
        raise NotImplementedError

class BusinessOwnerFidelityProgramView:

    def __init__(self, shop: ShopDetail, user_view: NoUserView):
        if shop.url is None or shop.name is None:
            raise ValueError('User data is required')
        self.shop = shop
        self.user_view = user_view

    def open_view(self):
        with st.container() as container:
            fprog_col1, fprog_col2 = st.columns(spec=2, gap='large')
            fprograms = None
            with fprog_col1:
                if fprograms is None:
                    fprograms = self.get_all_fidelity_programs().show()
                with st.expander('Create fidelity program'):
                    FidelityProgramCreateForm(self.shop).show()
            with fprog_col2:
                if len(fprograms.selected_rows) > 0:
                    programname = fprograms.selected_rows[0]['url']
                    self.get_fidelity_program(FidelityProgramDetail(url=programname).get()).show()

    def close_view(self):
        raise NotImplementedError

    def get_all_fidelity_programs(self):
        return Table(
            element=FidelityProgramList(),
            columns=['url', 'name', 'program_type'],
            hidden_columns=['url'],
        )

    def get_all_joined_fidelity_programs_by_business(self):
        return self.get_all_fidelity_programs_by_shop(self.shop.name)


    def get_all_fidelity_programs_by_shop(self, shopname: str):
        return Table(
            element=FidelityProgramList(api_endpoint=fidelity_programs_endpoint + 'byshop/' + shopname),
            columns=['url', 'name', 'program_type'],
            hidden_columns=['url'],
        )

    def create_fidelity_program(self):
        raise NotImplementedError

    def get_fidelity_program(self, program: FidelityProgramDetail):
        if program.url is None or program.name is None:
            raise ValueError('You must give a valid fidelity program')
        return JoinOrLeaveFidelityProgramAsBusiness(
            decorated=CashierFidelityProgramForm(
                element=program,
                prize_list=CustomerProductView(fidelity_program=program).get_all_products_by_program(),
                user_list=FidelityProgramCatalogueView(program=program).get_all_catalogue_elements_by_fidelity_program()
            ),
            shop=self.shop,
            is_joined=self.shop_is_joined(program)
        )

    def shop_is_joined(self, fidelity_program: FidelityProgramDetail):
        return self.shop.url in fidelity_program.shop_list

    def join_fidelity_program(self, programurl: str):
        raise NotImplementedError

    def leave_fidelity_program(self, programname: str):
        raise NotImplementedError