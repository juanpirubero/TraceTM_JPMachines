#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict

# Read the csv file and load the NTM configuration
def load_machine(file_path):
    transitions = defaultdict(list)
    # Read the file
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
        
        # Parse the transitions
        for line in lines[7:]:
            if len(line) >= 5:
                state, read, next_state, write, move = line
                transitions[(state, read)].append((next_state, write, move))
    
    return name, states, input_symbols, tape_symbols, start_state, accept_state, reject_state, transitions

# Simulate the NTM using Breadth-First search 
def trace_ntm(name, start_state, accept_state, reject_state, transitions, input_string, max_depth=100):
    tree = [[("", start_state, input_string)]] 
    total_transitions = 0 
    
    # Iterate through the configurations by depth
    for depth in range(max_depth):
        current_level = tree[-1] 
        next_level = []  

        #Iterate through each configuration at the current depth
        for left, state, tape in current_level:
            total_transitions += 1

            # Check for accept or reject states
            if state == accept_state:
                tree.append(next_level)
                return "Accepted", depth + 1, total_transitions, tree
            if state == reject_state:
                next_level.append((left, state, tape))
                continue
            current_symbol = tape[0] if tape else "_"

            # Process transitions for the current configuration and update the tape with a new symbol
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

        # Stop if no configurations exist
        if not next_level:
            tree.append(next_level)
            return "Rejected", depth + 1, total_transitions, tree

        tree.append(next_level)

    return "Terminated", max_depth, total_transitions, tree

# Run the NTM and get the results
def run(name, start_state, accept_state, reject_state, transitions, input_string, max_depth=100):
    result, depth, total_transitions, tree = trace_ntm(name, start_state, accept_state, reject_state, transitions, input_string, max_depth)
    
    output = []
    output.append(f"Machine name: {name}")
    output.append(f"Initial string: {input_string}")
    output.append(f"Depth of tree: {depth}")
    output.append(f"Total transitions: {total_transitions}")
    
    # Calculate the average nondeterminism
    total_configurations = sum(len(level) for level in tree)
    average_nondeterminism = total_configurations / depth if depth > 0 else 0
    output.append(f"Average nondeterminism: {average_nondeterminism:.2f}")

    # Get the configuration tree
    tree_output = []
    for level in tree:
        formatted_level = [f"[\"{left}\",\"{state}\",\"{tape}\"]" for left, state, tape in level]
        tree_output.append(f"[{','.join(formatted_level)}]")
    output.append("\n".join(tree_output))

    # Return whether the string was accepted, rejected, or stopped
    if result == "Accepted":
        output.append(f"String accepted in {depth} transitions")
    elif result == "Rejected":
        output.append(f"String rejected in {depth} transitions")
    else:
        output.append(f"Execution stopped after {max_depth} transitions")

    return "\n".join(output)

def main():
    ntm_file = sys.argv[1]
    input_arg = sys.argv[2]

    # Check whether to read the input string directly or from a file
    if input_arg.endswith('.txt'):
        with open(input_arg, 'r') as file:
            input_string = file.read().strip()
    else:
        input_string = input_arg
    name, states, input_symbols, tape_symbols, start_state, accept_state, reject_state, transitions = load_machine(ntm_file)
    result = run(name, start_state, accept_state, reject_state, transitions, input_string)
    # Print the output
    print(result)

if __name__ == "__main__":
    main()
