import os
import subprocess


def ensure_tt_metal_repo():
    """
    Checks if the data/tt-metal folder exists and clones the repository if it doesn't.
    Returns True if successful, False if there was an error.
    """
    tt_metal_path = os.path.join('data', 'tt-metal')
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Check if tt-metal directory already exists
    if not os.path.exists(tt_metal_path):
        try:
            # Clone the repository
            subprocess.run(
                ['git', 'clone', 'git@github.com:tenstorrent/tt-metal.git', '--recurse-submodules', tt_metal_path],
                check=True
            )
            print(f"Successfully cloned tt-metal repository to {tt_metal_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            return False

    return True


def update_tt_metal_repo():
    """
    Updates the tt-metal repository and its submodules.
    Returns True if successful, False if there was an error.
    """
    ensure_tt_metal_repo()
    
    tt_metal_path = os.path.join('data', 'tt-metal')
    
    if not os.path.exists(tt_metal_path):
        print(f"tt-metal repository not found at {tt_metal_path}")
        return False
        
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(tt_metal_path)
        
        # Pull the latest changes
        subprocess.run(['git', 'pull'], check=True)
        
        # Update submodules
        subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'], check=True)
        
        print(f"Successfully updated tt-metal repository at {tt_metal_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating repository: {e}")
        return False
    finally:
        # Always change back to the original directory
        os.chdir(original_dir)


def parse_grep_output(output):
    """
    Parse grep output that includes context lines.

    Grep produces groups of lines separated by a line that is exactly '--'.
    Each line in a group begins with the filename plus a separator (':' for a match
    or '-' for a context line). Instead of parsing each line individually, this function:
    
      1. Finds the group's filename by identifying the line that has the earliest colon.
      2. Uses that filename prefix to trim that many characters (plus one for the separator)
         from every line in the group.
      3. Aggregates the trimmed lines as the file's content.

    Returns a list of dictionaries with keys 'file' and 'content'.
    """
    groups = []
    current_group = []
    for line in output.splitlines():
        if line.strip() == "--":
            if current_group:
                groups.append(current_group)
                current_group = []
            continue
        current_group.append(line)
    if current_group:
        groups.append(current_group)

    processed_matches = []
    
    for group in groups:
        # Determine the file prefix from the line that has the earliest colon.
        candidate_prefix = None
        min_colon_index = None
        for line in group:
            colon_index = line.find(':')
            if colon_index != -1:
                if min_colon_index is None or colon_index < min_colon_index:
                    min_colon_index = colon_index
                    candidate_prefix = line[:colon_index]
        if candidate_prefix is None:
            # No line with colon found; skip this group.
            continue
        
        # Calculate the number of characters to trim:
        # the length of the candidate_prefix plus one (for the separator)
        trim_length = len(candidate_prefix) + 1
        
        # Process each line in the group that starts with candidate_prefix.
        content_lines = []
        for line in group:
            if line.startswith(candidate_prefix):
                # Trim the prefix and the separator.
                content_lines.append(line[trim_length:])
            else:
                # If the line doesn't start with the prefix, include it as-is.
                content_lines.append(line)
        
        processed_matches.append({
            'file': candidate_prefix,
            'content': '\n'.join(content_lines)
        })
    
    return processed_matches


def run_grep_search(search_pattern, search_path, context_before=10, context_after=10,
                    max_matches=5, ignore_case=True, extended_regex=False, exclude_file=None):
    """
    Run a grep search with specified parameters and return processed results.

    Args:
        search_pattern (str): Pattern to search for.
        search_path (str): Path to search in.
        context_before (int): Lines of context before match.
        context_after (int): Lines of context after match.
        max_matches (int): Maximum number of matches per file.
        ignore_case (bool): Whether to ignore case.
        extended_regex (bool): Whether to use extended regex.
        exclude_file (str): Path to file containing exclusion patterns.

    Returns:
        list: List of dictionaries containing file path and matching content.
    """
    try:
        cmd = ['grep', '-r']
        if ignore_case:
            cmd.append('-i')
        if extended_regex:
            cmd.append('-E')
        cmd.extend(['-B', str(context_before)])
        cmd.extend(['-A', str(context_after)])
        cmd.extend(['-m', str(max_matches)])
        cmd.append('--with-filename')
        cmd.append('--color=never')
        if exclude_file:
            cmd.append(f'--exclude-from={exclude_file}')
        cmd.extend([search_pattern, search_path])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # grep returns 1 if no matches are found; that is not an error.
        if result.returncode not in [0, 1]:
            print(f"Error running grep: {result.stderr}")
            return []
        
        # Enforce max_matches limit on the parsed results
        matches = parse_grep_output(result.stdout)
        return matches[:max_matches]
        
    except subprocess.SubprocessError as e:
        print(f"Error during grep search: {e}")
        return []

def search_repo(search_string, tt_metal_path=None):
    """
    Search the repository for a given string using grep, prioritizing different directories.
    Returns matches with 10 lines of context above and below.
    
    Searches in order of priority:
    1. tech-reports/ (up to 5 matches)
    2. models/demos/ (up to 5 matches)
    3. Other directories (up to 5 matches)
    """
    ensure_tt_metal_repo()
    if tt_metal_path is None:
        tt_metal_path = os.path.join('data', 'tt-metal')
    
    if not os.path.exists(tt_metal_path):
        print(f"Repository not found at {tt_metal_path}")
        return []
    
    results = []
    
    # 1. Search tech-reports
    tech_reports_path = os.path.join(tt_metal_path, 'tech-reports')
    if os.path.exists(tech_reports_path):
        results.extend(run_grep_search(search_string, tech_reports_path, max_matches=5))
    
    # 2. Search models/demos
    demos_path = os.path.join(tt_metal_path, 'models', 'demos')
    if os.path.exists(demos_path):
        results.extend(run_grep_search(search_string, demos_path, max_matches=5))
    
    # 3. Search everything else (excluding previous directories)
    try:
        # Create a temporary file with exclude patterns
        exclude_file = '.grep_exclude'
        with open(exclude_file, 'w') as f:
            f.write('tech-reports/*\n')
            f.write('models/demos/*\n')
        
        # Search with exclusions
        results.extend(run_grep_search(
            search_string,
            tt_metal_path,
            exclude_file=exclude_file,
            max_matches=5
        ))
        
        # Clean up temporary file
        os.remove(exclude_file)
        
    except OSError as e:
        print(f"Error during general search: {e}")
    
    return results


def get_more_context(search_terms, search_result):
    """
    Get more context around search terms in a specific file from a search result.
    
    Args:
        search_terms (list): List of search terms to look for
        search_result (dict): A search result dictionary containing 'file' and 'content' keys
        
    Returns:
        str: The file content with 20 lines of context above and below the match,
            or None if there was an error
    """
    try:
        file_path = search_result['file']
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
            
        # Join search terms with | for grep's extended regex OR pattern
        pattern = '|'.join(search_terms)
        
        results = run_grep_search(
            pattern,
            file_path,
            context_before=20,
            context_after=20,
            extended_regex=True
        )
        
        if results:
            return results[0]['content']
        else:
            print(f"No matches found in {file_path}")
            return None
            
    except OSError as e:
        print(f"Error getting more context: {e}")
        return None
