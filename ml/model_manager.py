import os
import time
import joblib
from ml.utils import (
    get_dataset_path,
    get_model_path,
    get_file_mtime,
    load_json
)
from ml.trainer import train_all_models
from ml.predictor import Predictor

class ModelManager:
    """
    Singleton Model Manager that loads ML models into memory once, reuses them,
    and enforces the automatic 3-case retraining policy.
    """
    _instance = None
    
    _crop_model = None
    _yield_model = None
    _label_encoder = None
    _feature_encoder = None
    _predictor = None
    _metadata = None
    
    RETRAIN_DAYS = 30
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.check_and_load_or_retrain()

    def check_and_load_or_retrain(self, force_retrain: bool = False):
        """
        Enforces Model Training Policy:
        - Case 1: If .pkl files do not exist -> Automatically train
        - Case 2: If dataset was modified after model creation -> Retrain
        - Case 3: If models are older than 30 days -> Retrain
        - Otherwise -> Load existing .pkl models
        """
        crop_model_path = get_model_path('crop_model.pkl')
        yield_model_path = get_model_path('yield_model.pkl')
        label_enc_path = get_model_path('label_encoder.pkl')
        feat_enc_path = get_model_path('feature_encoder.pkl')
        metadata_path = get_model_path('model_metadata.json')

        dataset_path = get_dataset_path('Crop_recommendation_extended.csv')
        
        # Check Case 1: Missing PKL files
        missing_files = not (
            os.path.exists(crop_model_path) and
            os.path.exists(yield_model_path) and
            os.path.exists(label_enc_path) and
            os.path.exists(feat_enc_path) and
            os.path.exists(metadata_path)
        )

        should_retrain = force_retrain or missing_files
        
        if not should_retrain:
            metadata = load_json(metadata_path)
            training_timestamp = metadata.get('training_timestamp', 0)
            
            # Check Case 2: Dataset modified after model creation
            dataset_mtime = get_file_mtime(dataset_path)
            if dataset_mtime > training_timestamp:
                print("[ModelManager] Case 2 Triggered: Dataset was modified since last training. Retraining...")
                should_retrain = True
            
            # Check Case 3: Models older than retraining period (30 days)
            age_seconds = time.time() - training_timestamp
            retrain_seconds = self.RETRAIN_DAYS * 86400
            if age_seconds > retrain_seconds:
                print("[ModelManager] Case 3 Triggered: Models older than 30 days. Retraining...")
                should_retrain = True

        if should_retrain:
            if missing_files:
                print("[ModelManager] Case 1 Triggered: Missing model files. Training fresh models...")
            train_all_models()

        # Load models into memory
        self._crop_model = joblib.load(crop_model_path)
        self._yield_model = joblib.load(yield_model_path)
        self._label_encoder = joblib.load(label_enc_path)
        self._feature_encoder = joblib.load(feat_enc_path)
        self._metadata = load_json(metadata_path)
        
        self._predictor = Predictor(
            crop_model=self._crop_model,
            yield_model=self._yield_model,
            label_encoder=self._label_encoder,
            feature_encoder=self._feature_encoder
        )
        print(f"[ModelManager] Models successfully loaded in memory. (Accuracy: {self._metadata.get('crop_classifier_accuracy') * 100:.2f}%)")

    def get_predictor(self) -> Predictor:
        if self._predictor is None:
            self.check_and_load_or_retrain()
        return self._predictor

    def get_metadata(self) -> dict:
        if self._metadata is None:
            self._metadata = load_json(get_model_path('model_metadata.json'))
        return self._metadata
