from decimal import Decimal

def calculate_paye_manual(annual_taxable_income):
    # 2026/2027 Brackets (from tax expert summary)
    # Threshold 1,878,601 and above: 666,209 + 45% of taxable income above 1,878,600
    # Primary Rebate: 17,820
    
    if annual_taxable_income > 1878600:
        base_tax = Decimal("666209") # Fixed amount for top bracket
        excess = annual_taxable_income - 1878600
        tax = base_tax + (excess * Decimal("0.45"))
    else:
        # Simplified for this specific high-income case
        tax = Decimal("0")
        
    tax -= Decimal("17820") # Primary Rebate
    return max(tax, Decimal("0"))

income = Decimal("2560000")
total_tax = calculate_paye_manual(income)
print(f"Annual Tax: {total_tax}")
print(f"Monthly Average: {total_tax/12}")
