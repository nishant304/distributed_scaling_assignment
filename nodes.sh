#!/bin/bash 

j=0
k=1
m=$1 

echo $1



directory=`pwd` 

       executable="greencompue.py";
       nodes=( "tile-1-0")
       for node in "${nodes[@]}"
       do
       echo "Booting node" $node
       nohup ssh $2 DISPLAY=:0  xterm -e bash -c "'python  $directory/$executable '" 2>&1 &
             
       done
               
         


       executable="Frontend.py";
       nodes=( "tile-2-0" "tile-3-0" "tile-4-0")
       for node in "${nodes[@]}"
       do
       echo "Booting node" $node
       nohup ssh $node DISPLAY=:0  xterm -e bash -c "'python  $directory/$executable --ip $2 --res_port $3'" >nohup11.out  2>&1 &
    
       done

        executable="loadbalancer.py";
        nodes=( "tile-5-0" )
        for node in "${nodes[@]}"
        do
        echo "Booting node" $node
        nohup ssh $node DISPLAY=:0  xterm -e bash -c "'python  $directory/$executable '" 2>&1 &
        done





executable="client.py"


for i in $(seq 1 $1)
    do
       node="tile-"$j"-"$k
       nohup  ssh $node DISPLAY=:0  xterm -e bash -c "'python  $directory/$executable '" 2>&1  &
        
            ((j=j+1))
    if [ "$j" == "6" ]  
    then
            j=0
                ((k=k+1))
               fi
                                     
done




