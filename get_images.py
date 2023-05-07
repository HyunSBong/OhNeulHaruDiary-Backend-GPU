import shutil
import glob
import itertools

data_root_path = 'data/다양한_형태의_한글문자_OCR/**/*.jpg'
file_list = glob.glob(data_root_path, recursive=True)
files = [file for file in file_list if file.endswith('.jpg')]

save_root_path = 'data/'
# copy images from dataset directory to current directory
for path in files:
    shutil.copy(path, save_root_path)

# separate dataset : train, validation, test
obj_list = ['train', 'test', 'validation']
for obj in obj_list:
    with open(f'data/gt_{obj}.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        try:
            file_path = line.split('.jpg')[0]
            file_name = file_path.split('/')[1] + '.jpg'
            res = shutil.move(save_root_path+file_name, f'data/{obj}/')
        except:
            continue