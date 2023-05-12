python3 ./create_lmdb_dataset.py \
    --inputPath ./data \
    --gtFile ./data/gt_train_500.txt \
    --outputPath ./data_lmdb/train

python3 ./create_lmdb_dataset.py \
    --inputPath ./data \
    --gtFile ./data/gt_validation_100.txt \
    --outputPath ./data_lmdb/validation

python3 ./create_lmdb_dataset.py \
    --inputPath ./data \
    --gtFile ./data/gt_test_50.txt \
    --outputPath ./data_lmdb/test
