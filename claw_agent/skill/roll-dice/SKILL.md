---
name: roll-dice
description: Roll dice using a random number generator. Use when asked to roll a die such as d6 or d20, roll multiple dice, generate random dice results, or simulate tabletop dice.
---

To roll a die, use one of the following commands to generate a random number
from 1 to the given number of sides.

```bash
echo $((RANDOM % <sides> + 1))
```

```powershell
Get-Random -Minimum 1 -Maximum (<sides> + 1)
```

You can also run the bundled script:

```bash
python scripts/roll_die.py <sides>
```

Replace `<sides>` with the number of sides on the die, such as 6 for a
standard die or 20 for a d20.
