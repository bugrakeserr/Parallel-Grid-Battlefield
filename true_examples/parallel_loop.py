# Import the MPI module from the mpi4py library
from mpi4py import MPI

# Total number of "numbers" to distribute among ranks
numbers = 40

# Get the rank (unique ID) of the current process
rank = MPI.COMM_WORLD.Get_rank()

# Get the total number of processes in the communicator
n_ranks = MPI.COMM_WORLD.Get_size()

# Calculate how many numbers each rank should handle
numbers_per_rank = numbers // n_ranks

# If there are leftover numbers, distribute them by increasing the workload of some ranks
if numbers % n_ranks > 0:
    numbers_per_rank += 1

# Calculate the range of numbers this rank will handle
my_first = rank * numbers_per_rank  # Starting number for this rank
my_last = my_first + numbers_per_rank  # Ending number (exclusive) for this rank

# Loop through the assigned range and print the numbers this rank is responsible for
for i in range(my_first, my_last):
    if i < numbers:  # Ensure we don't exceed the total count of numbers
        print("I'm rank {:d} and I'm printing the number {:d}.".format(rank, i))
