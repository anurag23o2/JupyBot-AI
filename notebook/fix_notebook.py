import nbformat

def fix_widgets_state(notebook_path):
    nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)
    if 'widgets' in nb['metadata']:
        print("Found 'widgets' in metadata.")
        nb['metadata'].pop('widgets')  # safest fix is just to remove it
        print("Removed 'metadata.widgets' from notebook.")
        nbformat.write(nb, notebook_path)
        print(f"Fixed and saved: {notebook_path}")
    else:
        print("No 'metadata.widgets' found. No changes made.")

# Replace with your notebook filename
fix_widgets_state("JupyBot.ipynb")
