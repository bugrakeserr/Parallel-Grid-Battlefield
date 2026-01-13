# Import the MPI module from the mpi4py library
from mpi4py import MPI

# Initialize the MPI communicator
comm = MPI.COMM_WORLD

# Get the rank (unique ID) of the current process
rank = comm.Get_rank()

# Get the total number of processes in the communicator
world_size = comm.Get_size()

# Example data to be sent by rank 0
data = {"a": 1, "b": 2, "c": 3}  # Dictionary as the data
# data = [1, 2, 3, 4, 5]  # Example of using a list instead (alternative data)

# If the current process is rank 0 (master process)
if rank == 0:
    # Loop through all other ranks to send the data
    for i in range(1, world_size):
        comm.send(data, dest=i, tag=11)  # Send data to rank i with tag 11
        print("Rank {} sent data {} to rank {}.".format(rank, data, i))

# If the current process is not rank 0 (worker process)
else:
    # Receive the data from rank 0
    data = comm.recv(source=0, tag=11)
    print("Rank {} received data {} from rank {}.".format(rank, data, 0))
