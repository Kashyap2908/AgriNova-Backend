import os
import joblib

from ml.utils import get_model_path, load_json
from ml.market_trainer import train_market_model
from ml.market_predictor import MarketPredictor

class MarketModelManager:
    """
    Singleton Manager for the Market Price Prediction model.
    Enforces training policy:
    - Retrains ONLY when new historical market data is added or model file missing.
    - Maintains single trained model file.
    - Loads model into memory for fast prediction inference.
    """
    _instance = None
    _model = None
    _metadata = None
    _predictor = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.check_and_retrain(force=False)

    def check_and_retrain(self, force: bool = False):
        """
        Enforces training policy:
        - If model pkl file is missing -> Train fresh model
        - If force is True (e.g. new data added to MarketCache) -> Retrain
        - Otherwise -> Load existing model into memory
        """
        if self._predictor is not None and not force:
            return

        model_path = get_model_path('market_prediction_model.pkl')
        metadata_path = get_model_path('market_model_metadata.json')

        missing_file = not (os.path.exists(model_path) and os.path.exists(metadata_path))
        should_retrain = force or missing_file

        if should_retrain:
            if missing_file:
                print("[MarketModelManager] Missing model file. Training fresh Market Prediction model...")
            else:
                print("[MarketModelManager] New historical market data detected. Retraining Market Model...")

            self._model, self._metadata = train_market_model()
        else:
            try:
                self._model = joblib.load(model_path)
                self._metadata = load_json(metadata_path)
            except Exception as e:
                print(f"[MarketModelManager] Failed loading model file: {e}. Retraining...")
                self._model, self._metadata = train_market_model()

        self._predictor = MarketPredictor(model=self._model, metadata=self._metadata)
        print(f"[MarketModelManager] Loaded Market Prediction model into memory.")

    def get_predictor(self) -> MarketPredictor:
        if self._predictor is None:
            self.check_and_retrain()
        return self._predictor

    def get_metadata(self) -> dict:
        if self._metadata is None:
            self._metadata = load_json(get_model_path('market_model_metadata.json'))
        return self._metadata
