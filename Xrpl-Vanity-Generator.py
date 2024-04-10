from xrpl.wallet import Wallet
import signal
import sys

def generate_xrp_addresses(num_addresses):
    """
    Generates XRP addresses using the xrpl library.
    """
    addresses = []
    for i in range(num_addresses):
        wallet = Wallet.create()
        address = wallet.classic_address
        seed = wallet.seed
        addresses.append((address, seed))
    return addresses

def find_matching_addresses(vanity_addresses, num_addresses, desired_count):
    """
    Finds XRP addresses matching any of the given vanity addresses and returns the matching addresses.
    """
    matching_addresses = {vanity: [] for vanity in vanity_addresses}
    completed_prefixes = set()

    while len(completed_prefixes) < len(vanity_addresses):
        addresses = generate_xrp_addresses(num_addresses)
        for address, seed in addresses:
            for vanity in vanity_addresses:
                if address.startswith(vanity):
                    matching_addresses[vanity].append((address, seed))
                    if len(matching_addresses[vanity]) >= desired_count:
                        completed_prefixes.add(vanity)
    
    return matching_addresses

def write_to_file(matching_addresses, output_file):
    """
    Writes the matching addresses to the specified output file.
    """
    with open(output_file, 'w') as f:
        for vanity, addresses in matching_addresses.items():
            f.write(f"Prefix: {vanity}\n")
            for address, seed in addresses:
                f.write(f"Address: {address}\nSeed: {seed}\n\n")
            f.write("\n")

def validate_prefixes(prefixes):
    """
    Validates the user input for prefixes.
    """
    prefixes = [prefix.strip() for prefix in prefixes.split(',')]
    for prefix in prefixes:
        if not prefix:
            raise ValueError("Empty prefix is not allowed.")
        if not prefix[0].isalpha():
            raise ValueError(f"Invalid prefix '{prefix}'. Prefixes must start with a letter.")
    return prefixes

def main():
    while True:
        prefixes = input("Which prefix(es) (separate by comma) do you want to find? (r is already at the front): ")
        try:
            prefixes = validate_prefixes(prefixes)
            break
        except ValueError as e:
            print(f"Error: {str(e)} Please try again.")

    vanity_addresses = ['r' + prefix for prefix in prefixes]

    if any(prefix[0].lower() == 'r' for prefix in prefixes):
        confirm = input(f"Are you sure you want to proceed with the prefix(es) {prefixes}? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return

    while True:
        try:
            desired_count = int(input("How many addresses should be found for each prefix? "))
            if desired_count <= 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

    num_addresses = 250000
    output_file = "matching_addresses.txt"

    def signal_handler(sig, frame):
        print("\nProgram interrupted. Writing found addresses to file...")
        write_to_file(matching_addresses, output_file)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    matching_addresses = find_matching_addresses(vanity_addresses, num_addresses, desired_count)
    write_to_file(matching_addresses, output_file)

    total_count = sum(len(addresses) for addresses in matching_addresses.values())
    print(f"{total_count} matching addresses found and saved to '{output_file}'.")

if __name__ == '__main__':
    main()