#!/bin/bash

# configuration
path="spc05/"
projName="bowl_shapenet/"

bulletFile="Data/bowlBullet/"
metaFile="Data/Meta/bowl_output.txt"

# folder set up
mkdir "${path}${projName}out_vdb/"
mkdir "${path}${projName}csv/"

# epoch Looping
for i in `seq 1 `
do
  # data obj looping
  while IFS= read -r objName
  do
    echo "$objName"
    
    csv_file="${path}${projName}/csv/$objName-$i.csv"
    exec_name="${path}${projName}/$objName-$i/obj_"
    out_name="${path}${projName}/out_vdb/$objName-$i"

    if test -f "$out_name.obj" ; then
        echo "$out_name.obj exists."
    else
        mkdir "${path}_out_squirrel/squirrel-$i/"
        if test -f "$csv_file" ; then
            echo "$csv_file exists."
        else
            echo "$csv_file not exists."
            # Create CSV  material(default);maxcrack(10);INITIAL_BEM(1);Facturable(2 means Twice,and 1 means only fracture once);
            echo "collisionObject2;target;0;0;0;0;0;0;0;0;0;0;0;0;0;1; 0.1;0.01;3.10E+09;0.327;1000;7.60E+05;1.00E+03;6.0;1500;0;default;5;1;2" > "$csv_file"
            # 球状随机采样 计算Vector
            M_PI=3.1415926
            rand1=( $(awk -v seed="${RANDOM}" 'BEGIN{srand(seed); print(rand())}') )
            rand2=( $(awk -v seed="${RANDOM}" 'BEGIN{srand(seed); print(rand())}') )
            theta=( $(awk -v random="${rand1}" -v pi="${M_PI}" 'BEGIN{theta=2*pi*random; print(theta)}') )
            phi=( $(awk -v random="${rand2}" 'BEGIN{tar=1-2*random;phi=atan2(sqrt(1-tar*tar), tar); print(phi)}') )
            x=( $(awk -v phi="${phi}" -v theta="${theta}" 'BEGIN{x=sin(phi)*cos(theta); print(x)}') )
            y=( $(awk -v phi="${phi}" -v theta="${theta}" 'BEGIN{y=sin(phi)*sin(theta); print(y)}') )
            z=( $(awk -v phi="${phi}" 'BEGIN{z=cos(phi); print(z)}') )
            radius=3
            velocity=( $(awk -v seed="${RANDOM}" 'BEGIN{srand(seed); v=25 + rand() * 75; print(v)}') )
            px=( $(awk -v x="${x}" -v r="${radius}" 'BEGIN{px=x*r; print(px)}') )
            py=( $(awk -v y="${y}" -v r="${radius}" 'BEGIN{py=y*r; print(py)}') )
            pz=( $(awk -v z="${z}" -v r="${radius}" 'BEGIN{pz=z*r; print(pz)}') )
            vx=( $(awk -v x="${x}" -v v="${velocity}" 'BEGIN{vx=-x*v; print(vx)}') )
            vy=( $(awk -v y="${y}" -v v="${velocity}" 'BEGIN{vy=-y*v; print(vy)}') )
            vz=( $(awk -v z="${z}" -v v="${velocity}" 'BEGIN{vz=-z*v; print(vz)}') )
            # 读取模板文件内容，并将随机角度插入
            echo "collisionObject1;sphere1;$px;$py;$pz;0;0;0;$vx;$vy;$vz;0;0;0;0;1; 0.6;0.1 ;3.10E+09;0.327;8900;7.60E+99;1.00E+03;3.0;  60;0;default;-1;1" >> "$csv_file"
        fi
        ../build/FractureRB $bulletFile/$objName.bullet $csv_file -o $exec_name -i 1e5 -f 1e7 -s 2 -n 400
        ../build/FractureRB_vis -i $exec_name --outVDBFile $out_name -n 1000 -o _hi -q 0.001 --vis-obj target --sdf
    fi

  done < "$metaFile"
done