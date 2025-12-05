#bin/bash
eval "$(conda shell.bash hook)"

export EVOICE_ENV=prod
export CUDA_VISIBLE_DEVICES=2,3
conda activate evoice && nohup gunicorn --workers 4 --bind 0.0.0.0:8210 --preload  rest:app  > rest.log 2>&1 &

echo "The rest server is running..."


gunicorn  --worker-class eventlet -w 2 \
         -k uvicorn.workers.UvicornWorker \
         --bind 0.0.0.0:8210 \
         --timeout 120 \
         --access-logfile - \
         --error-logfile - \
         --log-level warning \
         --worker-connections 1000 \
 rest:app