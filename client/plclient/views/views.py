from __future__ import annotations
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from streamlit_option_menu import option_menu
from plclient.utils.settings import users_endpoint, shops_endpoint, fidelity_programs_endpoint, catalogue_endpoint
from views.uiform import UserForm, UserCreateForm, UserSetPasswordForm, Table, ShopForm, FidelityProgramForm, FidelityProgramCreateForm, CatalogueForm, CatalogueCreateForm, CatalogueUpdateForm
from views.apiclient import UserDetail, UserList, ShopDetail, ShopList, FidelityProgramDetail, FidelityProgramList, CatalogueDetail, CatalogueList
import streamlit as st

@runtime_checkable
class View(Protocol):
    """
    Interface representing a UI which the user can interact with.
    At startup, the view is opened through the open_view function, 
    which shows all the available data and info.
    At logout, the view is closed through the close_view function.
    """

    def open_view(self):
        ...

    def close_view(self):
        ...


@dataclass(frozen=True, eq=True, order=True)
class UserDashboard:
    """
    ClientView instance of a user which doesn't have 
    administrative privileges. It may be associated 
    to both a customer and a business user.
    """

    user_view : UserView
    shop_view : ShopView
    fidelity_program_view : FidelityProgramView
    catalogue_view : CatalogueView

    def open_view(self):
        st.title('Project Loyalty Platform')
        self.sideBar()
    
    def close_view(self):
        st.write('LOGOUT')

    def home(self):
        return self.user_view.open_view() 

    def sideBar(self): 
        with st.sidebar as sidebar:
            selected=option_menu(
                menu_title="Main Menu",
                options=['Home', 'Shops', 'Fidelity Programs', 'Logout'],
                icons=['house', 'cart', 'people', 'dash-circle'],
                menu_icon="cast",
                default_index=0
            )
        if selected=="Home":
            self.home()
        if selected=='Shops':
            self.shop_view.open_view()
        if selected=='Fidelity Programs':
            self.fidelity_program_view.open_view()
                    #st.write(fprograms)
                #with fprog_col2:
                #    if fprograms.size != 0:
                        #for prog in fprograms.loc[2:3,'url']:
                #            st.write(FidelityProgramDetail(fprograms.iloc[0].to_dict()['url']))
        if selected=='Logout':
            self.close_view()


@dataclass(frozen=True, eq=True, order=True)
class UserView:
    user : UserDetail

    def open_view(self):
        home_col1, home_col2 = st.columns(2)
        with home_col1:
            user_profile, change_password = st.tabs(['User profile', 'Change password'])
            with user_profile:
                self.get_self_user().show()
            with change_password:
                UserSetPasswordForm(self.user).show()
        with home_col2:
            st.markdown("Welcome to Project Loyalty Platfom.\nThis platform aims to provide a common hub in which commercial businesses present themselves to the public and communicate with each other and with the customers themselves.\nCommercial establishments can join together in common loyalty programmes, channels constituting a way through which a customer is able to obtain economic advantages and rewards thanks to the loyalty towards the commercial establishment or the consortium of companies participating in the program itself, while commercial businesses can adopt strategies aimed at retaining existing customers and obtaining new ones.\nFor further clarification and for additional information, send an email to projectloyalty@gmail.com")

    def close_view(self):
        raise NotImplementedError

    def get_user(self, username: str):
        return UserForm(UserDetail(url=users_endpoint+username).get())
    
    def get_self_user(self):
        return UserForm(self.user)
    
    def user_create_form(self):
        return UserCreateForm(UserDetail)

@dataclass(frozen=True, eq=True, order=True)
class ShopView:
    shop : ShopDetail | None = None

    def open_view(self):
        all_shops, selected_shop = st.columns(2)
        with all_shops:
            shops = self.get_all_shops().show()
        with selected_shop:
            if len(shops.selected_rows) > 0:
                self.get_shop(shops.selected_rows[0]['name']).show()

    def close_view(self):
        raise NotImplementedError

    def get_shop(self, shopname: str):
        return ShopForm(ShopDetail(url=shops_endpoint+shopname).get())
    
    def get_session_shop(self):
        return ShopForm(self.shop) if self.shop is not None else st.write('No shop associated to this user')
    
    def get_all_shops(self):
        return Table(element=ShopList(), columns=['url', 'name', 'location'], hidden_columns=['url'])

@dataclass(frozen=True, eq=True, order=True)
class FidelityProgramView:

    def open_view(self):
        with st.container() as container:
            fprog_col1, fprog_col2 = st.columns(spec=2, gap='large')
            fprograms = None
            with fprog_col1:
                if fprograms is None:
                    fprograms = self.get_all_fidelity_programs().show()
            with fprog_col2:
                if len(fprograms.selected_rows) > 0:
                    st.write(self.get_fidelity_program(fprograms.selected_rows[0]['name']).show())

    def close_view(self):
        raise NotImplementedError

    def get_all_fidelity_programs(self):
        return Table(element=FidelityProgramList(), columns=['url', 'name', 'program_type'], hidden_columns=['url'])

    def get_all_fidelity_programs_by_shop(self, shopname: str):
        return Table(element=FidelityProgramList(api_endpoint=fidelity_programs_endpoint+'byshop/'+shopname), columns=['url', 'name', 'program_type'], hidden_columns=['url'])
    
    def create_fidelity_program(self):
        return FidelityProgramCreateForm(FidelityProgramDetail())
    
    def get_fidelity_program(self, programname: str):
        return FidelityProgramForm(FidelityProgramDetail(url=fidelity_programs_endpoint+programname).get())
    

@dataclass(frozen=True, eq=True, order=True)
class CatalogueView:

    def create_catalogue_element(self):
        return CatalogueCreateForm(CatalogueDetail())
    
    def get_all_catalogue_elements(self):
        return Table(element=CatalogueList(), columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])

    def get_all_catalogue_elements_by_user(self, username: str):
        return Table(element=CatalogueList(api_endpoint=catalogue_endpoint+username), columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])
    
    def get_all_catalogue_elements_by_fidelity_program(self, programname: str):
        return Table(element=CatalogueList(api_endpoint=catalogue_endpoint+programname), columns=['url', 'customer', 'fidelity_program'], hidden_columns=['url'])
    
    def get_catalogue_element(self, username: str, programname: str):
        return CatalogueForm(CatalogueDetail(api_endpoint=catalogue_endpoint+username+'/'+programname).get())
    
    def delete_catalogue_element(self, username: str, programname: str):
        return self.get_catalogue_element(username, programname).element.delete()

    def update_catalogue_element(self, username: str, programname: str):
        return CatalogueUpdateForm(self.get_catalogue_element(username, programname))