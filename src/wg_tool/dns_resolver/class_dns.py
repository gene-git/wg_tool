# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=too-few-public-methods
import dns.resolver


class Dns():
    """
    DNS using default stub resolver.
    """
    _resolver: dns.resolver.Resolver
    _initialized: bool = False

    @staticmethod
    def initialize(servers: list[str] | None = None,
                   port: int = 53,
                   search_domains: list[str] | None = None):
        """
        Caching resolver
        """
        if Dns._initialized:
            return

        Dns._resolver = dns.resolver.Resolver(configure=True)
        Dns._resolver.port = port

        if servers is not None:
            Dns._resolver.nameservers = servers

        if search_domains is not None:
            Dns._resolver.search = [
                    dns.name.from_text(dom) for dom in search_domains]
            Dns._resolver.use_search_by_default = True

        Dns._resolver.cache = dns.resolver.Cache()
        Dns._initialized = True

    @staticmethod
    def query(query: str, rr_type: str = 'A',) -> list[str]:
        """
        Cached dns query.

        Args:
            rr_type (str):
                'A' or 'PTR'
        Returns:
            list[str]:
                query result as list.
        """
        rrs: list[str] = []
        if not Dns._initialized:
            Dns.initialize()

        if not query:
            return rrs

        # Do the query
        resolver = Dns._resolver
        try:
            if rr_type == 'PTR':
                res = resolver.resolve_address(query)
            else:
                res = resolver.resolve(query, rr_type)

        except dns.exception.DNSException:
            return rrs

        # get result as text strings
        for rdata in res:
            record = rdata.to_text()
            if record != '0.0.0.0':
                rrs.append(record)
        return rrs
