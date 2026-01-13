# Import the MPI module from the mpi4py library
from mpi4py import MPI

# Initialize the communicator, which is the default communication group
comm = MPI.COMM_WORLD

# Get the total number of processes in the communicator
world_size = comm.Get_size()

# Get the rank (unique ID) of the current process in the communicator
rank = comm.Get_rank()

# Print a message showing the rank of the process and the total number of processes
# print("Hello from rank: {} of a world of {}".format(rank, world_size))

# Uncomment the following block to demonstrate a master-worker message pattern

if rank == 0:
    # Print a specific message for the master process (rank 0)
    print("Hello from master, my rank is: {}".format(rank))
else:
    # Print a message for the worker processes (all ranks other than 0)
    print("Hello from worker with rank: {}".format(rank))
