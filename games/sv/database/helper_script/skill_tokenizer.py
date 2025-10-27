# filename: games/sv/database/helper_script/skill_parser.py (Parser v5 - Simpler Dynamic, Refined Logic)
import json
import os
import sys
import re
import random
import pprint

# --- Configuration ---
FIELD_TO_ANALYZE = "skill_condition"
DB_FILENAME = "all_sv_cards_slim.json"
# --- End Configuration ---

# --- Helper Function ---
def is_numeric(token_value):
    if isinstance(token_value, (int, float)): return True
    return isinstance(token_value, str) and re.fullmatch(r'-?\d+(\.?\d+)?', token_value) is not None

# --- Tokenizer (Treats {..} as single DYNAMIC token) ---
TOKEN_SPECIFICATION = [
    ('EVO_SEP',    r'//'),
    ('EFFECT_SEP', r','),
    ('DYNAMIC',    r'\{[^{}]*\}'), # Treat whole {..} as one token
    ('NUMBER',     r'-?\d+(?:\.\d+)?'),
    ('KEYWORD',    r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('ASSIGN',     r'='),
    ('SEPARATOR',  r'[&|]'),
    ('COMPARISON', r'>=|>|<=|<|!='),
    ('OPERATOR',   r'[+\-*/%]'), # Included arithmetic
    ('DOT',        r'\.'),
    ('PAREN_OPEN', r'\('),
    ('PAREN_CLOSE',r'\)'),
    ('COLON',      r':'),
    # Removed explicit braces
    ('OTHER_SYM',  r'[?!]'),
    ('WHITESPACE', r'\s+'),
    ('MISMATCH',   r'.'),
]
TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
STRUCTURAL_TOKENS = {'//', ',', '=', '&', '|', '<', '>', '<=', '>=', '!=', '+', '-', '*', '/', '%'} # Removed .()?!:{}


def tokenize(text):
    if not text: return
    for mo in re.finditer(TOKEN_REGEX, text):
        kind, value = mo.lastgroup, mo.group()
        if kind not in ['WHITESPACE', 'MISMATCH']:
            yield (kind, value)

# --- Parser (Revised Precedence and Logic) ---
def parse_skill(skill_str):
    if not isinstance(skill_str, str) or not skill_str.strip(): return None
    tokens = list(tokenize(skill_str))
    if not tokens: return None
    token_index = 0
    def peek(): return tokens[token_index] if token_index < len(tokens) else (None, None)
    def consume():
        nonlocal token_index
        kind, value = peek()
        if kind is None: raise ValueError("Unexpected end of input during consume")
        token_index += 1
        if kind == 'NUMBER':
            try: return kind, (float(value) if '.' in value else int(value))
            except ValueError: return kind, value
        return kind, value

    # --- Revised Parsing Functions ---
    def parse_primary():
        kind, value = peek()
        # Treat DYNAMIC as a primary leaf node
        if kind in ('KEYWORD', 'DYNAMIC', 'NUMBER'):
            consume(); return value
        elif kind == 'PAREN_OPEN':
            consume(); expr = parse_toplevel(); consume('PAREN_CLOSE'); return expr
        elif kind == 'KEYWORD' and value.lower() == 'none':
             consume(); return 'none'
        else:
             if kind is None: raise ValueError("Expected primary value, found end.")
             # If it's an operator, something is wrong with precedence
             if value in STRUCTURAL_TOKENS:
                  raise ValueError(f"Expected primary value but got operator/separator: {kind} ('{value}')")
             consume(); return value # Pass unknown symbols?

    # Build parser using operator precedence (calls go from lower to higher precedence)
    def build_parser(parse_lower_precedence_func, operators, right_associative=False):
        # This needs careful token checking to prevent over-consuming
        def parser():
            # --- TYPO FIX: Use parse_lower_precedence_func ---
            left = parse_lower_precedence_func()
            kind, value = peek()
            while value in operators:
                consume() # Consume operator
                op = value
                if peek()[0] is None:
                     raise ValueError(f"Unexpected end of input after operator '{op}'")

                if right_associative:
                    right = parser()
                else:
                    # --- TYPO FIX: Use parse_lower_precedence_func ---
                    right = parse_lower_precedence_func()

                left = [op, left, right]
                kind, value = peek() # Look ahead for next iteration
            return left
        return parser

    # Define the chain based on precedence
    parse_term = build_parser(parse_primary, {'*', '/', '%'})
    parse_expr = build_parser(parse_term, {'+', '-'})
    parse_comparison = build_parser(parse_expr, {'>=', '>', '<=', '<', '!='})
    parse_assignment = build_parser(parse_comparison, {'='}, right_associative=True)
    parse_and = build_parser(parse_assignment, {'&'})
    parse_or = build_parser(parse_and, {'|'})
    parse_effect = parse_or # Base for a single effect between commas

    def parse_effect_list():
        effects = []
        if peek()[0] is None or peek()[1] == '//':
            return None
        effects.append(parse_effect()) # Parse the first effect
        while peek()[1] == ',':
            consume() # Consume ','
            if peek()[0] is None or peek()[1] == '//': break
            effects.append(parse_effect())
        if len(effects) == 1 and effects[0] == 'none': return 'none'
        return effects

    def parse_toplevel():
        left = parse_effect_list()
        if peek()[1] == '//':
            consume() # Consume '//'
            op = '//'
            if peek()[0] is None: right = None
            else: right = parse_effect_list()
            if left == 'none' and right is None: return None
            if left == 'none' and right == 'none': return None
            return [op, left if left is not None else [], right if right is not None else []]
        return left

    # --- Start Parsing ---
    try:
        tree = parse_toplevel()
        if token_index < len(tokens):
             raise ValueError(f"Parser did not consume all tokens. Remainder: {tokens[token_index:]}")
        return tree
    except ValueError as e:
        remaining_tokens = tokens[token_index:] if token_index < len(tokens) else "None"
        raise ValueError(f"Parsing failed: {e}. Remaining tokens: {remaining_tokens}")
    except Exception as e:
        remaining_tokens = tokens[token_index:] if token_index < len(tokens) else "N/A"
        raise ValueError(f"Unexpected parsing error: {e}. Near: {remaining_tokens}")

# --- (print_tree_indented function remains the same) ---
def print_tree_indented(node, indent=""):
    indent_increment = "  "
    if isinstance(node, (list, tuple)):
        is_operator_node = len(node) > 0 and isinstance(node[0], str) and node[0] in STRUCTURAL_TOKENS
        if is_operator_node:
            print(f"{indent}{node[0]}")
            for i in range(1, len(node)):
                print_tree_indented(node[i], indent + indent_increment)
        else:
             print(f"{indent}[Group/List]")
             for item in node:
                 print_tree_indented(item, indent + indent_increment)
    elif node is not None:
        print(f"{indent}{node}")

# --- (reconstruct_from_tree function remains the same) ---
def reconstruct_from_tree(node):
    if isinstance(node, (list, tuple)):
        is_operator_node = len(node) > 0 and isinstance(node[0], str) and node[0] in STRUCTURAL_TOKENS
        if is_operator_node:
            op = node[0]
            if len(node) == 3:
                left_str = reconstruct_from_tree(node[1])
                right_str = reconstruct_from_tree(node[2])
                return f"{left_str}{op}{right_str}"
            elif len(node) == 2 and op == '//':
                left_str = reconstruct_from_tree(node[1])
                return f"{left_str}{op}"
            else:
                  return op + "".join(reconstruct_from_tree(n) for n in node[1:])
        else:
             return ",".join(reconstruct_from_tree(item) for item in node)
    elif node is not None:
        return str(node)
    else:
        return ""

# --- (verify_reconstruction_for_all_cards function remains the same) ---
def verify_reconstruction_for_all_cards():
    script_dir = os.path.dirname(__file__)
    db_parent_path = os.path.join(script_dir, '..')
    db_filepath = os.path.join(db_parent_path, DB_FILENAME)
    print(f"--- Verifying Reconstruction for '{FIELD_TO_ANALYZE}' Field ---")
    print(f"Loading data from '{db_filepath}'...")
    try:
        with open(db_filepath, 'r', encoding='utf-8') as f: all_cards_data = json.load(f)
        print(f"Successfully loaded {len(all_cards_data)} cards.")
    except Exception as e: print(f"FATAL ERROR loading JSON: {e}"); sys.exit(1)

    mismatches_found = 0; cards_processed = 0; parse_errors = 0
    print("\n--- Checking for Mismatches ---")

    for card in all_cards_data:
        card_id = card.get('card_id', 'UnknownID'); field_string = card.get(FIELD_TO_ANALYZE)
        raw_string = field_string if isinstance(field_string, str) else ""
        raw_string_compact = "".join(raw_string.split())

        parsed_tree = None; reconstructed_string = ""; reconstructed_compact = ""

        try:
            if raw_string.strip(): parsed_tree = parse_skill(raw_string)
            else: parsed_tree = None
            cards_processed += 1

            if parsed_tree is not None:
                 reconstructed_string = reconstruct_from_tree(parsed_tree)
                 reconstructed_compact = "".join(reconstructed_string.split())

            if raw_string_compact != reconstructed_compact:
                mismatches_found += 1
                print("-" * 40); print(f"MISMATCH FOUND for Card ID: {card_id} ({card.get('card_name', '')})")
                print(f"\n1. Raw String:\n   '{raw_string}'"); print("\n2. Parsed Tree (Indented):")
                if parsed_tree is None: print("   (Parsing resulted in None)")
                else: print_tree_indented(parsed_tree)
                print("\n3. Reconstructed String:"); print(f"   '{reconstructed_string}'"); print("-" * 40)

        except Exception as e:
            parse_errors += 1
            print("-" * 40); print(f"ERROR processing Card ID: {card_id} ({card.get('card_name', '')})")
            print(f"Raw String: '{raw_string}'"); print(f"Error: {e}"); print("-" * 40)
            continue

    print("\n--- Verification Summary ---"); print(f"Total cards checked: {len(all_cards_data)}")
    print(f"Cards successfully processed (parsed & reconstructed): {cards_processed - parse_errors}")
    print(f"Mismatches between raw (compacted) and reconstructed (compacted) strings: {mismatches_found}")
    print(f"Errors during parsing/reconstruction: {parse_errors}")
    if mismatches_found == 0 and parse_errors == 0: print("✅ All processed strings reconstructed successfully!")
    elif mismatches_found > 0: print("❌ Found mismatches. See details above.")
    elif parse_errors > 0: print("❌ Encountered errors. See details above.")


# --- Execution ---
if __name__ == "__main__":
    DB_FILENAME = "all_sv_cards_slim.json"
    try: verify_reconstruction_for_all_cards()
    except Exception as e: print(f"An unexpected top-level error: {e}")