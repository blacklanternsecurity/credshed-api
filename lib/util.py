#!/usr/bin/env python3

# by TheTechromancer

import string
import random

def random_password(length=32):

    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))