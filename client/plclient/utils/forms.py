import streamlit as st
from dataclasses import dataclass
from streamlit_extras.switch_page_button import switch_page
from project_loyalty_client.utils.apiclient import User, FidelityProgram, Product
from project_loyalty_client.utils.settings import appimage

class LoginForm:

    def __init__(self, token=None, user_url=None, app_url=None):
        self.token = token
        self.user_url = token
        self.app_url = token

    def login_form(self):
        with st.form('Login form'):
            username = st.text_input(
                label='Username', 
                placeholder='enter username',
            )
            password = st.text_input(
                label='Password',
                placeholder='enter password',
                type='password',
            )
            submitted = st.form_submit_button('Submit')
            if submitted: 
                result = User(username=username, password=password).authenticate()
                if 'error' in result:
                    st.error(result['error'])
                else:
                    self.token = result['token']
                    self.user_url = result['url']
            self.enter_app()

    def signup_form(self):
        with st.form('Signup form'):
            username = st.text_input(
                label='Username', 
                placeholder='enter username',
            )
            email = st.text_input(
                label='Email address', 
                placeholder='enter email',
            )
            password = st.text_input(
                label='Password',
                placeholder='enter password',
                type='password',
            )
            confirm_password = st.text_input(
                label='Confirm password',
                placeholder='enter password again',
                type='password',
            )
            submitted = st.form_submit_button('Submit')
            if submitted: 
                User(username=username, password=password, email=email).register_user(confirm_password)

    def show(self):
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
        st.columns(3)[1].image(appimage)
        login_tab, signup_tab = st.tabs(["Login", "Signup"])
        with login_tab:
            self.login_form()
        with signup_tab:
            self.signup_form()

    def enter_app(self):
        if self.token is not None and self.user_url is not None:
            st.session_state['token'] = self.token
            st.session_state['user_url'] = self.user_url
            switch_page('dashboard')   

@dataclass(frozen=True, eq=True, order=True)
class AddProductForm:
    shop_url : str

    def show(self):
        with st.form('add_product_form'):
            prod_name = st.text_input(
                label='Product name', 
                placeholder='enter product name',
            )
            value = st.slider(
                label='Value',
                min_value=0.0,
                max_value=5.0,
                value=2.5,
                step=0.5
            )
            points_coefficient = st.slider(
                label='Points coefficient',
                min_value=-1.0,
                max_value=1.0,
                value=0.0,
                step=0.05
            )
            prize_coefficient = st.slider(
                label='Prize coefficient',
                min_value=-1.0,
                max_value=1.0,
                value=0.0,
                step=0.05
            )
            st.text('Associate to fidelity programs:')
            fprograms = FidelityProgram().get_all(self.shop_url+'joinedfidelityprograms/', ['name', 'program_type', 'description'], is_list=True)
            submitted = st.form_submit_button('Submit')
            if submitted: 
                Product(
                    name=prod_name, 
                    value=value, 
                    points_coefficient=points_coefficient, 
                    prize_coefficient=prize_coefficient, 
                    shop=self.shop_url).store()
                st.rerun()

@dataclass(frozen=True, eq=True, order=True)
class EmailForm:
    from_addr : str
    to_addr : str

    def show(self):
        with st.form('send_email'):
            st.text(f'From: {self.from_addr}')
            st.text(f'To: {self.to_addr}')
            st.text_input(
                label='Subject',
                placeholder='enter the subject',
            )
            st.text_area(
                label='Body',
                placeholder='enter text',
            )
            submitted = st.form_submit_button('Submit')