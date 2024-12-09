#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict

def load_machine(file_path):
    """Loads the NTM configuration from a CSV file."""
    transitions = defaultdict(list)

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        lines = list(reader)
        
        name = lines[0][0]  # Line 1: Machine name
        states = lines[1]  # Line 2: List of states
        input_symbols = lines[2]  # Line 3: Input symbols
        tape_symbols = lines[3]  # Line 4: Tape symbols
        start_state = lines[4][0]  # Line 5: Start state
        accept_state = lines[5][0]  # Line 6: Accept state
        reject_state = lines[6][0]  # Line 7: Reject state
        
        # Parse transitions
        for line in lines[7:]:
            if len(line) >= 5:
                state, read, next_state, write, move = line
                transitions[(state, read)].append((next_state, write, move))
    
    return name, states, input_symbols, tape_symbols, start_state, accept_state, reject_state, transitions

def trace_ntm(name, start_state, accept_state, reject_state, transitions, input_string, max_depth=100):
    """Traces all possible paths of the NTM using BFS and stores configurations in a list of lists."""
    tree = [[("", start_state, input_string)]]  # Tree of configurations
    total_transitions = 0  # Total state transitions made

    for depth in range(max_depth):
        current_level = tree[-1]  # Get the current level of configurations
        next_level = []  # Initialize the next level of configurations

        for left, state, tape in current_level:
            total_transitions += 1

            # Check for accept or reject states
            if state == accept_state:
                tree.append(next_level)
                return "Accepted", depth + 1, total_transitions, tree
            if state == reject_state:
                next_level.append((left, state, tape))
                continue

            # Determine the current symbol under the head
            current_symbol = tape[0] if tape else "_"

            # Process transitions for the current configuration
            if (state, current_symbol) in transitions:
                for next_state, write, move in transitions[(state, current_symbol)]:
                    new_tape = write + tape[1:] if tape else write
                    if move == "R":
                        next_left = left + (current_symbol if tape else "_")
                        next_tape = new_tape[1:] if len(new_tape) > 1 else ""
                        next_config = (next_left, next_state, next_tape)
                    elif move == "L":
                        next_left = left[:-1] if left else "_"
                        next_tape = (left[-1] if left else "_") + new_tape
                        next_config = (next_left, next_state, next_tape)
                    next_level.append(next_config)

        # Stop if no more configurations exist
        if not next_level:
            tree.append(next_level)
            return "Rejected", depth + 1, total_transitions, tree

        tree.append(next_level)  # Add the next level to the tree

    return "Terminated", max_depth, total_transitions, tree

def run(name, start_state, accept_state, reject_state, transitions, input_string, max_depth=100):
    """Runs the NTM and outputs results."""
    result, depth, total_transitions, tree = trace_ntm(name, start_state, accept_state, reject_state, transitions, input_string, max_depth)
    
    output = []
    output.append(f"Machine name: {name}")
    output.append(f"Initial string: {input_string}")
    output.append(f"Depth of tree: {depth}")
    output.append(f"Total transitions: {total_transitions}")
    
    # Calculate average nondeterminism
    total_configurations = sum(len(level) for level in tree)
    average_nondeterminism = total_configurations / depth if depth > 0 else 0
    output.append(f"Average nondeterminism: {average_nondeterminism:.2f}")

    # Format the configuration tree
    tree_output = []
    for level in tree:
        formatted_level = [f"[\"{left}\",\"{state}\",\"{tape}\"]" for left, state, tape in level]
        tree_output.append(f"[{','.join(formatted_level)}]")
    output.append("\n".join(tree_output))

    if result == "Accepted":
        output.append(f"String accepted in {depth} transitions")
    elif result == "Rejected":
        output.append(f"String rejected in {depth} transitions")
    else:
        output.append(f"Execution stopped after {max_depth} transitions")

    return "\n".join(output)

def main():
    """Main function to simulate the NTM."""
    if len(sys.argv) < 3:
        print("Usage: python ntm_machine.py <ntm_file.csv> <input_string_or_file>")
        sys.exit(1)

    ntm_file = sys.argv[1]
    input_arg = sys.argv[2]

    # Read input string directly or from a file
    if input_arg.endswith('.txt'):
        with open(input_arg, 'r') as file:
            input_string = file.read().strip()
    else:
        input_string = input_arg

    # Load the machine
    name, states, input_symbols, tape_symbols, start_state, accept_state, reject_state, transitions = load_machine(ntm_file)

    # Run the NTM
    result = run(name, start_state, accept_state, reject_state, transitions, input_string)
    print(result)

if __name__ == "__main__":
    main()
