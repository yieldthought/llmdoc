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


def search_repo(search_string, tt_metal_path=None):
    """
    Search the repository for a given string using grep.
    Returns matches with 10 lines of context above and below, limited to 10 matches.
    
    Args:
        search_string (str): The string to search for
        tt_metal_path (str, optional): Path to the repository. If None, uses default path.
    
    Returns:
        list: List of dictionaries containing file path and matching content
    """
    if tt_metal_path is None:
        tt_metal_path = os.path.join('data', 'tt-metal')
    
    if not os.path.exists(tt_metal_path):
        print(f"Repository not found at {tt_metal_path}")
        return []
    
    try:
        # Use grep with:
        # -r: recursive search
        # -l: show file names
        # -n: show line numbers
        # -B 10: show 10 lines before match
        # -A 10: show 10 lines after match
        # -m 10: stop after 10 matches
        # --color=never: disable color output
        result = subprocess.run([
            'grep',
            '-r',
            '-n',
            '-B', '10',
            '-A', '10',
            '-m', '10',
            '--color=never',
            search_string,
            tt_metal_path
        ], capture_output=True, text=True)
        
        # Split output into separate match groups
        matches = result.stdout.split('--')
        
        # Process matches into a more structured format
        processed_matches = []
        for match in matches:
            if not match.strip():
                continue
                
            lines = match.strip().split('\n')
            if not lines:
                continue
                
            # First line contains file name and line number
            first_line = lines[0]
            if ':' not in first_line:
                continue
                
            file_path, _ = first_line.split(':', 1)
            
            processed_matches.append({
                'file': file_path,
                'content': match.strip()
            })
        
        return processed_matches
        
    except subprocess.CalledProcessError as e:
        print(f"Error searching repository: {e}")
        return []


