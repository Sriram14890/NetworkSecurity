from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
import sys
if __name__=='__main__':
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestion_config=DataIngestionConfig(trainingpipelineconfig)
        dataingestion=DataIngestion(dataingestion_config)
        logging.info("Intiated the Data Ingestion")
        dataingestionnartifact=dataingestion.initiate_data_ingestion()
        logging.info("Data Ingestion Completed")
        print(dataingestionnartifact)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
        