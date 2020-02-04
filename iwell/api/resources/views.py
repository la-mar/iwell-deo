from flask import Blueprint
from flask_restful import Api


import api.resources as r

blueprint = Blueprint("root", __name__)
api = Api(blueprint)

api.add_resource(r.HealthCheck, "/health")
api.add_resource(r.JobCount, "/jobs")
api.add_resource(r.RunJob, "/<endpoint>")
api.add_resource(r.DescribeEndpoint, "/<endpoint>/describe")
api.add_resource(r.ListResources, "/endpoints")
api.add_resource(r.DescribeEndpoints, "/endpoints/describe")
