backend_url = 'http://127.0.0.1:8000/'

auth_endpoint = backend_url + 'api-token-auth/'
users_endpoint = backend_url + 'users/'
shops_endpoint = backend_url + 'shops/'
fidelity_programs_endpoint = backend_url + 'fidelityprograms/'
catalogue_endpoint = backend_url + 'catalogue/'
product_endpoint = backend_url + 'product/'
transaction_endpoint = backend_url + 'transactions/'

cashback_endpoint = fidelity_programs_endpoint + 'cashbackprograms/'
levels_endpoint = fidelity_programs_endpoint + 'levelsprograms/'
points_endpoint = fidelity_programs_endpoint + 'pointsprograms/'
membership_endpoint = fidelity_programs_endpoint + 'membershipprograms/'


def coefficient_limits(program_type: str) -> tuple[float, float]:
    match program_type:
        case "CASHBACK":
            return -1.0, 0.0
        case "LEVELS":
            return 0.000, 0.010
        case "MEMBERSHIP":
            return 0.0, 0.0
        case _:
            return 0.0, 1.0
