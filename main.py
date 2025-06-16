import argparse
import logging
import re
import datetime
import sys
from typing import Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize_phone_number(phone_number: str) -> Optional[str]:
    """
    Normalizes a phone number to the E.164 format (+[country code][number]).

    Args:
        phone_number: The phone number to normalize.

    Returns:
        The normalized phone number, or None if normalization fails.
    """
    try:
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone_number)

        # Check if the number already starts with a country code (e.g., +1)
        if digits_only.startswith('+'):
            # Assume it's already in a reasonable format and just clean it
            cleaned_number = re.sub(r'\D', '', digits_only)
            if len(cleaned_number) < 7:
              logging.error(f"Phone number {phone_number} is too short after cleaning.")
              return None  # Insufficient digits for a valid number
            return "+" + cleaned_number
        elif len(digits_only) == 10:  # Assume US number
            return "+1" + digits_only
        elif len(digits_only) == 11 and digits_only.startswith('1'):  # US number with leading 1
            return "+" + digits_only
        else:
            logging.warning(f"Could not automatically determine country code for phone number: {phone_number}")
            return None  # Unable to reliably determine the format.

    except Exception as e:
        logging.error(f"Error normalizing phone number {phone_number}: {e}")
        return None


def normalize_date(date_string: str, input_format: str, output_format: str = "%Y-%m-%d") -> Optional[str]:
    """
    Normalizes a date string to a specified format.

    Args:
        date_string: The date string to normalize.
        input_format: The format of the input date string (e.g., "%m/%d/%Y").
        output_format: The desired output format (e.g., "%Y-%m-%d").

    Returns:
        The normalized date string, or None if normalization fails.
    """
    try:
        date_object = datetime.datetime.strptime(date_string, input_format)
        normalized_date = date_object.strftime(output_format)
        return normalized_date
    except ValueError as ve:
        logging.error(f"Invalid date format. Could not parse date {date_string} using format {input_format}. Error: {ve}")
        return None
    except Exception as e:
        logging.error(f"Error normalizing date {date_string}: {e}")
        return None

def normalize_generic_string(text: str) -> str:
    """
    Normalizes a generic string by removing leading/trailing whitespace and converting to lowercase.
    This helps in consistent comparison and storage.

    Args:
        text: The string to normalize.

    Returns:
        The normalized string.
    """
    try:
        normalized_string = text.strip().lower()
        return normalized_string
    except Exception as e:
        logging.error(f"Error normalizing string: {e}")
        return text #Return the original string on error

def setup_argparse() -> argparse.ArgumentParser:
    """
    Sets up the command-line argument parser.

    Returns:
        An argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(description="Data Format Normalizer - Normalizes phone numbers, dates, and strings to a standard format.")
    parser.add_argument("--type", choices=["phone", "date", "string"], required=True, help="The type of data to normalize.")
    parser.add_argument("--input", required=True, help="The input data to normalize.")
    parser.add_argument("--input_format", help="The input date format (required for date normalization).  Example: '%m/%d/%Y'")
    parser.add_argument("--output_format", default="%Y-%m-%d", help="The output date format (default: '%Y-%m-%d'). Only applicable to date normalization.")
    parser.add_argument("--log_level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", help="Set the logging level (default: INFO)")

    return parser


def main() -> None:
    """
    Main function to parse arguments, normalize data, and print the result.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)

    data_type = args.type
    input_data = args.input

    try:
        if data_type == "phone":
            normalized_data = normalize_phone_number(input_data)
            if normalized_data:
                print(normalized_data)
            else:
                logging.error("Phone number normalization failed.")
                sys.exit(1) # Exit with an error code
        elif data_type == "date":
            if not args.input_format:
                parser.error("--input_format is required for date normalization.")
            normalized_data = normalize_date(input_data, args.input_format, args.output_format)
            if normalized_data:
                print(normalized_data)
            else:
                logging.error("Date normalization failed.")
                sys.exit(1) # Exit with an error code
        elif data_type == "string":
            normalized_data = normalize_generic_string(input_data)
            print(normalized_data)

        else:
            logging.error(f"Unsupported data type: {data_type}")
            sys.exit(1) # Exit with an error code

    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
        sys.exit(1) # Exit with an error code

if __name__ == "__main__":
    main()

# Example usage:
# python main.py --type phone --input "123-456-7890"
# python main.py --type date --input "01/01/2023" --input_format "%m/%d/%Y" --output_format "%Y-%m-%d"
# python main.py --type string --input "  Hello World  "