from abc import ABC, abstractmethod

from dbms.storage_engine.exceptions import StorageExhaustedError


class StorageAllocationStrategy(ABC):
    """Abstract Strategy interface for physical storage space allocation algorithms."""

    @abstractmethod
    def allocate(
        self,
        total_space: int,
        allocations: dict[int, int],
        bytes_needed: int,
    ) -> int:
        """Allocate space of `bytes_needed` and return the starting address offset."""
        pass

    @abstractmethod
    def release(
        self,
        allocations: dict[int, int],
        address: int,
    ) -> bool:
        """Release the allocation at `address`."""
        pass

    @abstractmethod
    def reallocate(
        self,
        total_space: int,
        allocations: dict[int, int],
        address: int,
        new_bytes: int,
    ) -> int:
        """Resize existing allocation at `address` to `new_bytes`."""
        pass


class ContiguousAllocationStrategy(StorageAllocationStrategy):
    """Concrete strategy implementing contiguous block allocation."""

    def allocate(
        self,
        total_space: int,
        allocations: dict[int, int],
        bytes_needed: int,
    ) -> int:
        used_space = sum(allocations.values())
        free_space = total_space - used_space

        if bytes_needed > free_space:
            raise StorageExhaustedError("Insufficient storage space available")

        # Find the lowest available starting address offset that does not overlap
        sorted_allocations = sorted(allocations.items())
        current_offset = 0

        for addr, size in sorted_allocations:
            if addr - current_offset >= bytes_needed:
                allocations[current_offset] = bytes_needed
                return current_offset
            current_offset = max(current_offset, addr + size)

        if total_space - current_offset >= bytes_needed:
            allocations[current_offset] = bytes_needed
            return current_offset

        raise StorageExhaustedError("Insufficient contiguous storage space available")

    def release(
        self,
        allocations: dict[int, int],
        address: int,
    ) -> bool:
        if address not in allocations:
            raise Exception(f"Address {address} is already free or invalid")
        del allocations[address]
        return True

    def reallocate(
        self,
        total_space: int,
        allocations: dict[int, int],
        address: int,
        new_bytes: int,
    ) -> int:
        if address not in allocations:
            raise Exception(f"Address {address} is not allocated")

        old_bytes = allocations[address]
        used_space_excluding_target = sum(allocations.values()) - old_bytes
        free_space = total_space - used_space_excluding_target

        if new_bytes > free_space:
            raise StorageExhaustedError("Insufficient storage space available for reallocation")

        # Check if reallocation can be done in-place or at a new address
        # Temporarily pop target to test allocation
        del allocations[address]

        try:
            # Check if original address can accommodate new_bytes
            sorted_allocations = sorted(allocations.items())
            can_fit_in_place = True
            for addr, size in sorted_allocations:
                if addr > address:
                    if address + new_bytes > addr:
                        can_fit_in_place = False
                    break

            if can_fit_in_place and address + new_bytes <= total_space:
                allocations[address] = new_bytes
                return address

            # Otherwise allocate new address
            new_addr = self.allocate(total_space, allocations, new_bytes)
            return new_addr
        except Exception:
            # Restore original allocation on failure
            allocations[address] = old_bytes
            raise


class StorageAllocator:
    """Context class managing physical storage space using an injected Strategy."""

    def __init__(
        self,
        total_space: int,
        strategy: StorageAllocationStrategy | None = None,
    ) -> None:
        self.total_space: int = total_space
        self.strategy: StorageAllocationStrategy = strategy or ContiguousAllocationStrategy()
        self.allocations: dict[int, int] = {}

    def allocate_space(self, bytes_needed: int) -> int:
        return self.strategy.allocate(self.total_space, self.allocations, bytes_needed)

    def release_space(self, address: int) -> bool:
        return self.strategy.release(self.allocations, address)

    def reallocate_space(self, address: int, new_bytes: int) -> int:
        return self.strategy.reallocate(self.total_space, self.allocations, address, new_bytes)

    def get_free_space(self) -> int:
        return self.total_space - sum(self.allocations.values())
