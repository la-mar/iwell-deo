from typing import Tuple, Dict

from flask_restful import Resource


class HealthCheck(Resource):
    def get(self) -> Tuple[Dict, int]:
        return {"status": "ok"}, 200
