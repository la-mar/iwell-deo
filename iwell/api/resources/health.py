from typing import Tuple

from flask_restful import Resource


class HealthCheck(Resource):
    def get(self) -> Tuple[str, int]:
        return "ok", 200
