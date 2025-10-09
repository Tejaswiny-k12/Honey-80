import unittest
from src.models.train import train_model
from src.models.predict import predict

class TestModels(unittest.TestCase):

    def setUp(self):
        self.sample_data = {
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6],
            'label': [0, 1, 0]
        }
        self.model = train_model(self.sample_data)

    def test_model_training(self):
        self.assertIsNotNone(self.model)
        self.assertTrue(hasattr(self.model, 'predict'))

    def test_model_prediction(self):
        predictions = predict(self.model, [[1, 4], [2, 5], [3, 6]])
        self.assertEqual(len(predictions), 3)
        self.assertTrue(all(isinstance(pred, (int, float)) for pred in predictions))

if __name__ == '__main__':
    unittest.main()