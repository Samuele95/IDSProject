from plclient.utils.settings import users_endpoint
from views.apiclient import UserDetail
from views.views import UserDashboard, UserView, ShopView, FidelityProgramView, CatalogueView


if __name__ == '__main__':
    UserDashboard(
        UserView(UserDetail(url=users_endpoint+'admin').get()),
        ShopView(),
        FidelityProgramView(),
        CatalogueView()
    ).open_view()