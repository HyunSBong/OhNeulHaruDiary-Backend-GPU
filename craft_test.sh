cd craft
python craft_test.py --trained_model="./weights/craft/craft_mlt_25k.pth" --refiner_model="./weights/craft/craft_refiner_CTW1500.pth" --test_folder="./image_testset/" --cuda=False --mps=True