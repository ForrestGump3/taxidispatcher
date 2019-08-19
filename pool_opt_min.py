from cvxopt.glpk import ilp
import numpy as np
from cvxopt import matrix

n=100
max_iter=5

arr = np.zeros((n, n*n)) 
for i in range(0,n):
    for j in range(0,n): 
        arr[i][n*i+j]=1.0 #  column with '1' only
        arr[i][n*j+i]=1.0 #  columns with single '1'
a=matrix(arr, tc='d') 
g=matrix([ [0 for x in range(n*n)] ], tc='d')
b=matrix(1*np.ones(n))
h=matrix(0*np.ones(1))
I=set(range(n*n))
B=set(range(n*n))

numb_cust=n # maybe *2? twice as many customers than there are stops; 
max_loss=1.01 # I don't care if it takes 2x longer with pool

# cost=np.zeros((n,n)) # distances
# # calculate distances
# for i in range(0,n):
#     for j in range(i,n):
#         cost[j][i]=j-i # simplification of distance - stop9 is closer to stop7 than to stop1
#         cost[i][j]=cost[j][i] 
cost = [[np.random.randint(1,40) for i in range(n)] for j in range(n)] 
#print (cost)
f= open("c:/Users/dell/Documents/TAXI-routing/Python/pool_out.txt","w+")

for iter in range(max_iter):
    demand = [[np.random.randint(0,n) for i in range(2)] for j in range(numb_cust)]
    # now we have to remove incidental from=to generated by 'random'
    length = numb_cust # *2: let's have twice as much customers than there are stops; 
    i=0
    while True:
        if(demand[i][0]==demand[i][1]): 
            demand.pop(i)
            length=length-1
        i=i+1
        if (i>=length): break

    numb_cust=length
    #print (demand)

    pool = []
    c=matrix([ [n*n for x in range(n*n)] ], tc='d') # filling with values much bigger than costs, n*n is quite OK

    for custA in range(numb_cust):
        for custB in range(numb_cust):
            if (custA != custB):
                plan1=False
                plan2=False
                cost1 = cost[demand[custA][0]][demand[custB][0]] + cost[demand[custB][0]][demand[custA][1]] + cost[demand[custA][1]][demand[custB][1]]
                cost2 = cost[demand[custA][0]][demand[custB][0]] + cost[demand[custB][0]][demand[custB][1]] + cost[demand[custB][1]][demand[custA][1]]
                if (cost[demand[custB][0]][demand[custA][1]] + cost[demand[custA][1]][demand[custB][1]]
                    < cost[demand[custB][0]][demand[custB][1]]*max_loss and  # cust B does not lose much with it
                    cost[demand[custA][0]][demand[custB][0]] + cost[demand[custB][0]][demand[custA][1]]
                    < cost[demand[custA][0]][demand[custA][1]]*max_loss # cust A does not lose much with it either
                    ): plan1 = True
                if (cost2 < cost[demand[custA][0]][demand[custA][1]]*max_loss ): #// cust A does not lose much with it, B never loses in this scenario
                    plan2 = True
                if (plan1 or plan2): 
                    if (cost1<cost2): # plan1 is better
                        # print("Customer %d takes %d, customer %d ends the whole trip, total cost: %d (with(out) pool - customer %d: %d(%d), customer %d: %d(%d))" %
                        #         (custA, custB, custB, cost1,
                        #         custA, cost[demand[custA][0]][demand[custB][0]] + cost[demand[custB][0]][demand[custA][1]], cost[demand[custA][0]][demand[custA][1]],
                        #         custB, cost[demand[custB][0]][demand[custA][1]] + cost[demand[custA][1]][demand[custB][1]], cost[demand[custB][0]][demand[custB][1]]))
                        pool.append((custA, custB, cost1))
                        c[custA*n + custB]=cost1
                    else:
                        # print("Customer %d takes %d, customer %d ends the whole trip, total cost: %d (with(out) pool - customer %d: %d(%d), customer %d: %d(%d))" %
                        # (custA, custB, custA, cost2,
                        # custA, cost2, cost[demand[custA][0]][demand[custA][1]],
                        # custB, cost[demand[custB][0]][demand[custB][1]], cost[demand[custB][0]][demand[custB][1]]))
                        pool.append((custA, custB, cost2))
                        c[custA*n + custB]=cost2

    pool.sort(key=lambda x:x[2])
    array = np.array(pool)
    #print (array)
    nmb = len(array)
    i=1
    total_cost = array[0][2] # the first element will always be in plan
    numb_plans=1;
    while True:
        j=0 # check if one of passengers were mentioned earlier
        while True:
            if (array[j][0]!=-1 and #  not marked as dropped
                (array[i][0]==array[j][0] or array[i][1]==array[j][1] or
                array[i][0]==array[j][1] or array[i][1]==array[j][0])): 
                array[i][0]=-1
                break
            else: j=j+1
            if (j >= i): 
                total_cost = total_cost + array[i][2]
                numb_plans=numb_plans+1
                break # not found
        i = i+1
        if (i >= nmb): break

    #print("Plans:")
    numb_of_trips=0
    for i in range(nmb):
        if (array[i][0]!=-1): 
            #print(array[i])
            numb_of_trips = numb_of_trips +1

    #print ("Routes: %d, total cost: %d" % (numb_of_trips, total_cost))
    print ("====================")
    (status,x)=ilp(c,g.T,h,a,b,I,B)
    #print(sum(c.T*x))
    tot_cost=0
    numb_var = 0
    for i in range(n*n):
        if (x[i]==1 and c[i]<n*n):
            #print ("%d %d (%d)" % (int(i/n), i % n, c[i]))
            tot_cost = tot_cost + c[i]
            numb_var = numb_var +1
    #print ("Routes: %d, total cost: %d" % (numb_var, tot_cost))
    if (numb_var == numb_of_trips): # it is easier to compare 
        f.write("%d; %d; %5.0f\n" % (total_cost, tot_cost, 100* (total_cost - tot_cost)/tot_cost) )

f.close() 