# Fix: Node.js Password Truncation Issue

## Problem

Node.js `dotenv` is truncating the password because `#` is treated as a comment delimiter in `.env` files.

**Symptoms:**
- Python connection works (16 characters, ends with `#`)
- Node.js connection fails with "ORA-01017: invalid credential"
- Node.js password is only 15 characters, doesn't end with `#`

## Solution

Quote the password in your `.env` file:

**Before (doesn't work in Node.js):**
```env
ADB_PASSWORD=YourPassword#123
```

**After (works in both Python and Node.js):**
```env
ADB_PASSWORD="YourPassword#123"
```

Or use single quotes:
```env
ADB_PASSWORD='YourPassword#123'
```

## Why This Happens

- `dotenv` in Node.js treats `#` as a comment delimiter
- Everything after `#` is ignored if not quoted
- `python-dotenv` handles this more gracefully, but quoting is still recommended

## Verification

After updating `.env`, test:

```bash
# Test password loading
node -e "require('dotenv').config(); const pwd = process.env.ADB_PASSWORD; console.log('Length:', pwd?.length); console.log('Ends with #:', pwd?.endsWith('#'));"

# Should show:
# Length: 16
# Ends with #: true
```

Then test connection:
```bash
node scripts/test-node-connection.js
```

## Best Practice

**Always quote passwords in `.env` files** if they contain:
- `#` (comment delimiter)
- `$` (variable expansion)
- Spaces
- Special characters

This ensures consistent behavior across Python and Node.js.
