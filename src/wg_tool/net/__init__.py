# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
'''
net module
'''
from .networks import NetWorks

from .network import NetWork
from .network import wg_address_to_address
from .network import wq_addresses_to_addresses

from .tools import internet_networks
from .tools import cidr_in_cidrs

from .shared import NetsShared
