from main import JevLib


def run_feel(jl: JevLib) -> None:
    email_state = """
    Please resolve my email immediately!
    """

    if jl.feels(email_state, "needs an urgent reply") > 0.7:
        print("The email needs an urgent reply.")
    else:
        print("The email does not need an urgent reply.")


def run_match(jl: JevLib) -> None:
    state = "My shoes arrived in the wrong size. Can I swap them for a different size?"
    instructions = "Which team should handle this?"

    teams = {
        "returns": "Exchanges, wrong or damaged items",
        "shipping": "Delivery status, delays, lost packages",
        "billing": "Charges, invoices, payment problems",
    }

    team = jl.match(state, instructions, teams)

    detailled_call = jl.match(
        state,
        instructions,
        teams,
        model="jev-latest",
        retry=None,
        timeout=5.0,
        extra_headers={"x-trace-id": "match-demo"},
        extra_body={"metadata": {"source": "demo"}},
    )
    print(f"Route to: {team}")


def main() -> None:
    try:
        with JevLib() as jl:
            print("JevLib initialized successfully.")
            run_feel(jl)

            print("----------------------------")

            run_match(jl)

            print("----------------------------")
    except RuntimeError as error:
        print(f"Error initializing JevLib: {error}")


if __name__ == "__main__":
    main()
