"""
TCM Formula Recommendation Configuration
"""

DATA_CONFIG = {
    'train_ratio': 0.6,
    'val_ratio': 0.2,
    'test_ratio': 0.2,
    'augment_factor': 5,
    'random_seed': 42,
}

MODEL_CONFIG = {
    'embed_dim': 256,
    'hidden_dim': 512,
    'label_dim': 128,
    'num_heads': 8,
    'dropout': 0.3,
}

TRAIN_CONFIG = {
    'batch_size': 64,
    'learning_rate': 0.001,
    'weight_decay': 0.05,
    'epochs': 500,
    'patience': 100,
    'alpha_fn': 0.85,
    'alpha_fp': 0.15,
}

LOSS_CONFIG = {
    'alpha_fn': 0.85,
    'alpha_fp': 0.15,
    'count_weight': 0.1,
    'label_smoothing': 0.0,
}

PATHS = {
    'data_dir': 'data',
    'checkpoint_dir': 'checkpoints',
    'log_dir': 'logs',
}
