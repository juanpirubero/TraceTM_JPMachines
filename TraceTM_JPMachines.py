#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict

def load_machine(file_path):
    # Store all state transitions in a dictionary
    transitions = defaultdict(list)

    # Open the CSV file
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

# Function for tracing all the configurations using BFS
def trace_ntm(name, start_state, accept_state, reject_state, transitions, input_string, max_depth=100):
    tree = [[("", start_state, input_string)]] 
    total_transitions = 0
    # Iterates up to the max depth to explore the configurations level by level
    for depth in range(max_depth):
        current_level = tree[-1] 
        next_level = []  

        for left, state, tape in current_level:
            total_transitions += 1

            # Check accept or reject states
            if state == accept_state:
                tree.append(next_level)
                return "Accepted", depth + 1, total_transitions, tree
            if state == reject_state:
                next_level.append((left, state, tape))
                continue

            
            current_symbol = tape[0] if tape else "_"

            # Process transitions for the configuration
            if (state, current_symbol) in transitions:
                for next_state, write, move in transitions[(state, current_symbol)]:
                    # Update head position and tape based on the transition and by writing the new symbol
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
        # Stop if no more configurations
        if not next_level:  
            tree.append(next_level)
            return "Rejected", depth + 1, total_transitions, tree

        tree.append(next_level)

    return "Terminated", max_depth, total_transitions, tree

# Run the NTM and output results
def run(name, start_state, accept_state, reject_state, transitions, input_string, max_depth=100):

    result, depth, total_transitions, tree = trace_ntm(name, start_state, accept_state, reject_state, transitions, input_string, max_depth)
    
    output = []
    # Get the necessary output
    output.append(f"Machine name: {name}")
    output.append(f"Initial string: {input_string}")
    output.append(f"Depth of tree: {depth}")
    output.append(f"Total transitions: {total_transitions}")
    
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
