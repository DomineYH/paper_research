#!/usr/bin/env python3
"""
Test script to verify research pipeline works properly
"""

import datetime
import os

# Create a simple test entry
today = datetime.date.today().strftime("%Y-%m-%d")

test_content = f"""# Test Research Pipeline Output - {today}

This is a test entry to verify the git commit functionality works correctly.

## Test Summary
- Date: {today}
- Pipeline: Research Pipeline Test
- Status: Operational

## Next Steps
1. Verify git commit automation
2. Ensure proper file structure
3. Test GitHub integration
"""

# Write test file
with open(f"paper_research/test_output_{today}.md", "w", encoding="utf-8") as f:
    f.write(test_content)

print(f"Test file created: paper_research/test_output_{today}.md")