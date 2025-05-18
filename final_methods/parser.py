import sys
sys.path.append('./..')
sys.path.append('.')

def parse_solution_file(filepath):
    """
    Parses a solution file and returns a dictionary mapping each community to its assigned healthcenter.
    Args:
        filepath (str): Path to the solution file.
    Returns:
        dict: {community: healthcenter}
    """
    assignments = {}  # {community: healthcenter}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith("Healthcenter deployed at"):
                # Example line:
                # Healthcenter deployed at 154: Communities Assigned = {103, 118, 137, ...}
                try:
                    parts = line.split(":")
                    center = int(parts[0].split()[-1])
                    comms_str = parts[1].split('=')[1].strip()
                    # Remove braces and split by comma
                    comms_str = comms_str.strip('{}')
                    if comms_str:
                        comms = [int(x.strip()) for x in comms_str.split(',')]
                        for c in comms:
                            assignments[c] = center
                except Exception:
                    continue  # Skip malformed lines
    return assignments

if __name__ == "__main__":
    # Test the parser on Sol_Instance_1.txt
    test_path = "../Final_solutions/Instance_1/Sol_Instance_1.txt"
    assignments = parse_solution_file(test_path)
    print("Assignments:")
    for community, healthcenter in sorted(assignments.items()):
        print(f"Community {community} assigned to Healthcenter {healthcenter}")


