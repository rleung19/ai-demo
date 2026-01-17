# Note on JSON Format

The notebook files (`.ipynb`) use a JSON structure. OML Notebooks may require `.json` format - if so, rename the files back to `.json` extension.

## If JSON Import Doesn't Work

1. **Use Markdown Files Instead**: 
   - `churn_analysis_original.md` - Copy each code block into OML Notebooks
   - `churn_analysis_enhanced.md` - Copy each code block into OML Notebooks

2. **Manual Creation**:
   - Create a new notebook in OML Notebooks UI
   - Copy code from markdown files cell by cell
   - Use `%script` for SQL, `%python` for Python

3. **OML Notebooks Format**:
   - OML Notebooks may use Zeppelin-style JSON
   - If you know the exact format, you can convert the markdown files
   - The markdown files contain all the code needed

## Recommended Approach

**Use the markdown files** (`*.md`) - they are easier to work with and contain all the code in a readable format. Simply:
1. Open the markdown file
2. Copy each code block
3. Paste into a new paragraph in OML Notebooks
4. Set the correct interpreter (`%script` for SQL, `%python` for Python)
