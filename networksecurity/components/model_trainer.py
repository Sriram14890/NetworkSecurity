import os
import sys
import mlflow
import dagshub

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    AdaBoostClassifier
)

from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import (
    ModelTrainerArtifact,
    DataTransformationArtifact
)

from networksecurity.utils.main_utils.utils import (
    save_object,
    load_object,
    load_numpy_array_data,
    evaluate_models
)

from networksecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score
)
from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from networksecurity.constant.training_pipeline import (
    MODEL_FILE_PATH,
    PREPROCESSOR_FILE_PATH
)

# Initialize MLflow (DagsHub)
dagshub.init(
    repo_owner="Sriram14890",
    repo_name="NetworkSecurity",
    mlflow=True
)


class ModelTrainer:
    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, model, metric):
        with mlflow.start_run():
            mlflow.log_metric("f1_score", metric.f1_score)
            mlflow.log_metric("precision", metric.precision_score)
            mlflow.log_metric("recall", metric.recall_score)
            mlflow.sklearn.log_model(model, "model")

    def train_and_select_model(self, X_train, y_train, X_test, y_test):
        models = {
            "RandomForest": RandomForestClassifier(),
            "DecisionTree": DecisionTreeClassifier(),
            "GradientBoosting": GradientBoostingClassifier(),
            "LogisticRegression": LogisticRegression(max_iter=1000),
            "AdaBoost": AdaBoostClassifier(),
        }

        params = {
            "DecisionTree": {
                "criterion": ["gini", "entropy"]
            },
            "RandomForest": {
                "n_estimators": [50, 100, 200]
            },
            "GradientBoosting": {
                "learning_rate": [0.01, 0.1],
                "n_estimators": [100, 200]
            },
            "LogisticRegression": {},
            "AdaBoost": {
                "n_estimators": [50, 100]
            }
        }

        model_report = evaluate_models(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            models=models,
            param=params
        )

        best_model_name = max(model_report, key=model_report.get)
        best_model = models[best_model_name]

        logging.info(f"Best model selected: {best_model_name}")
        return best_model

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            # Load transformed data
            train_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_train_file_path
            )
            test_arr = load_numpy_array_data(
                self.data_transformation_artifact.transformed_test_file_path
            )

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            # Train & select best model
            best_model = self.train_and_select_model(
                X_train, y_train, X_test, y_test
            )

            # Metrics
            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)

            train_metric = get_classification_score(y_train, y_train_pred)
            test_metric = get_classification_score(y_test, y_test_pred)

            # MLflow tracking
            self.track_mlflow(best_model, train_metric)
            self.track_mlflow(best_model, test_metric)

            # Load preprocessor
            preprocessor = load_object(
                self.data_transformation_artifact.transformed_object_file_path
            )

            # Ensure final_models directory
            os.makedirs(os.path.dirname(MODEL_FILE_PATH), exist_ok=True)

            # Save model + preprocessor
            save_object(MODEL_FILE_PATH, best_model)
            save_object(PREPROCESSOR_FILE_PATH, preprocessor)

            # Save combined NetworkModel
            network_model = NetworkModel(
                preprocessor=preprocessor,
                model=best_model
            )
            save_object(
                self.model_trainer_config.trained_model_file_path,
                network_model
            )

            logging.info(
                f"Model trained with {best_model.n_features_in_} features"
            )

            return ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=train_metric,
                test_metric_artifact=test_metric
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)
