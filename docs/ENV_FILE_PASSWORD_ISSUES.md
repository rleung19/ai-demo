# .env File Password Issues

## Problem: Special Characters in Passwords

If your password contains special characters like `#`, `$`, `!`, etc., they may be interpreted incorrectly in `.env` files.

### The `#` Character Issue

In `.env` files, `#` is used for comments. If your password ends with `#` and is not quoted, everything after the `#` will be treated as a comment and ignored.

**Example - Problem:**
```env
ADB_PASSWORD=MyPassword#123
# The "#123" part might be ignored!
```

**Example - Solution:**
```env
ADB_PASSWORD="MyPassword#123"
# Quoted - the entire password is preserved
```

## Solutions

### Option 1: Quote the Password (Recommended)

Wrap your password in double quotes:

```env
ADB_PASSWORD="YourPassword#123"
```

### Option 2: Escape Special Characters

For some special characters, you can escape them:

```env
ADB_PASSWORD=MyPassword\#123
```

### Option 3: Use Single Quotes

Single quotes also work:

```env
ADB_PASSWORD='YourPassword#123'
```

## Special Characters to Watch For

- `#` - Comment delimiter
- `$` - Variable expansion (in some contexts)
- `!` - History expansion (in some shells)
- `` ` `` - Command substitution
- `"` - String delimiter
- `'` - String delimiter
- Spaces - May need quoting

## Testing Your Password

To verify your password is loaded correctly:

```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
pwd = os.getenv('ADB_PASSWORD', '')
print('Password length:', len(pwd))
print('Password ends with #:', pwd.endswith('#'))
print('Last 5 chars:', pwd[-5:] if len(pwd) >= 5 else pwd)
"
```

If the password doesn't end with `#` when it should, it's being truncated.

## Best Practice

**Always quote passwords in .env files**, especially if they contain:
- Special characters
- Spaces
- Symbols

```env
ADB_PASSWORD="YourPassword#123"
```

This ensures the entire password is preserved regardless of special characters.
