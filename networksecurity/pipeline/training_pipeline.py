import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    TrainingPipelineConfig
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact
)

class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config=TrainingPipelineConfig()

    def start_data_ingestion(self):
        try:
            self.data_ingestion_config=DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start Data Ingestion.")
            data_ingestion=DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info("Data Ingestion Completed.")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact)->DataValidationArtifact:
        try:
            self.data_validation_config=DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Data Validation Started.")
            data_validation=DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                           data_validation_config=self.data_validation_config)
            data_validation_artifact=data_validation.initiate_data_validation()
            logging.info("Data Validation Completed.")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact)->DataTransformationArtifact:
        try:
            self.data_transformation_config=DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Data Transformation Started.")
            data_transformation=DataTransformation(data_validation_artifact=data_validation_artifact,
                                                   data_transformation_config=self.data_transformation_config)
            data_transformation_artifact=data_transformation.initiate_data_transformation()
            logging.info("Data Transformation Completed.")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config=ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Model Trainer Started.")
            model_trainer=ModelTrainer(model_trainer_config=self.model_trainer_config,
                                       data_transformation_artifact=data_transformation_artifact)
            model_trainer_artifact=model_trainer.initiate_model_trainer()
            logging.info("Model Trainer Completed.")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def run_pipeline(self):
        try:
            data_ingestion_artifact=self.start_data_ingestion()
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact=self.start_data_transformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.start_model_trainer(data_transformation_artifact=data_transformation_artifact)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    try:
        logging.info("Training pipeline started")
        pipeline = TrainingPipeline()
        pipeline.run_pipeline()
        logging.info("Training pipeline completed successfully")

    except NetworkSecurityException as e:
        logging.error(e)
        raise e

    except Exception as e:
        logging.error(e)
        raise NetworkSecurityException(e, sys)

        
