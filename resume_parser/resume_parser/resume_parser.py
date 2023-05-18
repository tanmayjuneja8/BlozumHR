import os, re
from . import utils
import spacy
import pprint
from spacy.matcher import Matcher
import multiprocessing as mp
import os


class ResumeParser(object):
    def __init__(self, resume, candidate_location, skills_from_jd):
        nlp = spacy.load("en_core_web_sm")
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            "name": None,
            "email": None,
            "mobile_number": None,
            "experience": None,
        }
        self.__resume = resume
        self.__text_raw = utils.extract_text(
            self.__resume, os.path.splitext(self.__resume)[1]
        )
        self.__text = " ".join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)

        text = self.__text.lower()
        found1 = 0
        print(candidate_location)
        if candidate_location != None:
            for i in candidate_location:
                cand_loc = i.strip().lower()
                if re.search(cand_loc, text):
                    found1 += 200
                    break

        # check skills here?
        tokens = text.split()
        found = 0
        for skill in skills_from_jd:
            escaped_skill = re.escape(skill)
            if len(escaped_skill.split()) == 1:
                if escaped_skill in tokens:
                    found += 100
            if len(escaped_skill.split()) > 1:
                if re.search(escaped_skill, text):
                    found += 100

        self.__score = {
            "Required JD Skills": found,
            "Candidate Location": found1,
            "Last Company Rating": 0,
            "Previous Company Domains": 0,
            "Your Competitors": 0,
            "College Rank": 0,
            "College Degree Relevance": 0,
            "Skill Relevance to Job": 0,
        }
        self.__get_basic_details()

    def get_score(self):
        return self.__score

    def get_resume_text(self):
        text = self.__text
        pattern = r"[^\w\d\s\n\+\.\,\:\%\/\$\-\–\—\―\(\)\{\}\[\]\@\#\'\"\>\<\`]"
        text = re.sub(pattern, "", text)
        return text

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        abcd = int(0.50 * len(self.__text))
        text2 = self.__text[0:abcd]
        experience = utils.extract_experience(text2)
        self.__details["experience"] = experience
        return


def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == "__main__":
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk("resumes"):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [pool.apply_async(resume_result_wrapper, args=(x,)) for x in resumes]

    results = [p.get() for p in results]

    pprint.pprint(results)
