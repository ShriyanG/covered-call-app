"""
Update Greeks for options data.

This script calculates and updates option Greeks (delta, gamma, theta, vega, rho)
for options in the database.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta


def fetch_all_options_snapshot(underlying_asset, contract_type="call", expiration_date=None):
    """
    Fetch ALL options snapshot from Massive API for a given underlying asset,
    handling pagination through all pages.
    
    Parameters:
    - underlying_asset (str): The underlying stock ticker (e.g., "QQQ")
    - contract_type (str): Option type ("call" or "put")
    - expiration_date (str): Optional expiration date filter (YYYY-MM-DD format)
    
    Returns:
    - list: All option results across all pages, or empty list if error
    """
    api_key = "3E0DAOW4AOEZXBOgw24x2yDBnITajqJc"
    base_url = f"https://api.massive.com/v3/snapshot/options/{underlying_asset}"
    
    all_results = []
    url = base_url
    page = 1
    
    while url:
        params = {
            "contract_type": contract_type,
            "order": "asc",
            "limit": 250,
            "sort": "ticker",
            "apiKey": api_key
        }
        
        # Add expiration_date parameter if provided
        if expiration_date:
            params["expiration_date"] = expiration_date
        
        try:
            print(f"Fetching page {page}...")
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "results" in data:
                all_results.extend(data["results"])
                print(f"Page {page}: {len(data['results'])} results (total so far: {len(all_results)})")
            
            # Check if there's a next page
            url = data.get("next_url")
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching options snapshot: {e}")
            break
    
    print(f"\n✅ Total options fetched: {len(all_results)}")
    return all_results


def filter_options_by_greeks(underlying_asset, start, end, delta_min, delta_max, theta_gamma_ratio_min):
    """
    Filter options by expiration date range and greeks criteria.
    
    Parameters:
    - underlying_asset (str): The underlying stock ticker (e.g., "QQQ")
    - start (int): Number of days from today for start of expiration date range
    - end (int): Number of days from today for end of expiration date range
    - delta_min (float): Minimum absolute delta value
    - delta_max (float): Maximum absolute delta value
    - theta_gamma_ratio_min (float): Minimum theta/gamma ratio (options below this are excluded)
    
    Returns:
    - pd.DataFrame: Filtered options with columns: Date, Ticker, expiration_date, strike_price, delta, theta, gamma
    """
    current_date = datetime.now().date()
    start_exp_date = (current_date + timedelta(days=start)).strftime('%Y-%m-%d')
    end_exp_date = (current_date + timedelta(days=end)).strftime('%Y-%m-%d')
    
    print(f"\nFiltering options for {underlying_asset}")
    print(f"Expiration date range: {start_exp_date} to {end_exp_date}")
    print(f"Delta range: {delta_min} to {delta_max}")
    print(f"Min theta/gamma ratio: {theta_gamma_ratio_min}")
    
    # Fetch all options for the ticker
    all_options = fetch_all_options_snapshot(underlying_asset, contract_type="call")
    
    filtered_rows = []
    
    for option in all_options:
        try:
            details = option.get("details", {})
            greeks = option.get("greeks", {})
            
            expiration = details.get("expiration_date")
            strike_price = details.get("strike_price")
            delta = greeks.get("delta", 0)
            theta = greeks.get("theta", 0)
            gamma = greeks.get("gamma", 0)
            
            # Check expiration date range
            if not (start_exp_date <= expiration <= end_exp_date):
                continue
            
            # Check delta range (absolute values)
            abs_delta = abs(delta)
            if not (delta_min <= abs_delta <= delta_max):
                continue
            
            # Check theta/gamma ratio
            if gamma == 0:
                continue  # Skip if gamma is 0 to avoid division by zero
            
            theta_gamma_ratio = abs(theta) / abs(gamma)
            if theta_gamma_ratio < theta_gamma_ratio_min:
                continue
            
            # Add to filtered results
            filtered_rows.append({
                "Date": current_date.strftime('%Y-%m-%d'),
                "Ticker": underlying_asset,
                "expiration_date": expiration,
                "strike_price": strike_price,
                "delta": delta,
                "theta": theta,
                "gamma": gamma,
                "theta_gamma_ratio": theta_gamma_ratio
            })
        
        except Exception as e:
            print(f"Error processing option: {e}")
            continue
    
    df = pd.DataFrame(filtered_rows)
    print(f"\n✅ Filtered {len(df)} options matching criteria")
    return df


def update_greeks():
    """
    Calculate and update Greeks for all options in the database.
    """
    pass


if __name__ == "__main__":
    # Test the filter function
    # Look for options expiring between 1-30 days from today
    # with delta between 0.3-0.7 (ATM options)
    # and theta/gamma ratio >= 20
    
    filtered_df = filter_options_by_greeks(
        underlying_asset="QQQ",
        start=30,
        end=45,
        delta_min=0.3,
        delta_max=0.7,
        theta_gamma_ratio_min=20.0
    )
    
    if not filtered_df.empty:
        print("\nFiltered Options Results:")
        print(filtered_df.to_string())
    else:
        print("No options matched the filter criteria.")
