###########################
###* Capstone Project *###
###########################

import math

################
## Formatting ##
################

# ASCII escape sequences.
# Color inspiration (https://stackoverflow.com/a/33206814).
class COLOR:
    GREEN   = "\033[92m"
    CYAN    = "\033[96m"
    YELLOW  = "\033[33m"
    ENDC    = "\033[0m"

# Utility functions to colour text output.
def color_wrap(color: COLOR):
    return lambda s: color + str(s) + COLOR.ENDC

def green(s):   return color_wrap(COLOR.GREEN) (s)
def cyan(s):    return color_wrap(COLOR.CYAN)  (s)
def yellow(s):  return color_wrap(COLOR.YELLOW)(s)


############
## Labels ##
############

# A few words used throughout the program.
class Label:
    INVESTMENT  = "investment"
    BOND        = "bond"
    SIMPLE      = "simple"
    COMPOUND    = "compound"


###########
## Input ##
###########

# Routines to handle various types of input from the user.
class Input:
    # Highlight the user input
    def __highlight(prompt, input_color=COLOR.CYAN):
        print(prompt, end=input_color)
        user_input = input()
        print("", end=COLOR.ENDC)
        return user_input

    # Abstracts away the input logic.
    # Input —> Type Cast —> Transform —> Conditional —> return
    def __input(prompt, type_cast=None, input_color=None,
                condition=None, transform=None):
        while True:
            user_input = Input.__highlight(prompt, input_color).strip()

            try:
                user_input = type_cast(user_input) if type_cast else user_input
            except ValueError:
                None

            user_input = transform(user_input) if transform else user_input
            if (not condition) or condition(user_input):
                return user_input

    # Conditionals.
    __positive = lambda num: num > 0

    # Transforms.
    __round = lambda num, precision: round(num, precision)

    # Prompt the user for the type of investment.
    def investment_type(prompt):
        return Input.__input(
            prompt,
            type_cast   = int,
            input_color = COLOR.GREEN,
            condition   = lambda s: s in [Label.INVESTMENT, Label.BOND],
            transform   = lambda s: s.lower(),
        )

    # Prompt the user for the type of interest.
    def interest_type(prompt):
        return Input.__input(
            prompt,
            type_cast   = str,
            input_color = COLOR.GREEN,
            condition   = lambda s: s in [Label.SIMPLE, Label.COMPOUND],
            transform   = lambda s: s.lower(),
        )

    # Prompt the user for a float.
    def float(prompt, positive=None, precision=None):
        return Input.__input(
            prompt,
            type_cast   = float,
            input_color = COLOR.CYAN,
            condition   = Input.__positive if positive else None,
            transform   = lambda num:
                Input.__round(num, precision) if precision != None else None
        )

    # Prompt the user for an integer.
    def int(prompt, positive=None):
        return Input.__input(
            prompt,
            type_cast   = int,
            input_color = COLOR.CYAN,
            condition   = Input.__positive if positive else None,
        )


##############
## UI Flow ###
##############

# Determine the type of investment from the user.
print()
print(f"{green('{:>10}'.format(Label.INVESTMENT))} — to calculate the amount of interest you'll earn on your investment")
print(f"{green('{:>10}'.format(Label.BOND))} — to calculate the amount you'll have to pay on your home loan")
print()

investment_type = Input.investment_type(
    f"Enter either '{green(Label.INVESTMENT)}' or '{green(Label.BOND)}' from the menu above to proceed: ")
print()

if investment_type == Label.INVESTMENT:
    ################
    ## Investment ##
    ################

    # Prompt the user for the initial deposit (£), interest rate (%),
    # duration (years) and the type of interest ('simple' or 'compound')

    deposit_amount = Input.float(
        f"      Amount to {cyan('(£)')} {green('deposit')}: ",
        precision=2,
        positive=True,
    )
    interest_rate = Input.float(
        f"       Rate of {cyan('(%)')} {green('interest')}: ",
        precision=3,
        positive=True,
    )
    duration_total = Input.int(
        f"Investment {cyan('(years)')} {green('duration')}: ", positive=True
    )

    print()
    print(f"{green('{:>10}'.format(Label.SIMPLE))} — earn a fixed amount per year")
    print(f"{green('{:>10}'.format(Label.COMPOUND))} — earn interest on your interest")
    print()

    interest_type = Input.interest_type(
        f"Enter either '{green(Label.SIMPLE)}' or '{green(Label.COMPOUND)}' from the menu above to proceed: "
    )

    print()
    print(f"Press {green('Enter ↵')} to see your {green('investment projection')}")
    input()

    # Calculate and print the investment projection. This includes the duration of the investment,
    # value of investment, interest accrued (total & previous year) as well as the corresponding totals

    investment_value = deposit_amount  # Current value of the investment
    duration_current = 0  # Current year of the investment
    interest_paid = 0  # Total interest accrued
    interest_prior = 0  # Interest accrued in previous year

    # Interest accrued per year
    def interest_compound():
        return investment_value * interest_rate / 100

    def interest_simple():
        return deposit_amount * interest_rate / 100

    # Final value of the investment
    def value_compound():
        return deposit_amount * math.pow(1 + interest_rate / 100, duration_total)

    def value_simple():
        return deposit_amount * (1 + interest_rate / 100 * duration_total)

    # Select the annual interest & final value calculation
    if interest_type == Label.COMPOUND:
        interest_fn = interest_compound
        value_fn = value_compound
    elif interest_type == Label.SIMPLE:
        interest_fn = interest_simple
        value_fn = value_simple
    else:
        raise NotImplementedError(f"Unknown interest type '{interest_type}'")

    ###########
    ## Table ##
    ###########

    # TODO Abstract away table drawing logic (or delegate to an external library)
    # NOTE This logic is repeated in the 'bond' branch (below), violating the DRY principle
    # https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
    # Table design inspiration https://ozh.github.io/ascii-tables/

    # Table titles, units and corresponding widths
    titles = ["Duration", "Value", "Rel. Value", "Accrued", "Tot. Accrued"]
    units = ["Years", "£", "%", "£", "£"]
    col_width = [max(len(t) + 2, 10) for t in titles]
    total_width = sum(col_width) + (len(titles) + 1) * 3

    titles_padded = [green(f"{t:^{col_width[i]}}") for i, t in enumerate(titles)]
    titles_string = "(_)".join(titles_padded)

    units_padded = [
        cyan(f"{f'({u})':>{col_width[i] - 1}} ") for i, u in enumerate(units)
    ]
    units_string = "(_)".join(units_padded)

    # Print table header
    print(f" o8{'8' * (total_width - 6)}8o ")
    print("(_)" + yellow(f"{'Investment Projection':^{total_width - 6}}") + "(_)")
    print(f"(88{'8' * (total_width - 6)}88)")

    # Print titles and corresponding units
    print(f"(_){titles_string}(_)")
    print(f"(_){units_string}(_)")
    print(f"(88{'(_)'.join(list(map(lambda cw: '8' * cw, col_width)))}88)")

    # Print yearly duration, value, rel. value, annual interest and total interest
    while duration_current <= duration_total:
        relative_value = 100 * investment_value / deposit_amount
        print(f"(_){cyan(f'{duration_current    :>{col_width[0] - 1}} '   )}", end="")
        print(f"(_){cyan(f'{investment_value    :>{col_width[1] - 1}.2f} ')}", end="")
        print(f"(_){cyan(f'{relative_value      :>{col_width[2] - 1}.1f} ')}", end="")
        print(f"(_){cyan(f'{interest_prior      :>{col_width[3] - 1}.2f} ')}", end="")
        print(
            f"(_){cyan(f'{interest_paid       :>{col_width[4] - 1}.2f} ')}", end="(_)\n"
        )

        interest_prior = interest_fn()
        interest_paid += interest_prior
        investment_value += interest_prior
        duration_current += 1

    # Print table footer, including the interest accrued and final investment value
    print(f"(88{'8' * (total_width - 6)}88)")
    print(
        "(_)"
        + yellow(
            f"{f'Total Interest: £{value_fn() - deposit_amount:<8.2f}':^{(total_width - 6)}}"
        )
        + "(_)"
    )
    print(
        "(_)"
        + yellow(
            f"{f'   Final Value: £{value_fn()                 :<8.2f}':^{(total_width - 6)}}"
        )
        + "(_)"
    )
    print(f" O8{'8' * (total_width - 6)}8O ")

elif investment_type == Label.BOND:
    ##########
    ## Bond ##
    ##########

    ## See https://bit.ly/4aTOhvN for a *math explainer*

    # Prompt the user for the value of the house (£),
    # interest rate (%) and the duration of repayment (months)
    house_value = Input.int(
        f"            House {cyan('(£)')} {green('value')}: ", positive=True
    )
    interest_rate = Input.float(
        f"       Rate of {cyan('(%)')} {green('interest')}: ",
        precision=3,
        positive=True,
    )
    months_total = Input.int(
        f"Repayment {cyan('(months)')} {green('duration')}: ", positive=True
    )

    # Calculate the monthly interest (assuming compound)
    # TODO Evaluate interest rate transform over differing temporal domains
    # https://www.investopedia.com/articles/07/continuously_compound.asp
    monthly_interest = interest_rate / 12

    # Calculate the monthly payment and corresponding initial capital payment.
    # "Capital payment" refers to the portion of the monthly payment
    # that goes toward paying back the loan on the mortgage.
    # NOTE Capital payments increase as a geometric sequence.
    monthly_payment = (house_value * (monthly_interest / 100)) / (
        1 - (1 + monthly_interest / 100) ** (-months_total)
    )
    capital_payment = (house_value * (monthly_interest / 100)) / (
        -1 + (1 + monthly_interest / 100) ** (months_total)
    )

    # Monthly payment notification
    print()
    print(
        f"Eek! Your {green('monthly payment')} will be {yellow(f'£{monthly_payment:.2f}')}"
    )
    print()
    print(f"Press {green('Enter ↵')} to see your {green('mortage projection')}")
    input()

    ###########
    ## Table ##
    ###########

    # Table titles, units and widths
    titles = ["Duration", "Bank Loan", "Ownership", "Total Paid", "Interest Paid"]
    units = [
        "Months",
        "£",
        "£",
        "£",
        "£",
    ]
    col_width = [max(len(t) + 2, 10) for t in titles]
    total_width = sum(col_width) + (len(titles) + 1) * 3

    titles_padded = [green(f"{t:^{col_width[i]}}") for i, t in enumerate(titles)]
    titles_string = "(_)".join(titles_padded)

    units_padded = [
        cyan(f"{f'({u})':>{col_width[i] - 1}} ") for i, u in enumerate(units)
    ]
    units_string = "(_)".join(units_padded)

    # Print table header
    print(f" o8{'8' * (total_width - 6)}8o ")
    print("(_)" + yellow(f"{'Mortgage Projection':^{total_width - 6}}") + "(_)")
    print(f"(88{'8' * (total_width - 6)}88)")

    # Print titles and the corresponding units
    print(f"(_){titles_string}(_)")
    print(f"(_){units_string}(_)")
    print(f"(88{'(_)'.join(['8' * cw for cw in col_width])}88)")

    # Print monthly duration, amount loaned, ownership, total paid and interest paid
    months_accum = 0
    loaned_amount = house_value
    owned_amount = 0
    total_paid = 0
    interest_paid = 0

    while months_accum <= months_total:
        print(f"(_){cyan(f'{months_accum    :>{col_width[0] - 1}} '   )}", end="")
        print(f"(_){cyan(f'{loaned_amount   :>{col_width[1] - 1}.2f} ')}", end="")
        print(f"(_){cyan(f'{owned_amount    :>{col_width[2] - 1}.2f} ')}", end="")
        print(f"(_){cyan(f'{total_paid      :>{col_width[3] - 1}.2f} ')}", end="")
        print(f"(_){cyan(f'{interest_paid   :>{col_width[4] - 1}.2f} ')}", end="(_)\n")

        months_accum += 1
        loaned_amount -= capital_payment
        owned_amount += capital_payment
        total_paid += monthly_payment
        interest_paid += monthly_payment - capital_payment
        capital_payment *= 1 + monthly_interest / 100

    total_paid -= monthly_payment

    # Print table footer, including the interest paid and total paid
    print(f"(88{'8' * (total_width - 6)}88)")
    print(
        "(_)"
        + yellow(f"{f'Interest Paid: £{interest_paid:<8.2f}':^{(total_width - 6)}}")
        + "(_)"
    )
    print(
        "(_)"
        + yellow(f"{f'   Total Paid: £{total_paid   :<8.2f}':^{(total_width - 6)}}")
        + "(_)"
    )
    print(f" O8{'8' * (total_width - 6)}8O ")

###############
## Farewell! ##
###############

print()
input(f"Press {green('Enter ↵')} to exit")
print(
    """
___ _,_  _, _, _ _,_   , _  _, _,_   
  |  |_| /_\ |\ | |_/   \ | / \ | |   
  |  | | | | | \| | \    \| \ / | |   
  ~  ~ ~ ~ ~ ~  ~ ~ ~     )  ~  `~'   
                         ~'           
  _,  _,  _, __,  _, _, _ _, _ __, __,
 / ` / \ / _ |_) /_\ |\/| |\/| |_  |_)
 \ , \ / \ / | \ | | |  | |  | |   | \\
  ~   ~   ~  ~ ~ ~ ~ ~  ~ ~  ~ ~~~ ~ ~
"""
)
print(
    f"A wee app by {yellow('Ian Haggerty')} ({cyan('https://github.com/ianhaggerty')})"
)
print()
