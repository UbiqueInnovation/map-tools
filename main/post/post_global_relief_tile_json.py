import json
import logging
from datetime import timedelta
from io import BytesIO

from commons import R2Client, BucketOutput

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2 = R2Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    style = "light"
    max_zoom = 10

    for bucket in [r2.post_playground, r2.post_playground_int]:
        with BytesIO() as file:
            tile_json = dict(
                tilejson="3.0.0",
                name="global-relief",
                version="1.0.0",
                format="jpeg",
                metadata=dict(crs="EPSG:4326"),
                tiles=[
                    "https://post-playground-dev.openmobilemaps.io/v1/background/global-relief/light/4326/{z}/{x}/{y}.jpg"
                ],
                minzoom=0,
                maxzoom=max_zoom,
            )
            file.write(json.dumps(tile_json).encode("UTF-8"))
            file.flush()
            file.seek(0)
            BucketOutput(
                bucket=bucket,
                cache_control=cache_control_test,
            ).upload(file, f"v1/background/global-relief/{style}/tiles.json")
