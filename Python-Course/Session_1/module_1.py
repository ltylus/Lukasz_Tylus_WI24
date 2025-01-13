from typing import List


def task_1(array: List[int], target: int) -> List[int]:
    seen = {}  # Dictionary to store numbers we've seen so far
    for num in sample:
        complement = target - num
        if complement in seen:
            return [complement, num]  # Return the pair if found
        seen[num] = True  # Add the current number to the dictionary
    return []  # Return an empty list if no pair is found


def task_2(number: int) -> int:
    reversed_number = 0
    while num > 0:
        last_digit = num % 10  # Extract the last digit
        reversed_number = reversed_number * 10 + last_digit  # Append the digit
        num //= 10  # Remove the last digit from the original number
    return reversed_number


def task_3(array: List[int]) -> int:
    for num in nums:
        index = abs(num) - 1  # Convert the number to a 0-based index
        if nums[index] < 0:
            return abs(num)  # The number is a duplicate
        nums[index] = -nums[index]  # Mark the number as visited by negating the value
    return -1  # No duplicate found


def task_4(string: str) -> int:
    # Mapping of Roman numerals to integers
    roman_map = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    total = 0
    n = len(roman)
    
    for i in range(n):
        # If this is not the last character and the current value is less than the next
        if i < n - 1 and roman_map[roman[i]] < roman_map[roman[i + 1]]:
            total -= roman_map[roman[i]]  # Subtract the value
        else:
            total += roman_map[roman[i]]  # Add the value
            
    return total


def task_5(array: List[int]) -> int:
    if not nums:  # Handle empty list edge case
        return None  # Or some other indicator for no elements
    smallest = nums[0]  # Assume the first element is the smallest
    for num in nums:
        if num < smallest:
            smallest = num  # Update the smallest number
    return smallest
