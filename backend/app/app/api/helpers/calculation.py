async def calculate_rate(
    total_seconds: int,
    total_kwh: float,
    energy_rate: float,
    time_rate: float,
    transaction_rate: float,
):
    """Calculate rate based on the price metrics and consumption metrics,
    Format price rates by precision of x decimal places based on the requirement.

    Args:
        total_seconds (int): Total time consumed in seconds
        total_kwh (float): Total kWh of energy used
        energy_rate (float): Price rate for energy consumption
        time_rate (float): Price rate for time duration
        transaction_rate (float): Price rate per charging process

    Returns:
        [str]: Calculated and formatted rates
    """
    energy = total_kwh * energy_rate
    time = (total_seconds / 3600) * time_rate
    overall = energy + time + transaction_rate

    # Precision of 3 decimal places for the prices
    # Additional check for if the float value is a whole number
    energy, time, transaction = map(
        lambda rate: "{0:0.3f}".format(rate) if not rate.is_integer() else int(rate),
        [energy, time, transaction_rate],
    )
    # Precision of 2 decimal places for the overall value
    overall = "{0:0.2f}".format(overall) if not overall.is_integer() else int(overall)
    return overall, energy, time, transaction
