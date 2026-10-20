import logging

from etl.extract import extract
from etl.load import load
from etl.transform import transform

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    grezzi = extract()
    puliti = transform(grezzi)
    load(puliti)
    logging.info("Pipeline completata")


if __name__ == "__main__":
    main()
