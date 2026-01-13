# Import the MPI module from the mpi4py library
from mpi4py import MPI

# Initialize the MPI communicator
comm = MPI.COMM_WORLD

# Get the rank (unique ID) of the current process
rank = comm.Get_rank()

# Get the total number of processes in the communicator
world_size = comm.Get_size()

# Example data to be sent (used by rank 0)
data = "VERY IMPORTANT DATA"

# If the current process is rank 0 (master process)
# if rank == 0:
#     # Send the data to rank 1
#     comm.send(data, dest=1, tag=11)
#     print("Rank {} sent data to rank {}.".format(rank, 1))

# # If the current process is rank 1 (worker process)
# elif rank == 1:
#     # Receive the data from rank 0
#     data = comm.recv(source=0, tag=11)
#     print("Rank {} received data from rank {}.".format(rank, 0))

# Uncomment the following block for a more general send-receive example

if rank == 0:
    for i in range(1, world_size):  # Send data to all other ranks
        comm.send(data, dest=i, tag=11)
        print("Rank {} sent data to rank {}.".format(rank, i))
else:
    # Receive data from rank 0
    data = comm.recv(source=0, tag=11)
    print("Rank {} received data from rank {}.".format(rank, 0))
