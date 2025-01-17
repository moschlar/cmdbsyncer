"""
Helper to get Account
"""
from mongoengine.errors import DoesNotExist
from application.models.account import Account


def get_account_by_name(name):
    """
    Get Account by Name or Return False
    """

    try:
        account_dict = dict(Account.objects.get(name=name, enabled=True).to_mongo())
        for field, value  in [(x['name'], x['value']) for x in account_dict['custom_fields']]:
            account_dict[field] = value
        del account_dict['custom_fields']
        account_dict['id'] = str(account_dict['_id'])
        return account_dict
    except DoesNotExist:
        return False


def get_account_variable(macro):
    """
    Replaces the given Macro with the Account data
    Example: {{ACCOUNT:mon:password}}
    """
    # @TODO: Cache
    _, account, var = macro.split(':')
    try:
        return get_account_by_name(account)[var[:-2]]
    except:
        raise ValueError("Account Variable not found")
