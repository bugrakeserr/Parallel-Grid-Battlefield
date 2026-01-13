# Import the MPI module from the mpi4py library
from mpi4py import MPI

# Initialize the MPI communicator
comm = MPI.COMM_WORLD

# Ensure there are exactly 2 processes for this program to work
assert comm.Get_size() == 2

# Get the rank (unique ID) of the current process
rank = comm.Get_rank()

# Initialize a counter for the "ping-pong" exchanges
count = 0

# Loop to simulate a ping-pong game (up to 5 exchanges)
while count < 5:
    # If the current process matches the ball's owner (count % 2)
    if rank == count % 2:
        count += 1  # Increment the counter
        # Send the ball (counter value) to the other rank
        comm.send(count, dest=(rank + 1) % 2)
        print("Rank", rank, "counts", count, "and sends the ball to rank", (rank + 1) % 2)
    # If the current process does not own the ball
    elif rank == (count + 1) % 2:
        # Receive the ball (counter value) from the other rank
        count = comm.recv(source=(rank + 1) % 2)
        print("Rank", rank, "received the ball with count", count, "from rank", (rank + 1) % 2)
