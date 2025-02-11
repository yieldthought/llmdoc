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
    Search the repository for a given string using grep, prioritizing different directories.
    Returns matches with 10 lines of context above and below.
    
    Searches in order of priority:
    1. tech-reports/ (up to 5 matches)
    2. models/demos/ (up to 5 matches)
    3. Other directories (up to 5 matches)
    
    Args:
        search_string (str): The string to search for
        tt_metal_path (str, optional): Path to the repository. If None, uses default path.
    
    Returns:
        list: List of dictionaries containing file path and matching content
    """
    ensure_tt_metal_repo()
    if tt_metal_path is None:
        tt_metal_path = os.path.join('data', 'tt-metal')
    
    if not os.path.exists(tt_metal_path):
        print(f"Repository not found at {tt_metal_path}")
        return []
    
    def search_directory(dir_path, max_matches=5):
        try:
            # Use grep with directory-specific search
            result = subprocess.run([
                'grep',
                '-r',
                '-n',
                '-B', '10',
                '-A', '10',
                '-m', str(max_matches),
                '--color=never',
                search_string,
                dir_path
            ], capture_output=True, text=True)
            
            matches = result.stdout.split('--')
            processed_matches = []
            
            for match in matches:
                if not match.strip():
                    continue
                    
                lines = match.strip().split('\n')
                if not lines or ':' not in lines[0]:
                    continue
                    
                file_path, _ = lines[0].split(':', 1)
                processed_matches.append({
                    'file': file_path,
                    'content': match.strip()
                })
            
            return processed_matches
            
        except subprocess.CalledProcessError:
            return []
    
    # Search in priority order
    tech_reports_path = os.path.join(tt_metal_path, 'tech-reports')
    demos_path = os.path.join(tt_metal_path, 'models', 'demos')
    
    results = []
    
    # 1. Search tech-reports
    if os.path.exists(tech_reports_path):
        results.extend(search_directory(tech_reports_path))
    
    # 2. Search models/demos
    if os.path.exists(demos_path):
        results.extend(search_directory(demos_path))
    
    # 3. Search everything else (excluding previous directories)
    try:
        # Create a temporary file with exclude patterns
        exclude_file = '.grep_exclude'
        with open(exclude_file, 'w') as f:
            f.write('tech-reports/*\n')
            f.write('models/demos/*\n')
        
        # Search with exclusions
        result = subprocess.run([
            'grep',
            '-r',
            '-n',
            '-B', '10',
            '-A', '10',
            '-m', '5',
            '--color=never',
            '--exclude-from=' + exclude_file,
            search_string,
            tt_metal_path
        ], capture_output=True, text=True)
        
        matches = result.stdout.split('--')
        for match in matches:
            if not match.strip():
                continue
                
            lines = match.strip().split('\n')
            if not lines or ':' not in lines[0]:
                continue
                
            file_path, _ = lines[0].split(':', 1)
            results.append({
                'file': file_path,
                'content': match.strip()
            })
        
        # Clean up temporary file
        os.remove(exclude_file)
        
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"Error during general search: {e}")
    
    return results


