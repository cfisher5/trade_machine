def currency(amount):
    if amount == " ":
        return ""
    if amount >= 0:
        return '${:,.2f}'.format(amount)
    else:
        return '-${:,.2f}'.format(-amount)
