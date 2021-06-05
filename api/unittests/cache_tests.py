import unittest
from APIHelpers.cache_helper import GlobalCacheHelper


class TestCacheSystem(unittest.TestCase):
    def test_cache_sanity(self):
        expected_stack = ["SampleNet_{0}".format(i) for i in range(10)]
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=10)
        for i in range(10):
            test_cache.add("SampleNet_{}".format(i), ("Network_{}".format(i), "./bin/samplenet_{}.bin".format(i)))
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(calculated_stack), len(expected_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_trimming(self):
        expected_stack = [5, 6, 7, 8, 9]  # stack should be trimmed based on max size and recently created/accessed
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=5)
        for i in range(10):
            test_cache.add(i, i)
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_lru(self):
        expected_stack = [0, 1, 3, 5, 7, 8, 9, 2, 4, 6]  # stack should be reordered based on recently accessed items
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=10)
        for i in range(10):
            test_cache.add(i, i)
        test_cache.read(2)  # Access cached data, leads to new access time being set internally, reordering the stack
        test_cache.read(4)
        test_cache.read(6)
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_flush(self):
        expected_stack = []   # stack should be empty after a flush
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=10)
        for i in range(10):
            test_cache.add(i, i)
        test_cache.flush()
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_flush_after_read(self):
        expected_stack = []   # stack should be empty after a flush
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=10)
        for i in range(10):
            test_cache.add(i, i)
        test_cache.read(2)
        test_cache.read(4)
        test_cache.read(6)
        test_cache.flush()
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_trimming_lru(self):
        expected_stack = [9, 6, 5, 8, 11, 13, 14, 15, 12, 10]
        test_cache = GlobalCacheHelper(max_size=10)
        # Test Instructions
        for i in range(10):
            test_cache.add(i, i)
        test_cache.read(6)
        test_cache.read(5)
        test_cache.read(8)
        for i in range(10, 16):
            test_cache.add(i, i)
        test_cache.read(12)
        test_cache.read(10)
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_flush_continue(self):
        expected_stack = [0, 1, 3, 2, 4]
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=10)
        for i in range(10):
            test_cache.add(i, i)
        test_cache.flush()
        for i in range(5):
            test_cache.add(i, i)
        test_cache.read(2)
        test_cache.read(4)
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_pop(self):
        expected_stack = [1, 2, 4, 5, 6, 8, 9]
        # Test Instructions
        test_cache = GlobalCacheHelper(max_size=10)
        for i in range(10):
            test_cache.add(i, "val_{0}".format(i))
        v_0 = test_cache.pop(0)
        v_3 = test_cache.pop(3)
        v_7 = test_cache.pop(7)
        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        self.assertEqual(v_0, "val_0")
        self.assertEqual(v_3, "val_3")
        self.assertEqual(v_7, "val_7")
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_lru_pop(self):
        test_cache = GlobalCacheHelper(max_size=10)
        expected_stack = [1, 5, 8, 9, 2, 4, 6]
        # Perform operations on cache prior to flush
        for i in range(10):
            test_cache.add(i, ("Network_{}".format(i), "./bin/samplenet_{}.bin".format(i)))

        test_cache.read(2)
        test_cache.read(4)
        test_cache.read(6)
        # Pop values from the stack
        test_cache.pop(0)
        test_cache.pop(3)
        test_cache.pop(7)

        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])

    def test_cache_large(self):
        test_cache = GlobalCacheHelper(max_size=100000)
        expected_stack = [i for i in range(9999)]

        for i in range(9999):
            test_cache.add(i, str(i))

        # Assertions
        calculated_stack = test_cache.get_stack()
        self.assertEqual(len(expected_stack), len(calculated_stack))
        for k in range(len(calculated_stack)):
            self.assertEqual(calculated_stack[k][0], expected_stack[k])


if __name__ == '__main__':
    unittest.main()
