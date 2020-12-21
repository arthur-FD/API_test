import logging

import azure.functions as func
import logging
import os

import azure.functions as func
import pandas as pd
import snowflake.connector
import yaml
import pathlib
from functest.utils.config_loader import ConfigLoader

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')
    with open(pathlib.Path(__file__).parent / "conf/parameter.yml", "r") as file:
        parameters = yaml.load(file, Loader=ConfigLoader)
    with open(pathlib.Path(__file__).parent / "conf/funct_query.sql", "r") as file:
        core_query = file.read()

    conn = snowflake.connector.connect(
        user=os.environ["USER_SF"],
        password=os.environ["PSW_SF"],
        account=os.environ["ACCOUNT_SF"],
        **parameters["snowflake_config"]
    )    
    
    cur = conn.cursor()
    cur.execute(core_query)
    core_data = cur.fetch_pandas_all()
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')
    req_params = {param_name: get_param(req, param_name) for param_name in ["OEM", "value2"]}
    if name:
        # return func.HttpResponse(body=str(req_params))
        return func.HttpResponse(body=core_data.to_json(date_format="iso", orient="split"))
    else:
        return func.HttpResponse(
             f"This HTTP triggered function executed successfully. {pathlib.Path(__file__).parent}",
             status_code=200
        )

def get_param(req, param_name, default_value=None):
    param_value = req.params.get(param_name)
    if not param_value:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            param_value = req_body.get(param_name, default_value)
    return param_value