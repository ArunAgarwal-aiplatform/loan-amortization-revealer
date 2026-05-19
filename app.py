import argparse
import sys


def get_interactive_input():
    
    print("\n" + "=" * 60)
    print("        LOAN AMORTIZATION REVEALER")
    print("=" * 60)
    print("\n  Please enter your loan details below:\n")

    # --- 1. Get Loan Amount ---
    while True: 
        try:     
            loan_input = input("  [1/4] Loan Amount (e.g., 500000): ").strip()
            
        
            loan_input = loan_input.replace(",", "")
            loan_amount = float(loan_input) # Convert text to a decimal number
            
            if loan_amount <= 0:
                print("         -> Loan must be greater than 0!\n")
                continue 
            break 
            
        except ValueError: 
            print("         -> Oops! Please enter valid numbers only.\n")

    # --- 2. Get Interest Rate ---
    while True:
        try:
            rate_input = input("  [2/4] Annual Interest Rate (e.g., 8.5): ").strip()
            interest_rate = float(rate_input)
            
            if interest_rate < 0:
                print("         -> Interest rate cannot be negative!\n")
                continue
            break
        except ValueError:
            print("         -> Oops! Please enter valid numbers only.\n")

    # --- 3. Get Tenure (Months) ---
    while True:
        try:
            tenure_input = input("  [3/4] Tenure in Months (e.g., 240 for 20 years): ").strip()
            tenure_months = int(tenure_input) 
            
            if tenure_months <= 0:
                print("         -> Tenure must be greater than 0!\n")
                continue
            break
        except ValueError:
            print("         -> Oops! Please enter whole numbers only.\n")

    # --- 4. Ask for Prepayment Months (Optional) ---
    print("\n  [4/4] Enter months to check prepay cost (optional)")
    print("         Example: 6 12 24 60  (or just press Enter to skip)\n")
    prepay_input = input("  Prepay months: ").strip()
    
    prepay_months = []
    if prepay_input: # If they didn't just press Enter
        for part in prepay_input.split():
            try:
                m = int(part)
                if 1 <= m < tenure_months:
                    prepay_months.append(m) # Add to our list
            except ValueError:
                pass # If they typed a letter here, just ignore it quietly
        
        if prepay_months:
            prepay_months = sorted(set(prepay_months))

    # --- 5. Ask if they want the giant table printed ---
    no_table = False
    while True:
        show_table = input("  Show full month-by-month table? (Y/n): ").strip().lower()
        if show_table in ('', 'y', 'yes'):
            break
        elif show_table in ('n', 'no'):
            no_table = True
            break

    # We pack all their answers into a dictionary (like a labeled box) and return it
    return {
        'loan_amount': loan_amount,
        'interest_rate': interest_rate,
        'tenure_months': tenure_months,
        'prepay_months': prepay_months,
        'no_table': no_table
    }



def calculate_emi(principal, annual_rate, tenure_months):
    if annual_rate == 0:
        return principal / tenure_months 
   
    monthly_rate = annual_rate / 12 / 100 
    numerator = principal * monthly_rate * (1 + monthly_rate) ** tenure_months
    denominator = (1 + monthly_rate) ** tenure_months - 1
    
    return numerator / denominator


def build_amortization_table(principal, annual_rate, tenure_months):
    
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12 / 100
    
    
    table = []
    
   
    remaining_balance = principal  # At start, you owe the full loan
    cumulative_interest = 0.0      # At start, you've paid 0 interest
    crossover_month = None         # We haven't found the crossover yet
    
 
    for month in range(1, tenure_months + 1):
        interest_component = remaining_balance * monthly_rate
        
        principal_component = emi - interest_component
        
        # 3. Fix for the very last month (to avoid 1-rupee rounding errors)
        if month == tenure_months:
            principal_component = remaining_balance
            interest_component = emi - principal_component
            if interest_component < 0:
                interest_component = 0.0
        
       
        cumulative_interest += interest_component
        
        remaining_balance -= principal_component
        
        # Don't let balance go below zero because of math rounding
        if remaining_balance < 0.01:
            remaining_balance = 0.0
     
        if crossover_month is None and principal_component > interest_component:
            crossover_month = month # Save this month number!
        
        # 6. LIST BUILDING - .append()
        # Put all this month's data into a dictionary, and add it to our list
        table.append({
            'month': month,
            'emi': emi,
            'principal': principal_component,
            'interest': interest_component,
            'cumulative_interest': cumulative_interest,
            'remaining_balance': remaining_balance
        })

    return emi, table, crossover_month


def calculate_prepay_cost(table, prepay_months, penalty_rate=0.02):
    
    results = []
    
    for month in prepay_months:
        if month < 1 or month > len(table):
            continue # Skip invalid months
            
        month_data = table[month - 1] # -1 because lists start at index 0
        remaining_balance = month_data['remaining_balance']
        interest_paid_till_date = month_data['cumulative_interest']
        
        penalty = remaining_balance * penalty_rate
        total_prepay_cost = remaining_balance + penalty
        
        # How much interest do you save by not paying the future months?
        future_interest = sum(row['interest'] for row in table[month:])
        savings = future_interest - penalty
        
        results.append({
            'month': month,
            'remaining_balance': remaining_balance,
            'interest_paid': interest_paid_till_date,
            'penalty': penalty,
            'total_cost': total_prepay_cost,
            'savings': savings
        })
        
    return results



def format_currency(amount):
    """Converts boring numbers like 5000000 into readable '₹50.00 L' (Lakhs)"""
    if amount >= 10000000: # 1 Crore
        return f"₹{amount / 10000000:.2f} Cr"
    elif amount >= 100000: # 1 Lakh
        return f"₹{amount / 100000:.2f} L"
    else:
        return f"₹{amount:,.2f}"


def print_header(principal, annual_rate, tenure_months, emi):
    """Prints the nice box at the top with loan summary."""
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    interest_percentage = (total_interest / principal) * 100

    print("\n" + "=" * 85)
    print(f"{'LOAN AMORTIZATION REVEALER':^85}") # ^85 means center it in 85 spaces
    print("=" * 85)

    # Drawing the box using simple text characters
    print(f"\n┌{'─' * 83}┐")
    print(f"│{'LOAN DETAILS':^83}│")
    print(f"├{'─' * 83}┤")
    print(f"│  {'Loan Amount:':<30} {format_currency(principal):>50} │")
    print(f"│  {'Annual Interest Rate:':<30} {annual_rate:>49.2f}% │")
    print(f"│  {'Loan Tenure:':<30} {tenure_months:>39} months │")
    print(f"│  {'Tenure (Years):':<30} {tenure_months / 12:>39.1f} years │")
    print(f"├{'─' * 83}┤")
    print(f"│{'EMI BREAKDOWN':^83}│")
    print(f"├{'─' * 83}┤")
    print(f"│  {'Monthly EMI:':<30} {format_currency(emi):>50} │")
    print(f"│  {'Total Payment:':<30} {format_currency(total_payment):>50} │")
    print(f"│  {'Total Interest:':<30} {format_currency(total_interest):>50} │")
    print(f"│  {'Interest as % of Loan:':<30} {interest_percentage:>49.2f}% │")
    print(f"└{'─' * 83}┘")


def print_amortization_table(table, crossover_month):
   
    print(f"\n{'─' * 85}")
    print(f"{'MONTH-BY-MONTH AMORTIZATION TABLE':^85}")
    print(f"{'─' * 85}")

    header = (
        f"{'Month':>6} │ {'EMI':>12} │ {'Principal':>12} │ "
        f"{'Interest':>12} │ {'Cum.Int':>12} │ {'Balance':>14}"
    )
    print(header)
    print(f"{'─' * 6}─┼─{'─' * 12}─┼─{'─' * 12}─┼─{'─' * 12}─┼─{'─' * 12}─┼─{'─' * 14}")

    # Loop through the list we built earlier and print each row
    for row in table:
        month = row['month']
        is_crossover = (month == crossover_month)
        
        if is_crossover:
            # Print in green color if it's the crossover month
            line = (
                f"{'>>>':>6} │ {row['emi']:>12,.2f} │ {row['principal']:>12,.2f} │ "
                f"{row['interest']:>12,.2f} │ {row['cumulative_interest']:>12,.2f} │ "
                f"{row['remaining_balance']:>14,.2f}"
            )
            # \033[92m is a secret code to turn terminal text green
            print(f"\033[92m{line}\033[0m <-- HERE! Principal > Interest")
        else:
            # Normal row
            line = (
                f"{month:>6} │ {row['emi']:>12,.2f} │ {row['principal']:>12,.2f} │ "
                f"{row['interest']:>12,.2f} │ {row['cumulative_interest']:>12,.2f} │ "
                f"{row['remaining_balance']:>14,.2f}"
            )
            print(line)

    print(f"{'─' * 85}")


def print_highlights(table, crossover_month, principal, emi):
    """Prints the text insights below the table."""
    total_interest = table[-1]['cumulative_interest']

    print(f"\n{'─' * 85}")
    print(f"{'KEY HIGHLIGHTS':^85}")
    print(f"{'─' * 85}")

    if crossover_month:
        crossover_data = table[crossover_month - 1]
        years = crossover_month // 12
        months_rem = crossover_month % 12
        time_str = f"{years}y {months_rem}m" if years > 0 else f"{crossover_month}m"

        print(f"\n  [!] CROSSOVER POINT: Month {crossover_month} ({time_str})")
        print(f"      At this point, your principal component ({format_currency(crossover_data['principal'])})")
        print(f"      finally exceeds your interest component ({format_currency(crossover_data['interest'])})!")
        print(f"      Interest already lost to bank: {format_currency(crossover_data['cumulative_interest'])}")
        print(f"      Remaining balance:             {format_currency(crossover_data['remaining_balance'])}")
    else:
        print(f"\n  [!] No crossover point found (interest is always >= principal)")

    print(f"\n  [$] TOTAL INTEREST ANALYSIS:")
    print(f"      Total Interest Paid: {format_currency(total_interest)}")
    print(f"      You borrowed {format_currency(principal)}, but pay back {format_currency(principal + total_interest)}")
    print(f"      Interest Multiple:   {total_interest / principal:.2f}x of principal")


def print_prepay_analysis(prepay_results):
    """Prints the table showing what happens if you prepay."""
    print(f"\n{'─' * 85}")
    print(f"{'PREPAYMENT COST ANALYSIS (2% penalty assumed)':^85}")
    print(f"{'─' * 85}")

    header = (
        f"{'At Month':>10} │ {'Balance':>14} │ {'Int.Paid':>14} │ "
        f"{'Penalty':>12} │ {'Total Cost':>14} │ {'Savings':>14}"
    )
    print(header)
    print(f"{'─' * 10}─┼─{'─' * 14}─┼─{'─' * 14}─┼─{'─' * 12}─┼─{'─' * 14}─┼─{'─' * 14}")

    for row in prepay_results:
        line = (
            f"{row['month']:>10} │ {row['remaining_balance']:>14,.2f} │ "
            f"{row['interest_paid']:>14,.2f} │ {row['penalty']:>12,.2f} │ "
            f"{row['total_cost']:>14,.2f} │ {row['savings']:>14,.2f}"
        )
        print(line)

    print(f"{'─' * 85}")
    print(f"\n  [*] Tip: Prepay as early as you can to maximize savings!")


def generate_default_prepay_months(tenure_months):
   
    milestones = []
    # Pick 1 year, 2 year, 3 year marks etc.
    for year in range(1, int(tenure_months / 12) + 1):
        m = year * 12
        if m < tenure_months:
            milestones.append(m)
    milestones.extend([6, 18, 36, 60, 120])
    # Clean up the list: remove duplicates, remove invalid months, sort them
    milestones = sorted(set(m for m in milestones if 1 <= m < tenure_months))
    return milestones[:8] # Return max 8 items

def main():
    """
    This is the boss function. It decides HOW the program gets its data.
    Does the user type it interactively? Or did they pass command line arguments?
    """
    
    # ARGPARSE SETUP
    # This tells Python: "Hey, if the user runs this from terminal with flags like --loan, accept them."
    parser = argparse.ArgumentParser(
        description='Loan Amortization Revealer - Uncover the true cost of your loan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python loan_amortization.py                    # Interactive mode (asks you questions)
  python loan_amortization.py 500000 8.5 240     # Positional arguments
  python loan_amortization.py --loan 3000000 --rate 9.0 --tenure 180
        """
    )

    # Positional arguments (no flags, just typed in order)
    parser.add_argument('loan_amount', nargs='?', type=float, help='Loan amount')
    parser.add_argument('interest_rate', nargs='?', type=float, help='Interest rate')
    parser.add_argument('tenure_months', nargs='?', type=int, help='Tenure in months')

    # Named arguments (with flags like -l or --loan)
    parser.add_argument('-l', '--loan', type=float, help='Loan amount')
    parser.add_argument('-r', '--rate', type=float, help='Interest rate')
    parser.add_argument('-t', '--tenure', type=int, help='Tenure in months')
    parser.add_argument('-p', '--prepay', nargs='+', type=int, help='Months to check prepay')
    parser.add_argument('--no-table', action='store_true', help='Skip the giant table')
    parser.add_argument('-i', '--interactive', action='store_true', help='Force interactive mode')

 
    args = parser.parse_args()
    
    all_positional = [args.loan_amount, args.interest_rate, args.tenure_months]
    all_named = [args.loan, args.rate, args.tenure]
    has_cli_input = any(v is not None for v in all_positional) or any(v is not None for v in all_named)

    # If they typed NOTHING, or if they typed "-i", run the interactive mode
    if not has_cli_input or args.interactive:
        user_input = get_interactive_input() # Call the function from Part 1
        loan_amount = user_input['loan_amount']
        interest_rate = user_input['interest_rate']
        tenure_months = user_input['tenure_months']
        prepay_months = user_input['prepay_months']
        no_table = user_input['no_table']
        penalty_rate = 2.0
    else:
        # They used command line! Grab the values.
        # "Named args override positional" - if they typed both, named wins
        loan_amount = args.loan if args.loan else args.loan_amount
        interest_rate = args.rate if args.rate else args.interest_rate
        tenure_months = args.tenure if args.tenure else args.tenure_months
        prepay_months = args.prepay
        no_table = args.no_table
        penalty_rate = 2.0

        # Basic error checking for command line
        if loan_amount is None or interest_rate is None or tenure_months is None:
            print("\n  ERROR: You must provide loan, rate, and tenure.\n")
            sys.exit(1) # Stop the program immediately with error code 1

   
    emi, table, crossover_month = build_amortization_table(loan_amount, interest_rate, tenure_months)

    
    if not prepay_months:
        prepay_months = generate_default_prepay_months(tenure_months)

   
    prepay_results = calculate_prepay_cost(table, prepay_months, penalty_rate / 100)

   
    print_header(loan_amount, interest_rate, tenure_months, emi)

    if not no_table:
        print_amortization_table(table, crossover_month)

    print_highlights(table, crossover_month, loan_amount, emi)

    if prepay_results:
        print_prepay_analysis(prepay_results)

    
    print(f"\n{'=' * 85}")
    print(f"{'FINAL SUMMARY':^85}")
    print(f"{'=' * 85}")
    print(f"""
  ┌─────┐
  │  Quick Reference                                                           │
  ├─────────────────────────────────────────────────────────────────────────────┤
  │  Monthly EMI:            {format_currency(emi):>45}  │
  │  Total Interest:         {format_currency(table[-1]['cumulative_interest']):>45}  │
  │  Crossover Month:        {str(crossover_month) if crossover_month else 'N/A':>45}  │
  └─────────────────────────────────────────────────────────────────────────────┘
    """)
    print(f"{'=' * 85}\n")



if __name__ == "__main__":
    main()
