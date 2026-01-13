
# communicate function is used to communicate between processors in a 2D grid

# from_list is a list of 8 elements that contains a list to be received from the neighbors
# to_list is a list of 8 elements that contains a list to be sent to the neighbors


## tags used for the communication:
    # 11: above
    # 12: below
    # 13: left
    # 14: right
    # 15: above right
    # 16: below right
    # 17: above left
    # 18: below left


# receive order:
    # from below : 0
    # from above : 1
    # from right : 2
    # from left : 3
    # from below left : 4
    # from above left : 5
    # from below right: 6
    # from above right : 7

# odd processors send first then receive. 

def communicate(from_list, to_list, rank, sqrt_p, comm):
    
    # if there is only one processor, no communication is needed
    world_size = comm.Get_size()
    if world_size <= 2:
        return from_list
    
    # row-wise communication

    # mark the odd and even rows
    odd1 = ((rank - 1) // sqrt_p) % 2 == 0

    # the most top row
    if rank <= sqrt_p: 
        if(odd1):
            # below
            comm.send(to_list[0], dest=rank+sqrt_p, tag=12) 
            # from below
            from_list[0] = comm.recv(source=rank+sqrt_p, tag=11)  
        else:
            # from below
            from_list[0] = comm.recv(source=rank+sqrt_p, tag=11) 
            # below 
            comm.send(to_list[0], dest=rank+sqrt_p, tag=12)  

    # the most bottom row
    elif rank > sqrt_p*(sqrt_p-1):  
        if(odd1):
            # above
            comm.send(to_list[1], dest=rank-sqrt_p, tag = 11)   
            # from above
            from_list[1] = comm.recv(source=rank-sqrt_p, tag = 12)   
        else:
            # from above
            from_list[1] = comm.recv(source=rank-sqrt_p, tag = 12) 
            # above  
            comm.send(to_list[1], dest=rank-sqrt_p, tag = 11)   

    # intermediate rows        
    else:  
        if(odd1):
            # above
            comm.send(to_list[1], dest=rank-sqrt_p, tag=11)
            # below  
            comm.send(to_list[0], dest=rank+sqrt_p, tag=12)  
            # from below
            from_list[0] = comm.recv(source=rank+sqrt_p, tag=11)  
            # from above
            from_list[1] = comm.recv(source=rank-sqrt_p, tag=12)   
        else:
            # from below
            from_list[0] = comm.recv(source=rank+sqrt_p, tag=11)  
            # from above
            from_list[1] = comm.recv(source=rank-sqrt_p, tag=12)   
            # above
            comm.send(to_list[1], dest=rank-sqrt_p, tag=11)   
            # below
            comm.send(to_list[0], dest=rank+sqrt_p, tag=12)  

    # column-wise communication

    # mark the odd and even columns
    odd2 = (rank%2 == 1)

    # the most left column
    if(rank%sqrt_p==1):  
        if(odd2):
            # right
            comm.send(to_list[2], dest=rank+1, tag=14) 
            # from right
            from_list[2] = comm.recv(source=rank+1, tag=13) 
        else:
            # from right
            from_list[2] = comm.recv(source=rank+1, tag=13)
            # right
            comm.send(to_list[2], dest=rank+1, tag=14) 

    # the most right column
    elif(rank%sqrt_p==0):   
        if(odd2):
            # left
            comm.send(to_list[3], dest=rank-1, tag=13) 
            # from left
            from_list[3] = comm.recv(source=rank-1, tag=14) 
        else:
            # from left
            from_list[3] = comm.recv(source=rank-1, tag=14) 
            # left
            comm.send(to_list[3], dest=rank-1, tag=13) 

    # intermediate columns        
    else:
        if(odd2):
            # left
            comm.send(to_list[3], dest=rank-1, tag=13) 
            # right	
            comm.send(to_list[2], dest=rank+1, tag=14) 
            # from right
            from_list[2] = comm.recv(source=rank+1, tag=13) 
            # from left	
            from_list[3] = comm.recv(source=rank-1, tag=14) 	
        else:
            # from right
            from_list[2] = comm.recv(source=rank+1, tag=13) 
            # from left	
            from_list[3] = comm.recv(source=rank-1, tag=14) 
            # left
            comm.send(to_list[3], dest=rank-1, tag=13)
            # right	
            comm.send(to_list[2], dest=rank+1, tag=14) 
    
    # diagonal-wise communication

    # use the same odd and even row marking for the row-wise communication and diagonal-wise communication
    odd3 = odd1 

    # no sending
    if(rank == 1): 
        pass

    # no sending
    elif(rank == sqrt_p*sqrt_p): 
        pass

    # first row or last column (don't send to right above) 
    elif(rank <= sqrt_p or rank%sqrt_p==0): 
        if(odd3):
            # below left	
            comm.send(to_list[4], dest=rank+sqrt_p-1, tag=18) 
            # from below left
            from_list[4] = comm.recv(source=rank+sqrt_p-1, tag=15) 
        else:
            # from below left
            from_list[4] = comm.recv(source=rank+sqrt_p-1, tag=15) 
            # below left	
            comm.send(to_list[4], dest=rank+sqrt_p-1, tag=18) 

    # last row or first column
    elif(rank > sqrt_p*(sqrt_p-1) or rank%sqrt_p==1):  
        if(odd3):
            # above right
            comm.send(to_list[7], dest=rank-sqrt_p+1, tag=15)  
            # from above right
            from_list[7] = comm.recv(source=rank-sqrt_p+1, tag=18)  
        else:
            # from above right
            from_list[7] = comm.recv(source=rank-sqrt_p+1, tag=18) 
            # above right 
            comm.send(to_list[7], dest=rank-sqrt_p+1, tag=15)  
    else:
        if(odd3):
            # above right
            comm.send(to_list[7], dest=rank-sqrt_p+1, tag=15) 
            # below left	 
            comm.send(to_list[4], dest=rank+sqrt_p-1, tag=18) 
            # from below left
            from_list[4] = comm.recv(source=rank+sqrt_p-1, tag=15)
            # from above right
            from_list[7] = comm.recv(source=rank-sqrt_p+1, tag=18)  
        else:
            # from below left
            from_list[4] = comm.recv(source=rank+sqrt_p-1, tag=15) 
            # from above right
            from_list[7] = comm.recv(source=rank-sqrt_p+1, tag=18)  
            # above right
            comm.send(to_list[7], dest=rank-sqrt_p+1, tag=15) 
            # below left	
            comm.send(to_list[4], dest=rank+sqrt_p-1, tag=18) 
            

    # no sending 
    if(rank == sqrt_p): 
        pass
    # no sending 
    elif(rank == sqrt_p*(sqrt_p-1) + 1): 
        pass

    # first row or first column (don't send to left above)
    elif(rank <= sqrt_p or rank%sqrt_p==1): 
        if(odd3):
            #below right
            comm.send(to_list[6], dest=rank+sqrt_p+1, tag=16)  
            # from below right
            from_list[6] = comm.recv(source=rank+sqrt_p+1, tag=17)  
        else:
            # from below right
            from_list[6] = comm.recv(source=rank+sqrt_p+1, tag=17) 
            #below right 
            comm.send(to_list[6], dest=rank+sqrt_p+1, tag=16)  

    # last row or last column
    elif(rank > sqrt_p*(sqrt_p-1) or rank%sqrt_p==0):  
        if(odd3):
            # above left
            comm.send(to_list[5], dest=rank-sqrt_p-1, tag = 17) 
            # from above left
            from_list[5] = comm.recv(source=rank-sqrt_p-1, tag = 16) 
        else:
            # from above left
            from_list[5] = comm.recv(source=rank-sqrt_p-1, tag = 16) 
            # above left
            comm.send(to_list[5], dest=rank-sqrt_p-1, tag = 17) 
    else:
        if(odd3):
            #below right
            comm.send(to_list[6], dest=rank+sqrt_p+1, tag=16)  
            # above left
            comm.send(to_list[5], dest=rank-sqrt_p-1, tag = 17) 
            # from above left
            from_list[5] = comm.recv(source=rank-sqrt_p-1, tag = 16) 
            # from below right
            from_list[6] = comm.recv(source=rank+sqrt_p+1, tag=17) 
        else:
            # from above left
            from_list[5] = comm.recv(source=rank-sqrt_p-1, tag = 16) 
            # from below right
            from_list[6] = comm.recv(source=rank+sqrt_p+1, tag=17)  
            #below right
            comm.send(to_list[6], dest=rank+sqrt_p+1, tag=16)  
            # above left
            comm.send(to_list[5], dest=rank-sqrt_p-1, tag = 17) 

    # return the received elements
    return from_list