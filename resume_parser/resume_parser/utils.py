from datetime import datetime
import time
import io
import re
import pandas as pd
import docx2txt
from . import constants as cs
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


def extract_text_from_pdf(pdf_path):
    """
    Helper function to extract the plain text from .pdf files

    :param pdf_path: path to PDF file to be extracted
    :return: iterator of string of extracted text
    """
    with open(pdf_path, "rb") as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(
                resource_manager, fake_file_handle, laparams=LAParams()
            )
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()


def extract_text_from_doc(doc_path):
    """
    Helper function to extract plain text from .doc or .docx files

    :param doc_path: path to .doc or .docx file to be extracted
    :return: string of extracted text
    """
    temp = docx2txt.process(doc_path)
    text = [line.replace("\t", " ") for line in temp.split("\n") if line]
    return " ".join(text)


def extract_text(file_path, extension):
    """
    Wrapper function to detect the file extension and call text extraction function accordingly

    :param file_path: path of file of which text is to be extracted
    :param extension: extension of file `file_name`
    """
    text = ""
    if extension == ".pdf":
        for page in extract_text_from_pdf(file_path):
            text += " " + page
    elif extension == ".docx" or extension == ".doc":
        text = extract_text_from_doc(file_path)
    return text


def extract_name(nlp_text, matcher):
    """
    Helper function to extract name from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param matcher: object of `spacy.matcher.Matcher`
    :return: string of full name
    """
    pattern = [cs.NAME_PATTERN]

    matcher.add("NAME", None, *pattern)

    matches = matcher(nlp_text)

    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text


def extract_mobile_number(text):
    """
    Helper function to extract mobile number from text

    :param text: plain text extracted from resume file
    :return: string of extracted mobile numbers
    """
    # Found this complicated regex on : https://zapier.com/blog/extract-links-email-phone-regex/
    phone = re.findall(
        re.compile(
            r"(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?"
        ),
        text,
    )
    if phone:
        number = "".join(phone[0])
        if len(number) > 10:
            return "+" + number
        else:
            return number


def extract_company_college_names(text):
    start = time.time()
    df = pd.read_csv("resume_parser/List_of_companies_in_India.csv")
    names = []
    to_remove = [
        ";",
        ":",
        "{",
        "}",
        "(",
        ")",
        "[",
        "]",
        ",",
        "-",
        "–",
        "/",
        ".",
        "—",
        ",",
    ]
    for i in to_remove:
        text = text.replace(i, "")
    tokens = text.split()
    for name in df.name:
        name = name.lstrip()
        name = name.rstrip()
        escaped_name = re.escape(name)
        if len(escaped_name.split()) == 1:
            if escaped_name in tokens:
                names.append(name)
        if len(escaped_name.split()) > 1:
            if re.search(escaped_name, text):
                names.append(name)
    end = time.time()
    print("Time taken to extract company college names : ", end - start)
    print(names)
    return names


def cleanup(token, lower=True):
    if lower:
        token = token.lower()
    return token.strip()


def extract_experience(resume_text):
    dict = {
        "jan": 1,
        "january": 1,
        "february": 2,
        "feb": 2,
        "march": 3,
        "mar": 3,
        "april": 4,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "july": 7,
        "jul": 7,
        "august": 8,
        "aug": 8,
        "september": 9,
        "sep": 9,
        "october": 10,
        "oct": 10,
        "november": 11,
        "nov": 11,
        "december": 12,
        "dec": 12,
    }
    resume_text = resume_text.replace(",", "")
    abc = re.findall(
        r"\b(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?|jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?)\s*(\d{4}|'\d{2}|\d{2}|\’\d{2})\s*(\D|to|-|–)\s*\b(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|Jul(y)?|Aug(ust)?|Sep(tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)|jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember))?\s*(\d{4}|'\d{2}|\d{2}|\’\d{2})?\s*(Present|present)?\s*[a-zA-Z]*",
        resume_text,
    )
    arr = []
    for i in range(len(abc)):
        for k in range(len(abc[i])):
            if (
                abc[i][k] == ""
                or abc[i][k] == "uary"
                or abc[i][k] == "ruary"
                or abc[i][k] == "ch"
                or abc[i][k] == "il"
                or abc[i][k] == "e"
                or abc[i][k] == "y"
                or abc[i][k] == "ust"
                or abc[i][k] == "tember"
                or abc[i][k] == "ober"
                or abc[i][k] == "ember"
            ):
                continue
            pattern = r"""[’'"](\d{2})"""
            if abc[i][k].lower() in dict:
                arr.append(dict[abc[i][k].lower()])
            if abc[i][k].isdigit():
                arr.append(int(abc[i][k]))
            if re.search(pattern, abc[i][k]):
                arr.append(int(abc[i][k][1:]))
            if abc[i][k].lower() == "present":
                arr.append(datetime.now().month)
                arr.append(datetime.now().year)
    num_periods = len(arr) // 4
    total_months = 0
    for i in range(num_periods):
        start_month = arr[i * 4]
        start_year = arr[i * 4 + 1]
        end_month = arr[i * 4 + 2]
        end_year = arr[i * 4 + 3]
        if start_year < 100:
            if start_year > (datetime.now().year % 100) and start_year < 100:
                start_year = 1900 + start_year
            else:
                start_year = 2000 + start_year
        if end_year < 100:
            if end_year > (datetime.now().year % 100) and end_year < 100:
                end_year = 1900 + end_year
            else:
                end_year = 2000 + end_year
        total_months += (end_year - start_year) * 12 + (end_month - start_month)
    return total_months


def string_found(string1, string2):
    if re.search(r"\b" + re.escape(string1) + r"\b", string2):
        return True
    return False
