"""
Optimized and enhanced implementation for CRC testing and calculations.
"""

import time
import unittest
from urh.signalprocessing.Encoding import Encoding
from urh.util import util
from urh.util.GenericCRC import GenericCRC
from urh.util.WSPChecksum import WSPChecksum


class OptimizedCRC(unittest.TestCase):
    """
    Test cases for validating CRC calculations with optimizations.
    """

    def test_crc(self):
        """
        Validate CRC values against known results.
        """
        c = GenericCRC(polynomial=WSPChecksum.CRC_8_POLYNOMIAL)
        e = Encoding()

        bitstr = [
            "010101010110100111011010111011101110111011100110001011101010001011101110110110101101",
            "010101010110101001101110111011101110111011100110001011101010001011101110110111100101",
            "010101010110100111010010111011101110111011100110001011101010001011101110110110100101",
        ]

        expected = ["78", "c9", "f2"]

        for value, expect in zip(bitstr, expected):
            self.assertEqual(util.bit2hex(c.crc(e.str2bit(value[4:-8]))), expect)

    def test_crc8(self):
        """
        Validate CRC-8 calculations.
        """
        messages = ["aabbcc", "abcdee", "dacafe"]
        expected = ["7d", "24", "33"]
        crc = GenericCRC(polynomial=GenericCRC.DEFAULT_POLYNOMIALS["8_ccitt"])

        for msg, expect in zip(messages, expected):
            bits = util.hex2bit(msg)
            self.assertEqual(util.bit2hex(crc.crc(bits)), expect)

    def test_multiple_crc_scenarios(self):
        """
        Test CRC with various configurations.
        """
        c = GenericCRC(
            polynomial="16_standard",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        bitstrings = [
            "101001001010101010101011101111111000000000000111101010011101011",
            "101001001010101101111010110111101010010110111010",
            "00000000000000000000000000000000100000000000000000000000000000000001111111111111",
        ]

        for bitstr in bitstrings:
            crc_new = c.crc(c.str2bit(bitstr))
            crc_ref = c.reference_crc(c.str2bit(bitstr))
            self.assertEqual(crc_new, crc_ref)

    def test_adaptive_crc(self):
        """
        Test adaptive CRC calculation for performance improvements.
        """
        c = GenericCRC(polynomial="16_ccitt")
        input_data = "10101010101010"
        input_data_extended = "1010101010101001"

        crc1 = c.crc(c.str2arr(input_data))
        crc2 = c.crc(c.str2arr(input_data_extended))

        # Compute crc2 from crc1 using delta
        delta = "01"
        c.start_value = crc1
        crcx = c.crc(c.str2arr(delta))

        self.assertEqual(crcx, crc2)

    def test_cache_mechanism(self):
        """
        Validate cache mechanism for CRC calculations.
        """
        c = GenericCRC(polynomial="16_standard")
        c.calculate_cache(8)
        self.assertEqual(len(c.cache), 256)

    def test_performance(self):
        """
        Ensure CRC calculation meets performance criteria.
        """
        c = GenericCRC(polynomial="16_ccitt")
        input_data = "10101010101010" * 1000
        runs = 100
        elapsed_time = 0

        for _ in range(runs):
            start = time.time()
            c.crc(c.str2arr(input_data))
            elapsed_time += time.time() - start

        avg_time = elapsed_time / runs
        self.assertLess(avg_time, 0.05)

    def test_reverse_polynomial(self):
        """
        Test polynomial reversal and validate results.
        """
        c = GenericCRC(polynomial="16_standard")
        c.reverse_polynomial = True
        input_data = "101001001010101010101011101111111000000000000111101010011101011"

        crc_reversed = c.crc(c.str2bit(input_data))
        crc_normal = c.reference_crc(c.str2bit(input_data))

        self.assertEqual(crc_reversed, crc_normal)


if __name__ == "__main__":
    unittest.main()

