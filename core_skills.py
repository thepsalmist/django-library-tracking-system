import random

numbers = [random.randint(1,20) for _ in range (10)]
print(numbers)

# List comprehension
n_below_10_list_comprehension = [n for n in numbers if n < 10]
print(n_below_10_list_comprehension)

# Filter
n_below_10_filter = list(filter(lambda n:n <10, numbers))
print(n_below_10_filter)
