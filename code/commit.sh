#!/bin/bash
#exec 3>&1 4>&2
#trap 'exec 2>&4 1>&3' 0 1 2 3
#exec 1>log.out 2>&1
exec > log.out 2>&1
set -x

mensaje=$1
echo $mensaje

cd /home/cristian/Descargas/Universidad/2021-2/Análisis_numérico/PROYECTO/Código/Numerical_Analysis && git add .
cd /home/cristian/Descargas/Universidad/2021-2/Análisis_numérico/PROYECTO/Código/Numerical_Analysis && git commit -m "$mensaje"
cd /home/cristian/Descargas/Universidad/2021-2/Análisis_numérico/PROYECTO/Código/Numerical_Analysis && git pull
cd /home/cristian/Descargas/Universidad/2021-2/Análisis_numérico/PROYECTO/Código/Numerical_Analysis && git push
