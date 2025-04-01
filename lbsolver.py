#! /usr/local/bin/python3

DICT_NAME = "lbwords.txt"

# Examples of previous puzzles
EXAMPLE_PUZZLES = [
    ["WNT", "LVE", "KYO", "ARH"],
    ["INH", "GLC", "MKE", "ATO"],
    ["PRO", "CTI", "SAH", "DGN"],
    ["TLQ", "SRU", "BFI", "EMO"],
    ["LEI", "XYS", "CUV", "KOT"]
]

# Default puzzle (will only be used if --use-default is specified)
DEFAULT_PUZZLE = ["LEI", "XYS", "CUV", "KOT"]

def load_dict(dict_name):
    with open(dict_name, 'r') as f:
        words = f.readlines()
    words = [w.strip() for w in words]
    return words


def eliminate_consecutives(word_list, puzzle):
    """Eliminate words that contain consecutive letters from the same side of the square."""
    new_list = []
    for word in word_list:
        # Check each pair of consecutive letters in the word
        is_valid = True
        for i in range(len(word)-1):
            letter1, letter2 = word[i], word[i+1]
            # Check if these letters appear consecutively in any side of the puzzle
            for side in puzzle:
                if letter1 in side and letter2 in side:
                    is_valid = False
                    break
            if not is_valid:
                break
        if is_valid:
            new_list.append(word)
    return new_list


def eliminate_unavailable_letters(word_list, letters):
    print(f"Eliminating words that contain a letter that's not in puzzle ({letters})")
    new_list = [word for word in word_list if all(c in letters for c in word)]
    return new_list


def remove_duplicate_letters(word):
    seen = set()
    result = []
    for char in word:
        if char not in seen:
            seen.add(char)
            result.append(char)
    return ''.join(result)


def get_unique_letters(word):
    return set(word)


def score_words(words, puzzle):
    d = {}
    for w in words:
        u = remove_duplicate_letters(w)
        d[w] = len(u)

    s = sorted(d, key=lambda x: d[x], reverse=True)
    for w in s[:100]:
        print(f"{w} -- {d[w]}")
    
    return s


def find_all_letters_used(words, all_puzzle_letters):
    """Check if a sequence of words uses all letters in the puzzle."""
    used_letters = set()
    for word in words:
        used_letters.update(set(word))
    return used_letters == set(all_puzzle_letters)


def find_chains(valid_words, all_puzzle_letters, max_chain_length=4, prefer_common_words=True):
    """Find chains of words where the last letter of one word is the first letter of the next."""
    # Create a dictionary mapping first letters to words
    first_letter_map = {}
    for word in valid_words:
        first_letter = word[0]
        if first_letter not in first_letter_map:
            first_letter_map[first_letter] = []
        first_letter_map[first_letter].append(word)
    
    # Track the best solutions
    best_solutions = []
    best_solution_length = max_chain_length + 1  # Initialize to one more than max
    best_redundancy_score = float('inf')  # Lower is better
    
    # Track progress
    import time
    start_time = time.time()
    chains_explored = 0
    
    # Precompute all_puzzle_letters as a set
    all_letters_set = set(all_puzzle_letters)
    
    # Calculate word complexity score (lower is better - favors common/simple words)
    # This is a heuristic that generally favors shorter, more common words
    def word_complexity(word):
        # Length component - longer words are more complex
        length_score = len(word) * 0.5
        
        # Letter frequency component - rare letters make words more complex
        rare_letters = "JQXZVBKWYPGFM"
        common_letters = "ETAOINSRHLDCU"
        letter_score = 0
        for letter in word:
            if letter in rare_letters:
                letter_score += 2
            elif letter not in common_letters:
                letter_score += 1
        
        # Pattern complexity - words with unusual patterns are more complex
        pattern_score = 0
        vowels = "AEIOU"
        consonant_count = 0
        vowel_count = 0
        for i, letter in enumerate(word):
            if letter in vowels:
                vowel_count += 1
                consonant_count = 0
            else:
                consonant_count += 1
                vowel_count = 0
                
            # Penalize consonant clusters of 3+ or vowel clusters of 3+
            if consonant_count >= 3 or vowel_count >= 3:
                pattern_score += 1
        
        # Total score is weighted sum
        return length_score + letter_score + pattern_score
    
    # Calculate redundancy score (lower is better)
    def calculate_redundancy(word_chain):
        # Count each letter's occurrences across all words
        letter_counts = {}
        for word in word_chain:
            for letter in word:
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
        
        # Calculate redundancy: sum of occurrences minus 1 for each letter
        # (since each letter needs to appear at least once)
        redundancy = sum(max(0, count - 1) for count in letter_counts.values())
        return redundancy
    
    # Calculate solution complexity (lower is better - favors simpler solutions)
    def solution_complexity(word_chain):
        return sum(word_complexity(word) for word in word_chain)
    
    # Helper function for DFS
    def build_chain(current_chain, used_letters):
        nonlocal chains_explored, best_solution_length, best_redundancy_score
        chains_explored += 1
        
        # Show progress every 10000 chains
        if chains_explored % 10000 == 0:
            elapsed = time.time() - start_time
            print(f"Explored {chains_explored} chains in {elapsed:.2f} seconds...")
        
        # If we've found a solution that uses all letters
        if used_letters == all_letters_set:
            chain_length = len(current_chain)
            redundancy_score = calculate_redundancy(current_chain)
            complexity_score = solution_complexity(current_chain) if prefer_common_words else 0
            
            # If this solution uses fewer words, it's automatically better
            if chain_length < best_solution_length:
                best_solutions.clear()
                best_solutions.append((current_chain[:], redundancy_score, complexity_score))
                best_solution_length = chain_length
                best_redundancy_score = redundancy_score
                print(f"Found solution with {chain_length} words: {' → '.join(current_chain)} (redundancy: {redundancy_score})")
                return
            
            # If this solution uses the same number of words
            elif chain_length == best_solution_length:
                is_better = False
                is_equivalent = False
                
                # First prioritize by redundancy
                if redundancy_score < best_redundancy_score:
                    is_better = True
                elif redundancy_score == best_redundancy_score:
                    # Then by complexity (if enabled)
                    if prefer_common_words:
                        # Compare with existing solutions
                        existing_min_complexity = min([c for _, _, c in best_solutions]) if best_solutions else float('inf')
                        if complexity_score < existing_min_complexity:
                            is_better = True
                        elif complexity_score == existing_min_complexity:
                            is_equivalent = True
                    else:
                        is_equivalent = True
                
                if is_better:
                    # Better solution, clear previous
                    best_solutions.clear()
                    best_solutions.append((current_chain[:], redundancy_score, complexity_score))
                    best_redundancy_score = redundancy_score
                    print(f"Found better solution with {chain_length} words: {' → '.join(current_chain)} (redundancy: {redundancy_score})")
                elif is_equivalent:
                    # Equivalent solution, add to list
                    best_solutions.append((current_chain[:], redundancy_score, complexity_score))
                    print(f"Found equivalent solution with {chain_length} words: {' → '.join(current_chain)} (redundancy: {redundancy_score})")
                return
        
        # If we've exceeded our max chain length, stop
        if len(current_chain) >= max_chain_length:
            return
            
        # Optimization: If we can't possibly beat the best solution, stop
        if best_solution_length < float('inf') and len(current_chain) >= best_solution_length - 1 and used_letters != all_letters_set:
            return
        
        # Get the last letter of the current chain's last word
        if not current_chain:
            # Start with any word if the chain is empty
            words_with_scores = []
            for word in valid_words:
                new_letters = set(word)
                # Score = (new letters * 5) - complexity
                score = (len(new_letters) * 5) - (word_complexity(word) if prefer_common_words else 0)
                words_with_scores.append((word, score))
            
            # Sort by score, descending
            words_with_scores.sort(key=lambda x: -x[1])
            
            for word, _ in words_with_scores:
                new_used_letters = used_letters.union(set(word))
                build_chain([word], new_used_letters)
        else:
            last_letter = current_chain[-1][-1]
            
            # Find all words that start with the last letter
            if last_letter in first_letter_map:
                # Score words by new letters, redundancy, and complexity
                next_words = first_letter_map[last_letter]
                next_words_with_scores = []
                
                for word in next_words:
                    if word not in current_chain:  # Avoid using the same word twice
                        # Calculate how many new letters this word would add
                        new_letters = set(word) - used_letters
                        
                        # Calculate how many redundant letters this word would add
                        redundant_letters = len(word) - len(new_letters)
                        
                        # Word complexity if enabled
                        complexity = word_complexity(word) if prefer_common_words else 0
                        
                        # Score = (new letters * 8) - (redundant letters * 2) - complexity
                        # This prioritizes words that:
                        # 1. Add more new letters
                        # 2. Minimize redundant letters
                        # 3. Are simpler/more common
                        score = (len(new_letters) * 8) - (redundant_letters * 2) - complexity
                        
                        # Extra boost if this word would complete the puzzle
                        missing_letters = all_letters_set - used_letters
                        if new_letters.issuperset(missing_letters):
                            score += 50
                            
                        next_words_with_scores.append((word, score))
                
                # Sort by score, descending
                next_words_with_scores.sort(key=lambda x: -x[1])
                
                for word, _ in next_words_with_scores:
                    new_used_letters = used_letters.union(set(word))
                    build_chain(current_chain + [word], new_used_letters)
    
    # Start the chain-building process
    build_chain([], set())
    
    print(f"Finished exploring {chains_explored} chains in {time.time() - start_time:.2f} seconds")
    
    # Extract just the word chains from the solutions (strip the scores)
    return [chain for chain, _, _ in best_solutions]


def solve_lb(words, puzzle, max_chain_length=4):
    puzzle_letters = puzzle[0] + puzzle[1] + puzzle[2] + puzzle[3]
    words = eliminate_unavailable_letters(words, puzzle_letters)
    print(f"After eliminating words that contain letters not in puzzle, {len(words)} words left.")

    for side in puzzle:
        words = eliminate_consecutives(words, side)
        print(f"After eliminating for side {side}, there are {len(words)} words left in the dictionary")

    if len(words) == 0:
        print("\nNo valid words found for this puzzle. Please check your input.")
        return
        
    # Ask user if they want to see top words by letter count
    show_top_words = input("\nShow top words by unique letter count? (y/n): ").strip().lower()
    if show_top_words.startswith('y'):
        # First approach: Find the words with the most unique letters
        print("\nTop words by unique letter count:")
        top_words = score_words(words, puzzle_letters)
    else:
        # Still need to get the top words for the chain finding
        d = {}
        for w in words:
            d[w] = len(set(w))
        top_words = sorted(d, key=lambda x: d[x], reverse=True)
    
    # Second approach: Find chains of words that use all letters
    print("\nFinding optimal word chains...")
    
    # Filter out very short words for better solutions (but keep words of length 4+)
    min_word_length = 3
    filtered_words = [w for w in words if len(w) >= min_word_length]
    
    # If we have too few words, try with shorter words
    if len(filtered_words) < 100 and min_word_length > 2:
        print(f"Only {len(filtered_words)} words of length {min_word_length}+ found. Including shorter words...")
        min_word_length = 2
        filtered_words = [w for w in words if len(w) >= min_word_length]
    
    print(f"Using {len(filtered_words)} words of length {min_word_length} or more for chain finding")
    
    # Ask about word simplicity preference
    prefer_simple = input("\nPrefer simpler, more common words in solutions? (y/n): ").strip().lower()
    prefer_common_words = prefer_simple.startswith('y')
    
    if prefer_common_words:
        print("Will prioritize simpler, more common words in solutions.")
    else:
        print("Will focus on minimizing word count and letter redundancy only.")
    
    # Check if user wants to customize max chain length
    custom_length = input(f"\nLooking for solutions with up to {max_chain_length} words. Change this? (Enter number or press Enter to keep): ").strip()
    if custom_length and custom_length.isdigit():
        max_chain_length = int(custom_length)
        print(f"Set maximum chain length to {max_chain_length}")
    
    print(f"Searching for solutions with up to {max_chain_length} words...")
    
    # First try with a smaller subset of the best words for performance
    subset_size = min(500, len(filtered_words))
    print(f"First trying with a subset of {subset_size} words...")
    
    # Don't just sort by unique letters - use a mix of uniqueness and simplicity
    # if we're preferring common words
    if prefer_common_words:
        # For common words, we want a mix of word uniqueness and simplicity
        from functools import cmp_to_key
        
        def word_score(word):
            # Calculate uniqueness score (higher is better)
            uniqueness = len(set(word)) * 3
            
            # Calculate simplicity score (higher is better)
            simplicity = 0
            if len(word) <= 6:  # Favor words of reasonable length
                simplicity += 2
            if len(word) <= 8:  # But still consider medium-length words
                simplicity += 1
                
            # Letter frequency component - common letters make words simpler
            common_letters = "ETAOINSRHLDCU"
            for letter in word:
                if letter in common_letters:
                    simplicity += 0.1
                    
            # Return combined score
            return uniqueness + simplicity
        
        top_words_subset = sorted(filtered_words, key=word_score, reverse=True)[:subset_size]
    else:
        # For technical solutions, just sort by unique letters
        top_words_subset = sorted(filtered_words, key=lambda w: -len(set(w)))[:subset_size]
    
    # Now find chains
    solutions = find_chains(top_words_subset, puzzle_letters, max_chain_length, prefer_common_words)
    
    if not solutions and len(filtered_words) < 3000:
        # If no solutions found and dictionary size is manageable, try with all words
        try_all = input("No solutions found with top words. Try with all valid words? (y/n): ").strip().lower()
        if try_all.startswith('y'):
            print("Trying with all valid words...")
            solutions = find_chains(filtered_words, puzzle_letters, max_chain_length, prefer_common_words)
        
    if not solutions and max_chain_length < 5:
        # If still no solutions, try with all words and one more in the chain
        try_longer = input(f"No solutions found. Try with max chain length of {max_chain_length + 1}? (y/n): ").strip().lower()
        if try_longer.startswith('y'):
            print(f"Trying with max chain length of {max_chain_length + 1}...")
            solutions = find_chains(filtered_words, puzzle_letters, max_chain_length + 1, prefer_common_words)
    
    if solutions:
        print("\n==== FOUND SOLUTIONS ====")
        
        # Calculate redundancy score for each solution
        solutions_with_scores = []
        for solution in solutions:
            # Count each letter's occurrences across all words
            letter_counts = {}
            for word in solution:
                for letter in word:
                    letter_counts[letter] = letter_counts.get(letter, 0) + 1
            
            # Calculate redundancy: sum of occurrences minus 1 for each letter
            redundancy = sum(max(0, count - 1) for count in letter_counts.values())
            
            # Total letters used (includes redundancy)
            total_letters = sum(letter_counts.values())
            
            # Efficiency ratio: unique letters / total letters (higher is better)
            efficiency = len(letter_counts) / total_letters
            
            solutions_with_scores.append((solution, redundancy, efficiency))
        
        # Group solutions by number of words
        grouped_solutions = {}
        for solution, redundancy, efficiency in solutions_with_scores:
            length = len(solution)
            if length not in grouped_solutions:
                grouped_solutions[length] = []
            grouped_solutions[length].append((solution, redundancy, efficiency))
        
        # Display solutions by group
        for length in sorted(grouped_solutions.keys()):
            solutions_in_group = grouped_solutions[length]
            
            # Sort solutions within each group by redundancy (lower is better)
            solutions_in_group.sort(key=lambda x: x[1])
            
            print(f"\n=== {length}-WORD SOLUTIONS ===")
            
            # Limit display to 10 solutions per group
            max_display = min(10, len(solutions_in_group))
            for i, (solution, redundancy, efficiency) in enumerate(solutions_in_group[:max_display]):
                letters_used = set()
                for word in solution:
                    letters_used.update(set(word))
                
                # Check if all puzzle letters are used
                if letters_used == set(puzzle_letters):
                    status = "COMPLETE"
                else:
                    status = f"PARTIAL ({len(letters_used)}/{len(set(puzzle_letters))} letters)"
                
                # Show efficiency metrics
                print(f"Solution {i+1}: {' → '.join(solution)}")
                print(f"  Status: {status}")
                print(f"  Redundancy: {redundancy} extra letter occurrences")
                print(f"  Efficiency: {efficiency:.1%} (higher is better)")
                
                # Show missing letters if any
                if letters_used != set(puzzle_letters):
                    missing = set(puzzle_letters) - letters_used
                    print(f"  Missing letters: {''.join(sorted(missing))}")
                print()
            
            # Show if there are more solutions not displayed
            remaining = len(solutions_in_group) - max_display
            if remaining > 0:
                print(f"... and {remaining} more {length}-word solutions")
    else:
        print("\nNo solutions found. Consider:")
        print("1. Increasing the maximum chain length")
        print("2. Adding more words to your dictionary")
        print("3. Checking if your puzzle input is correct")
        
    # Ask if user wants to try another puzzle
    another = input("\nWould you like to solve another puzzle? (y/n): ").strip().lower()
    if another.startswith('y'):
        # Call main() with restart=True to avoid showing the intro again
        main(restart=True)


def get_puzzle():
    import re
    pattern = re.compile("^[A-Z]+$", re.I)

    while True:
        try:
            print("\nEnter the letters for each side of the square (one side per line):")
            sides = []
            
            for i in range(4):
                side_input = input(f"Side {i + 1}: ").strip()
                
                # Special commands
                if side_input.lower() == 'quit' or side_input.lower() == 'exit':
                    print("Exiting program.")
                    import sys
                    sys.exit(0)
                elif side_input.lower() == 'example' or side_input.lower() == 'examples':
                    show_examples()
                    # Restart input
                    sides = []
                    break
                
                # Process normal input
                sides.append(side_input.upper())
            
            # If we didn't get 4 sides, restart
            if len(sides) < 4:
                continue
                
            # Combine all sides into one string to check for duplicates
            combined_sides = ''.join(sides)

            # Validate that each side only contains letters
            if any(not pattern.match(side) for side in sides):
                raise ValueError("Each side must only contain letters (A-Z).")
                
            # Check that each side has at least one letter
            if any(len(side) == 0 for side in sides):
                raise ValueError("Each side must have at least one letter.")

            # Check for duplicate letters across all sides
            if len(set(combined_sides)) != len(combined_sides):
                raise ValueError(
                    "Duplicate letters found. Please ensure all letters are unique across the sides.")

            print(f"\nYour puzzle: {' | '.join(sides)}")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            if confirm == 'y' or confirm == 'yes':
                return sides
            else:
                print("Let's try again.")

        except ValueError as ve:
            print("Error:", ve)
            print("Please try entering the sides again.")


def show_examples():
    """Show example puzzles to help users understand the format."""
    print("\nExample puzzles:")
    for i, puzzle in enumerate(EXAMPLE_PUZZLES):
        print(f"Example {i+1}: {' | '.join(puzzle)}")
    print()


def main(restart=False):
    import sys
    
    if not restart:
        # Print welcome message
        print("\n" + "=" * 50)
        print("LETTER BOXED SOLVER".center(50))
        print("=" * 50)
        print("\nThis program helps you solve the Letter Boxed word puzzle.")
        print("Enter the letters on each side of the square, and it will find chains")
        print("of words that use all letters with the fewest possible words.")

    try:
        words = load_dict(DICT_NAME)
        print(f"{len(words)} words were loaded from the dictionary.")
    except FileNotFoundError:
        print(f"Error: Dictionary file '{DICT_NAME}' not found.")
        print("Make sure the file exists in the same directory as this program.")
        return

    # Parse command line args (only on first run, not when restarting)
    use_default_puzzle = False
    max_chain_length = 4  # Default value
    show_examples_flag = False

    if not restart:
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--use-default':
                use_default_puzzle = True
            elif arg == '--max-chain' and i+1 < len(sys.argv):
                try:
                    max_chain_length = int(sys.argv[i+1])
                    i += 1  # Skip the next argument
                except ValueError:
                    print(f"Invalid chain length: {sys.argv[i+1]}. Using default of 4.")
            elif arg == '--examples':
                show_examples_flag = True
            elif arg == '--help' or arg == '-h':
                print("Letter Boxed Solver")
                print("Usage: python lbsolver.py [options]")
                print("\nOptions:")
                print("  --use-default      Use the default puzzle")
                print("  --max-chain N      Set maximum chain length (default: 4)")
                print("  --examples         Show example puzzles")
                print("  --help, -h         Show this help message")
                return
            i += 1

        # Show examples if requested
        if show_examples_flag:
            show_examples()
                    
    # Get puzzle letters
    if use_default_puzzle and not restart:
        print(f"Using default puzzle: {DEFAULT_PUZZLE}")
        puzzle = DEFAULT_PUZZLE
    else:
        print("\nLETTER BOXED PUZZLE INPUT")
        print("=======================")
        print("Enter the letters on each side of the square.")
        print("Tip: Each side typically has 3 letters, and all letters must be unique.")
        print("Special commands: 'example', 'help', 'quit'")
        puzzle = get_puzzle()
        
    solve_lb(words, puzzle, max_chain_length)


def solve_puzzle(puzzle):
    """Solve the puzzle and return solutions in a format suitable for the web interface."""
    print(f"Received puzzle data: {puzzle}")
    
    # Get all letters from the puzzle
    all_letters = ''.join(puzzle)
    print(f"All letters: {all_letters}")
    
    # Load dictionary
    words = load_dict(DICT_NAME)
    print(f"Loaded {len(words)} words from dictionary")
    
    # Filter words
    words = eliminate_unavailable_letters(words, all_letters)
    print(f"After eliminating unavailable letters: {len(words)} words")
    
    words = eliminate_consecutives(words, puzzle)  # Pass the puzzle array to check sides
    print(f"After eliminating consecutives: {len(words)} words")
    
    # Find solutions
    solutions = find_chains(words, all_letters)
    print(f"Found {len(solutions)} solutions")
    
    # Format solutions for web interface
    formatted_solutions = []
    for chain in solutions:  # solutions is now just a list of chains
        # Calculate redundancy score
        letter_counts = {}
        for word in chain:
            for letter in word:
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
        redundancy = sum(max(0, count - 1) for count in letter_counts.values())
        
        # Calculate complexity score
        complexity = 0
        for word in chain:
            # Length component
            complexity += len(word) * 0.5
            # Letter frequency component
            rare_letters = "JQXZVBKWYPGFM"
            common_letters = "ETAOINSRHLDCU"
            for letter in word:
                if letter in rare_letters:
                    complexity += 2
                elif letter not in common_letters:
                    complexity += 1
        
        formatted_solutions.append({
            'words': chain,
            'score': len(chain) * 100 - redundancy * 10 - complexity
        })
    
    return formatted_solutions


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-default', action='store_true', help='Use the default puzzle')
    args = parser.parse_args()
    
    if args.use_default:
        puzzle = DEFAULT_PUZZLE
    else:
        puzzle = input("Enter puzzle (4x4 grid of letters): ").strip().split()
    
    solutions = solve_puzzle(puzzle)
    for solution in solutions:
        print(f"Solution: {' → '.join(solution['words'])} (Score: {solution['score']})")
