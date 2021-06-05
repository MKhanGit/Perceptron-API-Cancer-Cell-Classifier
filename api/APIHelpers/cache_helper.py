from APIHelpers.io_helper import save_pretrained_network


class GlobalCacheHelper:
    def __init__(self, max_size=50):
        self.global_cache = dict()
        self.max_size = max_size
        self.access_counter = SequentialIDGenerator()

    def keys(self):
        return self.global_cache.keys()

    def get_stack(self):
        # Cache is organized in the format of {'key': ('value', last_access_time)}
        return sorted(self.global_cache.items(), key=lambda item: item[1][1])  # sort based on last access

    def read(self, key):
        if key in self.global_cache.keys():
            val = self.global_cache[key][0]
            self.global_cache[key] = (val, self.access_counter.next())  # Update last access
            return val

    def add(self, key, val):
        self.global_cache[key] = (val, self.access_counter.next())
        # Remove overflows from cache and store to disk
        while len(self.global_cache.keys()) > self.max_size:
            sorted_cache = sorted(self.global_cache.items(), key=lambda item: item[1][1])
            removal_key = sorted_cache[0][0]  # sorted by access time
            removed_entry = self.global_cache.pop(removal_key)
            if isinstance(removed_entry[0], tuple):
                save_pretrained_network(removed_entry[0][0], removed_entry[0][1])

    def pop(self, key):
        if key in self.global_cache.keys():
            removed_entry = self.global_cache.pop(key)[0]
            if isinstance(removed_entry, tuple):
                save_pretrained_network(removed_entry[0], removed_entry[1])
            return removed_entry

    def flush(self):
        gckeys = list(self.global_cache.keys())
        for key in gckeys:
            self.pop(key)
        self.access_counter.reset()


class SequentialIDGenerator:
    def __init__(self, start_id=0):
        self.curr = int(start_id) - 1
        self.nxt = self.curr

    def next(self):
        self._inc()
        return self.nxt

    def reset(self, start_id=0):
        self.curr = int(start_id) - 1
        self.nxt = self.curr

    def _inc(self):
        self.curr += 1
        self.nxt += 1
