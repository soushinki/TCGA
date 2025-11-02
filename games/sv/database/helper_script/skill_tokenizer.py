# filename: games/sv/database/helper_script/skill_parser.py (Corrected)
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

# --- Tokenizer (Updated) ---
TOKEN_SPECIFICATION = [
    ('EVO_SEP',    r'//'),
    ('EFFECT_SEP', r','),
    ('ARROW_SYM',  r'<-'),
    ('COMPARISON', r'>=|>|<=|<|!='),
    ('NESTED_DYNAMIC', r'\{([^{}]|\{[^{}]*\})*\}'),
    ('DYNAMIC',    r'\{[^{}]*\}'),
    ('ID_WITH_UNDERSCORE', r'\d+_\d+([a-zA-Z0-9_]*)'),
    ('NUMBER',     r'\d+(?:\.\d+)?'),
    ('KEYWORD',    r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('ASSIGN',     r'='),
    ('SEPARATOR',  r'[&|]'),
    ('OPERATOR',   r'[+\-*/%]'),
    ('DOT',        r'\.'),
    ('PAREN_OPEN', r'\('),
    ('PAREN_CLOSE',r'\)'),
    ('COLON',      r':'),
    ('AT_SYM',     r'@'),
    ('OTHER_SYM',  r'[?!]'),
    ('WHITESPACE', r'\s+'),
    ('MISMATCH',   r'.'),
]
TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
STRUCTURAL_TOKENS = {'//', ',', '=', '&', '|', '<', '>', '<=', '>=', '!=', '.', '(', ')', ':', '+', '-', '*', '/', '%', '?', '!', '{}', '{{}}', '@', 'SEQ', 'UNARY_QUESTION'}


def tokenize(text):
    """Yields (token_type, token_value) tuples, ignoring whitespace/mismatch."""
    if not text: return
    for mo in re.finditer(TOKEN_REGEX, text):
        kind, value = mo.lastgroup, mo.group()
        if kind not in ['WHITESPACE', 'MISMATCH']:
            yield (kind, value)

# --- Parser (Updated) ---
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
    
    def expect(expected_kind):
        kind, value = peek()
        if kind == expected_kind:
            return consume() # Correctly calls consume() with no arguments
        raise ValueError(f"Expected token {expected_kind} but got {kind} ('{value}')")
    
    def parse_primary():
        kind, value = peek()
        if kind in ('KEYWORD', 'DYNAMIC', 'NESTED_DYNAMIC', 'NUMBER', 'ARROW_SYM', 'ID_WITH_UNDERSCORE'):
            consume(); return value
        elif kind == 'PAREN_OPEN':
            consume(); expr = parse_or(); expect('PAREN_CLOSE'); return ['(', expr]
        elif kind == 'KEYWORD' and value.lower() == 'none':
             consume(); return 'none'
        elif kind == 'OPERATOR' and value == '-':
             consume() # consume '-'
             primary = parse_primary() 
             return ['UNARY_MINUS', primary]
        elif kind == 'OTHER_SYM' and value == '?':
             consume() # consume '?'
             primary = parse_primary()
             return ['UNARY_QUESTION', primary]
        else:
             if kind is None: raise ValueError("Expected primary value, found end.")
             if value in STRUCTURAL_TOKENS - {'(', '-'}: 
                 raise ValueError(f"Expected primary value but got operator/symbol: {kind} ('{value}')")
             consume(); return value

    def parse_juxtaposition_sequence():
        """
        Parses sequences like (a:b)(c:d) or func(a:b).
        This handles the "juxtaposition" (side-by-side) operator.
        """
        # Get the first item (e.g., 'skill', or the first '(a:b)' block)
        item = parse_primary()
        
        # Peek at the next token
        kind, value = peek()
        
        # If the next token is NOT an open-paren, it's not a sequence.
        # Just return the single item we just parsed.
        if kind != 'PAREN_OPEN':
            return item
        
        # It IS a sequence. Start a sequence node with the first item.
        sequence_node = ['SEQ', item]
        
        # Loop as long as we keep seeing new parenthesized blocks
        while kind == 'PAREN_OPEN':
            # parse_primary() will handle the ( ... ) block
            next_item = parse_primary()
            sequence_node.append(next_item)
            
            # Peek at the next token to see if we continue
            kind, value = peek()
            
        return sequence_node

    def build_binary_op_parser(parse_lower_precedence_func, operators, right_associative=False):
        def parser():
            left = parse_lower_precedence_func() 
            kind, value = peek()
            if right_associative:
                if value in operators:
                    consume(); op = value; right = parser(); return [op, left, right]
                return left
            else: # Left associative
                while value in operators:
                    consume(); op = value
                    right = parse_lower_precedence_func() 
                    left = [op, left, right]
                    kind, value = peek()
                return left
        return parser

    parse_at_sym = build_binary_op_parser(parse_juxtaposition_sequence, {'@'})
    parse_colon_op = build_binary_op_parser(parse_at_sym, {':'})
    parse_term = build_binary_op_parser(parse_colon_op, {'*', '/', '%'})
    parse_expr = build_binary_op_parser(parse_term, {'+', '-'})
    parse_question_op = build_binary_op_parser(parse_expr, {'?'})
    parse_comparison = build_binary_op_parser(parse_question_op, {'>=', '>', '<=', '<', '!='})
    parse_assignment = build_binary_op_parser(parse_comparison, {'='}, right_associative=True)
    parse_and = build_binary_op_parser(parse_assignment, {'&'})
    parse_or = build_binary_op_parser(parse_and, {'|'})
    
    def parse_effect_list():
        if peek()[0] is None or peek()[1] == '//':
             return 'none'
        effects = [parse_or()] 
        while peek()[1] == ',':
            consume()
            if peek()[0] is None or peek()[1] == '//': break
            effects.append(parse_or())
        if len(effects) == 1 and effects[0] == 'none': return 'none'
        return effects

    def parse_toplevel():
        left = parse_effect_list()
        if peek()[1] == '//':
            consume(); op = '//'
            if peek()[0] is None: right = 'none'
            else: right = parse_effect_list()
            return [op, left, right]
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


# --- Function to print the tree with indentation ---
def print_tree_indented(node, indent=""):
    indent_increment = "  "
    if isinstance(node, (list, tuple)):
        is_operator_node = len(node) > 0 and isinstance(node[0], str) and (node[0] in STRUCTURAL_TOKENS or node[0] == 'UNARY_MINUS' or node[0] == '{{}}')
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

# --- Function to reconstruct the string from the tree ---
def reconstruct_from_tree(node):
    if isinstance(node, (list, tuple)):
        is_operator_node = len(node) > 0 and isinstance(node[0], str) and (node[0] in STRUCTURAL_TOKENS or node[0] == 'UNARY_MINUS' or node[0] == '{{}}')
        if is_operator_node:
            op = node[0]
            if op == '{{}}':
                inner_str = reconstruct_from_tree(node[1]) if len(node) > 1 else ""
                return f"{{{{{inner_str}}}}}" 
            elif op == 'UNARY_MINUS':
                return f"-{reconstruct_from_tree(node[1])}"
            elif op == 'UNARY_QUESTION':
                return f"?{reconstruct_from_tree(node[1])}"
            elif op == '(':
                return f"({reconstruct_from_tree(node[1])})"
            elif op == 'SEQ':
                return "".join(reconstruct_from_tree(n) for n in node[1:])
            elif len(node) == 3: # Handle binary operators
                left_str = reconstruct_from_tree(node[1])
                right_str = reconstruct_from_tree(node[2])
                return f"{left_str}{op}{right_str}"
            else: 
                  return op + "".join(reconstruct_from_tree(n) for n in node[1:])
        else: 
             return ",".join(reconstruct_from_tree(item) for item in node)
    elif node is not None:
        return str(node)
    else:
        return ""

# --- verify_reconstruction_for_all_cards (Main loop) ---
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
            if raw_string.strip() and raw_string.strip().lower() != 'none':
                parsed_tree = parse_skill(raw_string)
            elif raw_string.strip().lower() == 'none':
                parsed_tree = 'none'
            else: 
                parsed_tree = None
            cards_processed += 1

            if parsed_tree is not None:
                 reconstructed_string = reconstruct_from_tree(parsed_tree)
                 reconstructed_compact = "".join(reconstructed_string.split())
            else:
                reconstructed_compact = ""

            if raw_string_compact == 'none' and reconstructed_compact == 'none':
                 pass
            elif raw_string_compact != reconstructed_compact:
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