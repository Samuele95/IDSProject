import streamlit as st
import pandas as pd
import random
import string
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from plclient.utils.settings import users_endpoint, shops_endpoint, fidelity_programs_endpoint
from views.apiclient import APIClient, APIClientDetail, APIClientList, UserDetail, ShopDetail, UserList, ShopList, FidelityProgramDetail, FidelityProgramList, CatalogueDetail
from st_aggrid import AgGrid, GridOptionsBuilder

@runtime_checkable
class UIElement(Protocol):
    def show(self):
        ...


class Form(ABC):
    element : APIClientDetail

    @abstractmethod
    def show(self):
        pass

@dataclass(frozen=True, eq=True, order=True)
class Table:
    element : APIClientList
    columns : list[str]
    hidden_columns : list[str] | None = None
    selection_mode: str = field(default='single')


    def show(self):
        data = self.element.get()
        if len(data) == 0:
            st.text(f'No data registered yet!')
            return 
        df = pd.DataFrame.from_dict(data)[self.columns]
        builder = GridOptionsBuilder.from_dataframe(df)
        builder.configure_selection(selection_mode=self.selection_mode)
        if self.hidden_columns is not None:
            builder.configure_columns(column_names=self.hidden_columns, hide=True)
        go = builder.build()
        filtered_df = AgGrid(df, gridOptions=go, fit_columns_on_grid_load=True, theme='material')
        st.write(filtered_df.selected_rows)   
        return filtered_df


@dataclass(eq=True, order=True)
class UserForm(Form):
    element : UserDetail
    disable_button : bool = True

    def show(self):
        with st.form('User profile'):
            self.username = st.text_input(
                label='Username', 
                value=self.element.username,
                placeholder='enter your username',
                disabled=True,
            )
            self.email = st.text_input(
                label='Email address', 
                value=self.element.email, 
                placeholder='enter your email address',
                disabled=self.disable_button
            )
            self.location = st.text_input(
                label='Location', 
                value=self.element.location, 
                placeholder='enter your location',
                disabled=self.disable_button
            )
            self.bio = st.text_area(
                label='Bio', 
                value=self.element.bio, 
                placeholder='enter a small description',
                disabled=self.disable_button
            )
            self.update_button = st.form_submit_button('Update', disabled=self.disable_button)

@dataclass(eq=True, order=True)
class UserUpdateForm:
    decorated : UserForm

    def show(self):
        self.decorated.disable_button=False
        self.decorated.show()
        if self.decorated.update_button:
            UserDetail(
                api_endpoint = self.decorated.element.api_endpoint,
                url = self.decorated.element.url,
                username=self.decorated.username,
                password=self.decorated.element.password,
                email=self.decorated.email,
                location=self.decorated.location,
                bio=self.decorated.bio
            ).create_or_update()

@dataclass(eq=True, order=True)
class UserCreateForm(Form):
    element : UserDetail

    def show(self):
        with st.form('User create'):
            self.username = st.text_input(
                label='Username', 
                placeholder='enter your username',
                disabled=True,
            )
            self.email = st.text_input(
                label='Email address', 
                placeholder='enter your email address',
            )
            self.password = st.text_input(
                label='New password',
                placeholder='enter yout new password',
                type='password',
            )
            self.confirm_password = st.text_input(
                label='Confirm password',
                placeholder='enter password again',
                type='password',
            )
            self.update_button = st.form_submit_button('Create')
            if self.decored.update_button:
                    UserDetail(
                        api_endpoint = self.element.api_endpoint,
                        username=self.username,
                        password=self.password,
                        confirm_password=self.confirm_password,
                        email=self.email,
                    ).create_or_update()


@dataclass(eq=True, order=True)
class UserSetPasswordForm(Form):
    element : UserDetail

    def show(self):
        with st.form('User password update'):
            self.password = st.text_input(
                label='New password',
                placeholder='enter yout new password',
                type='password',
            )
            self.confirm_password = st.text_input(
                label='Confirm password',
                placeholder='enter password again',
                type='password',
            )
            self.update_button = st.form_submit_button('Change password')
            if self.update_button:
                    UserDetail(
                        api_endpoint = self.element.api_endpoint,
                        url=self.element.url,
                        username=self.element.username,
                        password=self.password,
                        confirm_password=self.confirm_password
                    ).create_or_update()

@dataclass(eq=True, order=True)
class ShopForm(Form):
    element : ShopDetail

    def show(self):
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Info", "Products", "Reviews", "Contact us", "Owner", "Employees", 'Joined Fidelity Programs'])
        with tab1:
            shop_name = st.text_input(
                label='Shop name', 
                value=self.element.name,
                placeholder='enter shop name',
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )

            shop_location = st.text_area(
                label='Location', 
                value=self.element.location, 
                placeholder='enter shop location',
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )

            
        with tab4:
            with st.expander('Phone'):
                shop_number = st.text_input(
                    label='Phone number', 
                    value=self.element.phone,
                    placeholder='enter phone number',
                    disabled=True,
                    key=random.choices(string.ascii_lowercase, k=5),
                    label_visibility='collapsed'
                )

        with tab5:
            if self.element.owner is not None:
                UserForm(UserDetail(api_endpoint=users_endpoint, url=self.element.owner).get()).show()
                
@dataclass(eq=True, order=True)
class ShopCreateForm(Form):
    element : ShopDetail

    def show(self):
        with st.form('Shop init profile'):
            self.name = st.text_input(
                label='Shop name', 
                placeholder='enter shop name',
            )
            self.email = st.text_input(
                label='Email address', 
                placeholder='enter shop email address',
            )
            self.owner = st.text_input(
                label='Owner username', 
                value= UserDetail(api_endpoint=users_endpoint, url=self.element.owner).get().username if self.element.owner else '',  
                placeholder='enter your location',
            )
            self.create_button = st.form_submit_button('Create shop')
            if self.create_button:
                ShopDetail(
                    api_endpoint = self.element.api_endpoint,
                    name=self.name,
                    email=self.email,
                    owner=shops_endpoint+self.owner
                ).create_or_update()

@dataclass(frozen=True, eq=True, order=True)
class FidelityProgramForm(Form):
    element : FidelityProgramDetail

    def show(self):
        match self.element.program_type:
            case 'CASHBACK':
                box_index = 0
            case 'LEVELS':
                box_index = 1
            case 'POINTS':
                box_index = 2
            case _:
                box_index = 3
        tab1, tab2, tab3, tab4 = st.tabs(["Info", "Prizes", "Joined Shops", "Users and stats"])
        with tab1:
            program_name = st.text_input(
                label='Program name', 
                value=self.element.name,
                placeholder='enter program name',
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )
            program_type = st.selectbox(
                label='Program Type',
                options=('CASHBACK', 'LEVELS', 'POINTS', 'GENERIC'),
                index=box_index,
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )

            program_des = st.text_area(
                label='Bio', 
                value=self.element.description, 
                placeholder='enter a small description',
                disabled=True,
                key=random.choices(string.ascii_lowercase, k=5)
            )
        #with tab2:
        #    prizes = get_all_request(url+'prizes/', ['name', 'value', 'shop'], is_list=True)
        with tab3:
            shops = Table(element=ShopList(data=self.element.shop_list, datainstance=ShopDetail), columns=['url', 'name'], hidden_columns=['url']).show() 

        #with tab4:
        #    st.subheader('Joined users:')
        #    users = get_all_request(url+'users/', ['customer', 'points'], is_list=True)
        #    st.subheader('Your stats:')
        #    df = pd.DataFrame.from_dict(requests.get('http://127.0.0.1:8000/catalogue/').json()['results'])
        #    fdf = df.loc[df['customer'].str.contains(st.session_state.userurl)]
        #    if fdf.empty:
        #        st.write('You are not registered to this fidelity program')
        #    else: 
        #        current_user = fdf.iloc[0]['url']
        #        st.write(user_stats_in_fidelity_program(current_user))
            #print(get_all_request('http://127.0.0.1:8000/catalogue/', ['url', 'id', 'customer', 'fidelity_program']))

@dataclass(eq=True, order=True)
class FidelityProgramCreateForm(Form):
    element : FidelityProgramDetail

    def show(self):
        with st.container():
            ptype = st.selectbox(
                label='Fidelity program type',
                options=['GENERIC', 'CASHBACK', 'POINTS', 'LEVELS', 'MEMBERSHIP'],
            )
            name = st.text_input(
                label='Fidelity program name', 
                placeholder='enter program name',
            )
            desc = st.text_area(
                label='Description',
                placeholder='enter a description'
            )
            min_lim, max_lim = self.coefficient_limits(ptype)
            if min_lim != max_lim:
                points_coefficient = st.slider(
                    label='Points coefficient',
                    min_value=min_lim,
                    max_value=max_lim,
                    value=(min_lim+max_lim)/2,
                    step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
                    format='%.4f'
                )
                prize_coefficient = st.slider(
                    label='Prize coefficient',
                    min_value=min_lim,
                    max_value=max_lim,
                    value=(min_lim+max_lim)/2,
                    step=max(abs(min_lim), abs(max_lim)) * 5 / 100,
                    format='%.4f'
                )
            #st.text('Associate to shops:')
            #shops = get_df_filtered(url+'/shops/', ['url', 'name', 'location'])
            #shoplst = []
            #if shops.size != 0:
            #    for sh in shops.loc[:,'url']:
            #        shoplst.append(sh)
            #st.button('Submit', on_click=store_review_data(userurl, shopurl, rating, content))
            submitted = st.button('Submit')
            if submitted: 
                type(self.element)(
                    api_endpoint=self.element.api_endpoint,
                    name=name, 
                    program_type=ptype,
                    description=desc, 
                    points_coefficient=points_coefficient/100,
                    prize_coefficient=prize_coefficient/100,
                    shoplist=self.element.shop_list
                ).create_or_update
    
    def coefficient_limits(self, program_type: str):
        match program_type:
            case 'CASHBACK':
                return (-1.0, 0.0)
            case 'LEVELS':
                return (0.000, 0.010)
            case 'MEMBERSHIP':
                return (0.0, 0.0)
            case _:
                return (0.0, 1.0)

@dataclass(eq=True, order=True)
class CatalogueForm(Form):
    element : CatalogueDetail

    def show(self):
        with st.container() as container:
            if self.element.url is None:
                st.write('No catalogue element to be shown!')
            self.username = st.text_input(
                label='User', 
                value=UserDetail(url=self.element.customer).get().username,
                placeholder='enter your username',
                disabled=True,
                key=str(self.element)+'1'
            )
            self.fidelity_program = st.text_input(
                label='Fidelity Program', 
                value=FidelityProgramDetail(url=self.element.fidelity_program).get().name, 
                placeholder='enter your email address',
                disabled=True,
                key=str(self.element)+'2'
            )
            self.points = st.write(f'Points: {self.element.points}')

@dataclass(eq=True, order=True)
class CatalogueCreateForm(Form):
    element : CatalogueDetail
    user : str | None = None
    fidelity_program : str | None = None

    def show(self):
        with st.container() as container:
            with st.expander('Select user'):
                if self.user is None:
                    users = Table(UserList(), ['url', 'username'], {'url':None}).show()
                    self.user = users.selected_rows[0]['url'] if len(users.selected_rows) > 0 else None
            with st.expander('Select fidelity program'):
                if self.fidelity_program is None:
                    fidelity_programs = Table(FidelityProgramList(), ['url', 'name', 'program_type'], {'url':None}).show()
                    self.fidelity_program = fidelity_programs.selected_rows[0]['url'] if len(fidelity_programs.selected_rows) > 0 else None
            self.create_button = st.button('Create catalogue element')
            if self.create_button and self.user is not None and self.fidelity_program is not None:
                st.write(self.user)
                st.write(self.fidelity_program)
                CatalogueDetail(
                    customer=self.user,
                    fidelity_program=self.fidelity_program,
                ).create_or_update()

@dataclass(eq=True, order=True)
class CatalogueUpdateForm:
    decorated : CatalogueForm

    def show(self):
        self.decorated.show()
        new_pts = st.text_input(
            label='New points', 
            key=str(self.decorated)
        )
        self.update_button = st.button('Update catalogue element')
        if self.update_button:
            points_number = float(new_pts)
            CatalogueDetail(
                url=self.decorated.element.url,
                customer=self.decorated.element.customer,
                fidelity_program=self.decorated.element.fidelity_program,
                points=points_number if points_number >= 0 else 0.0
            ).create_or_update()        

                    
