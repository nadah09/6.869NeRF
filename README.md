# 6.869NeRF
Final project implementation of NeRF for 6.869: Advanced in Computer Vision

## Installing dependencies
```
pip3 install -r requirements.txt
cd torchsearchsorted
pip3 install .
cd ..
pip3 install tensorboard -U
```

For downloading data:
```
bash download_example_data.sh
```

## Running
```
python3 run_nerf.py --config config_fern.txt
```
