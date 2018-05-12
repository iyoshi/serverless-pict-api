import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            return int(o)

        return super(DecimalEncoder, self).default(o)
