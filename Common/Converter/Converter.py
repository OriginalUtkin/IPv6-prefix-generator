import ipaddress
import attr

from typing import Dict, List


@attr.s
class Converter:
    """Convert all output prefixes to hexadecimal representation"""

    binary_prefixes = attr.ib(factory=list, type=list)

    def _normalize_prefix(self, prefix) -> Dict[str, str]:
        """Normalize prefix length to 128 bits if needed.

        :param prefix: string; binary prefix representation of prefix for normalization
        :return: dictionary; binary representation of prefix has a len as 128 bits / previous prefix len
        """
        prefix_len = len(prefix)
        expected_len = ipaddress.IPV6LENGTH

        if prefix_len != expected_len:
            additional_bits = expected_len - prefix_len
            normalized = prefix + ''.join(['0' for _ in range(additional_bits)])

            return {"prefix": normalized, "prefix_len": prefix_len}

        return {"prefix": prefix, "prefix_len": prefix_len}

    def _get_hex_repr(self, prefix) -> str:
        """Convert binary representation of prefix to hexadecimal representation.

        :param prefix: string; binary representation of prefix
        :return: string; converted prefix to hexadecimal which has a format prefix/prefix_len
        """
        normalized_prefix = self._normalize_prefix(prefix)
        hex_repr = ipaddress.IPv6Address(int(normalized_prefix['prefix'], 2))

        return f"{hex_repr}/{normalized_prefix['prefix_len']}"

    def convert_prefixes(self) -> List[str]:
        """Converting all prefixes after generating process to hexadecimal representation.

        :return: list; list with converted prefixes
        """
        converted_prefixes = []

        for prefix in self.binary_prefixes:
            converted_prefix = self._get_hex_repr(prefix)
            converted_prefixes.append(converted_prefix)

        return converted_prefixes
