from plclient.views.views import UserDashboard
from plclient.utils.settings import users_endpoint

if __name__ == '__main__':
    UserDashboard(url=users_endpoint, username='admin').open_view()
