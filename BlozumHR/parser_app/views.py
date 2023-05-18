from django.shortcuts import render, redirect
import xml.etree.ElementTree as ET
import re
import firebase_admin
from firebase_admin import firestore, credentials
from resume_parser import utils
from django.forms.models import model_to_dict

# from flair.data import Sentence
# from flair.models import SequenceTagger
import os, re
import time, json
import requests

import pandas as pd

from resume_parser.resume_parser import ResumeParser
from .models import Resume, UploadResumeModelForm
from django.contrib import messages
from django.conf import settings
from django.db import IntegrityError
import os
import pyrebase
import openai
from dotenv import load_dotenv
from django.http import JsonResponse
from urllib.parse import urlparse, parse_qs


load_dotenv()


config = {
    "apiKey": "AIzaSyD_XXBkWkJ6DxpWPdDi8nQFKzJm28FxcPw",
    "authDomain": "blozum-d1db4.firebaseapp.com",
    "projectId": "blozum-d1db4",
    "databaseURL": "https://blozum-d1db4-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "blozum-d1db4.appspot.com",
    "messagingSenderId": "853786318410",
    "appId": "1:853786318410:web:0cc7df7da8bc376c09b8b3",
    "measurementId": "G-HBEQMGF499",
}

# Initialising database,auth and firebase for further use
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
cred = credentials.Certificate(
    "./parser_app/blozum-d1db4-firebase-adminsdk-nm0fb-2a929027a7.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()


def signIn(request):
    return render(request, "Login.html")


def home(request):
    return render(request, "Home.html")


def postsignIn(request):
    email = request.POST.get("email")
    pasw = request.POST.get("pass")
    try:
        # if there is no error then signin the user with given email and password
        user = authe.sign_in_with_email_and_password(email, pasw)
        uid = user["localId"]
    except:
        message = (
            "Invalid Credentials!! Please Check your data/sign-up with a new account."
        )
        return render(request, "Login.html", {"message": message})
    session_id = user["idToken"]
    request.session["uid"] = str(session_id)
    # Pass uid as a query parameter in the redirect URL
    return homepage(request, uid)


def logout(request):
    try:
        del request.session["uid"]
    except:
        pass
    return render(request, "Login.html")


def signUp(request):
    return render(request, "Registration.html")


class title_job:
    def __init__(self):
        self.title = None

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title


job_title = title_job()


class comp_domain:
    def __init__(self):
        self.title = None

    def set_domain_companies(self, title):
        self.title = title

    def get_domain_companies(self):
        # extract company domain
        return self.title


domain = comp_domain()


class comp_type:
    def __init__(self):
        self.title = None

    def set_company_type(self, title):
        self.title = title

    def get_company_type(self):
        # extract company domain
        return self.title


comp_tags = comp_type()


class skillset:
    def __init__(self):
        self.skills = None

    def set_skills(self, arr):
        self.skills = arr

    def get_skills(self):
        # extract company domain
        return self.skills


job_skills12 = skillset()


class college_rank:
    def __init__(self):
        self.title = None

    def set_tier(self, title):
        self.title = title

    def get_college_tier(self):
        return self.title


coll_rank = college_rank()


class location12:
    def __init__(self):
        self.title = None

    def set_loc(self, title):
        self.title = title

    def get_loc(self):
        return self.title


loc12 = location12()


def postsignUp(request):
    email = request.POST.get("email")
    passs = request.POST.get("pass")
    name = request.POST.get("name")
    comp_name = request.POST.get("comp_name")
    try:
        # creating a user with the given email and password
        user = authe.create_user_with_email_and_password(email, passs)
        uid = user["localId"]
        data = {
            "name": name,
            "company_name": comp_name,
            "email": email,
            "credits": 1000,
        }
        doc_ref = db.collection("Users").document(uid)
        doc_ref.set(data)
    except Exception as e:
        print("An error occurred:", e)
        return render(request, "Registration.html", {"uid_val": uid})

        # Pass uid as a query parameter in the redirect URL
    return render(request, "Login.html", {"uid_val": uid})


def jd_form(request):
    form = UploadResumeModelForm()
    uid123 = request.GET.get("uid") or request.POST.get("uid")
    if request.method == "POST":
        company_type = request.POST.getlist("myDropdown[]")
        comp_tags.set_company_type(company_type)
        job_title12 = request.POST.get("job_title")
        job_title.set_title(job_title12)
        location = request.POST.get("location")
        education = request.POST.get("education")
        coll_rank.set_tier(education)
        skills = request.POST.get("skills")
        competitors = request.POST.get("competitors")
        competitors = str(competitors)
        competitors = competitors.split(",")
        for i in range(len(competitors)):
            competitors[i] = competitors[i].lstrip()
            competitors[i] = competitors[i].rstrip()
        domain.set_domain_companies(competitors)
        # Do some processing with the form data - skills
        skills = str(skills)
        location = str(location)
        location = location.lower()
        skills = skills.lower()
        # skills = re.sub(r"a-zA-Z0-9+#*!:_", " ", skills)
        # to_remove = [
        #     ";",
        #     ":",
        #     "{",
        #     "}",
        #     "(",
        #     ")",
        #     "[",
        #     "]",
        #     ",",
        #     "-",
        #     "–",
        #     "/",
        #     ".",
        #     "—",
        # ]
        # for i in to_remove:
        #     skills = skills.replace(i, " ")
        skills = skills.split(",")
        location = location.split(",")
        job_skills12.set_skills(skills)
        loc12.set_loc(location)
        # Redirect the user to a success page
        messages.success(
            request,
            "Job Description submitted successfully! Please upload the resumes and submit.✨",
        )
        return render(
            request,
            "base.html",
            {"form": form, "uid_val": uid123},
        )
    else:
        # Render the form
        render(request, "base.html", {"uid_val": uid123})


def extract_email(text):
    """
    Helper function to extract email id from text

    :param text: plain text extracted from resume file
    """
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(";")
        except IndexError:
            return None


def import_from_ATS(request, *args):
    uid12 = request.GET.get("uid") or request.POST.get("uid")
    for arg in args:
        uid12 = arg
    if request.method == "GET":
        link = request.GET.get("link")
        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)
        code_value = query_params.get("code", [""])[0]

        final_url = f"https://accounts.zoho.com/oauth/v2/token?grant_type=authorization_code&client_id=1000.KWR38CA8IIYFVYI3JU3J3234UCGA7O&client_secret=ccc6ef7ad62440da0950621a18b5035c912cee0d27&redirect_uri=https://blozum.com/&code={code_value}"
        # POST request
        response1 = requests.post(final_url)
        if response1.status_code == 200:
            json_auth = str(response1.json())
            json_auth = json_auth.replace("'", '"')
            data = json.loads(json_auth)
            access_token = data.get("access_token")
            if access_token is None:
                messages.warning(
                    request,
                    "Could not authenticate your Zoho Recruit account. Please carefully paste the authorization link within 60 seconds after it appears.",
                )
                return homepage(request, uid12)
        else:
            print("Request failed with status code:", response1.status_code)
            messages.warning(
                request,
                "Could not authenticate your Zoho Recruit account. Please carefully paste the authorisation link in under 60 seconds after it appears.",
            )
            return homepage(request, uid12)

        domain_comp = domain.get_domain_companies()
        title = job_title.get_title()
        degree = coll_rank.get_college_tier()
        location = loc12.get_loc()
        skills = job_skills12.get_skills()
        company_tags = comp_tags.get_company_type()
        print(access_token)
        # Candidate Information
        urls = "https://recruit.zoho.com/recruit/v2/Candidates"
        headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        # Send the GET request
        response = requests.get(urls, headers=headers)
        # Check the response
        candidates = []
        cand_names = []
        cand_summaries = []
        cand_experiences = []
        cand_emails = []
        cand_attachments = {}
        if response.status_code == 200:
            data = response.json()["data"]
            for i in range(len(data)):
                candidates.append(data[i]["id"])
                cand_names.append(data[i]["Full_Name"])
                cand_summaries.append(data[i]["Skill_Set"])
                cand_experiences.append(data[i]["Experience_in_Years"])
                cand_emails.append(data[i]["Email"])
        else:
            print("Request failed with status code:", response.json())

        ## Dictionary of attachment_ids with candidate_ids
        for cand in candidates:
            urls1 = f"https://recruit.zoho.com/recruit/v2/Candidates/{cand}/Attachments"
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
            if response.status_code == 200:
                response = requests.get(urls1, headers=headers)
                cand_attachments[cand] = response.json()["data"][0]["id"]
            else:
                print("Request failed with status code:", response.json())

        ########################################################################
        # CV ki info extract karlo.
        ########################################################################
        if len(cand_attachments) != 0:
            ref = db.collection("Users").document(uid12)
            credits = ref.get().to_dict()["credits"]
            if credits < len(cand_attachments):
                messages.warning(
                    request,
                    "You have lesser number of credits left. Please recharge!",
                )
            if credits >= len(cand_attachments):
                credits -= len(cand_attachments)
                print("Credits reduced.")
                ref.update(
                    {
                        "credits": credits,
                    }
                )
        resumes_list = []
        j = 0
        for i in cand_attachments:
            # College, Company Names
            ########### This also has some information about their past experiences extracted from their CVs.
            cand_score = {
                "Required JD Skills": 0,
                "Candidate Location": 0,
                "Last Company Rating": 0,
                "Previous Company Domains": 0,
                "Your Competitors": 0,
                "College Rank": 0,
                "College Degree Relevance": 0,
                "Skill Relevance to Job": 0,
            }

            urls = f"https://recruit.zoho.com/recruit/private/xml/Candidates/getTabularRecords?authtoken={access_token}&id={i}&tabularNames=(Experience Details,Educational Details)&scope=recruitapi"
            headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
            response12 = requests.get(urls, headers=headers)
            # Check the response
            if response12.status_code == 200:
                root = ET.fromstring(response12.content)
                # Find the relevant XML elements and extract college names
                college_names = []
                for tr in root.findall(".//TR"):
                    college_name = tr.find("./TL[@val='Institute / School']")
                    if college_name is not None and college_name.text is not None:
                        college_name.text = college_name.text.replace(",", "")
                        college_names.append(college_name.text)

                # Print the extracted college names
                df = pd.read_csv(
                    "/Users/tanmayjuneja/Documents/blozumhr/BlozumHR/resume_parser/parser_app/List_of_companies_in_India.csv"
                )
                for college_name in college_names:
                    if college_name is None:
                        continue
                    if college_name.lower() in df["name"].tolist():
                        filtered_data = df.loc[
                            df["name"] == college_name.lower()
                        ].rating
                        if filtered_data.size == 1:
                            rating = filtered_data.item()
                            cand_score["College Rank"] += 300 - int(rating)
                        else:
                            print(filtered_data)

                company_names = []
                experience_details = root.find(".//FL[@val='Experience Details']")
                for tr in experience_details.findall("TR"):
                    company = tr.find("TL[@val='Company']")
                    if company is not None and company.text is not None:
                        company.text = company.text.replace(",", "")
                        company_names.append(company.text)

                arr = []
                for i in range(len(company_names)):
                    comp_name = company_names[i]
                    if comp_name is None:
                        continue
                    comp_name = comp_name.split(" ")
                    if company_names[i].lower() in df["name"].tolist():
                        df3 = df[df["name"] == company_names[i].lower()]
                        ## last work experience ka score
                        if i == 0:
                            cand_score["Last Company Rating"] += int(
                                df3.iloc[0].rating.item() * 100
                            )
                        # Extracting unique tags from all the candidate's companies.
                        for i in df3.tags:
                            arr2 = str(i).split(",")
                            for k in arr2:
                                arr.append(k.strip())
                        continue
                    df2 = df[df["name"].str.startswith(comp_name[0].lower())]
                    if not df2.empty:
                        if df2.shape[0] == 1:
                            ## last work experience ka score
                            if i == 0:
                                cand_score["Last Company Rating"] += int(
                                    df2.iloc[0].rating.item() * 100
                                )
                            for i in df2.tags:
                                arr2 = str(i).split(",")
                                for k in arr2:
                                    arr.append(k.strip())
                            continue
                        if df2.shape[0] > 1:
                            final_df = df2[
                                df2["name"].apply(
                                    lambda x: len(x.split()) > 1
                                    and x.split()[1] == comp_name[1].lower()
                                )
                            ]
                            if not final_df.empty:
                                ## last work experience ka score
                                if i == 0:
                                    cand_score["Last Company Rating"] += int(
                                        final_df.iloc[0].rating.item() * 100
                                    )
                                for i in final_df.iloc[0].tags:
                                    arr2 = str(i).split(",")
                                    for k in arr2:
                                        arr.append(k.strip())
                                continue
                            if i == 0:
                                cand_score["Last Company Rating"] += int(
                                    df2.iloc[0].rating.item() * 100
                                )
                            for i in df2.iloc[0].tags:
                                arr2 = str(i).split(",")
                                for k in arr2:
                                    arr.append(k.strip())

                    # Intersection between the tags of candidate's companies and JD input tags.
                    candidate_company_tags = set(arr)
                    company_tags = comp_tags.get_company_type()
                    common_values = 0
                    if company_tags is not None:
                        for i in candidate_company_tags:
                            for j in company_tags:
                                if i.split() == j.split():
                                    common_values += 1

                        cand_score["Previous Company Domains"] += (
                            float((common_values / len(company_tags))) * 100
                        )

                ## Check competitors and add to the score.
                if domain_comp is not None:
                    for i in range(len(domain_comp)):
                        competitor = domain_comp[i]
                        for k in company_names:
                            if k.strip().lower() == competitor.strip().lower():
                                cand_score["Your Competitors"] += 200

                total = -1 * sum(cand_score.values())
                resumes_list.append(
                    {
                        "name": cand_names[j],
                        "companies": company_names,
                        "college": college_names,
                        "summary": cand_summaries[j],
                        "experience": cand_experiences[j],
                        "score": cand_score,
                        "email": str(cand_emails[j]),
                        "total_score": total,
                    }
                )
                if j < len(cand_attachments):
                    j += 1

            else:
                print("Request failed with status code:", response.json())

        ## Sort the resumes list first.
        resumes_list.sort(key=lambda x: x["total_score"])
        for resume in resumes_list:
            del resume["total_score"]
        print(resumes_list)
        resumes_json = json.dumps(resumes_list)

        context = {
            "resumes": resumes_list,
            "uid_val": uid12,
            "resumes_json": resumes_json,
        }

        #     urls = f"https://recruit.zoho.com/recruit/v2/Candidates/{i}/Attachments/{cand_attachments[i]}"
        #     headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
        #     response = requests.get(urls, headers=headers)
        #     # Check the response
        #     if response.status_code == 200:
        #         pdf_path = os.path.join(os.getcwd(), "resume.pdf")
        #         with open(pdf_path, "wb") as file:
        #             file.write(response.content)
        #         ## Resume text pre-processing and saving information for each candidate.
        #         text = utils.extract_text(pdf_path, os.path.splitext(pdf_path)[1])
        #         pattern = r"[^\w\d\s\n\+\.\,\:\%\/\$\-\–\—\―\(\)\{\}\[\]\@\#\'\"\>\<\`]"
        #         text = re.sub(pattern, "", text)

        # 1. What are all the skills and competencies of the candidate?
        # 2. Is the candidate's profile related to the role of "{title}"? Answer only in Yes/No.
        # 3. Does the candidate have a degree in {degree} or related field? Answer only Yes/No according to your judgement.
        # 7. Answer in Yes/No/Maybe : Are any of the candidate's previous job/internship designations related to the role of "{title}"?
        # 8. If Yes/Maybe : Is the role of "{title}" higher than the candidate's last job designation (first job designation found in text) in terms of hierarchy in an organization? Answer in only Yes/No.

        #             openai.api_key = os.getenv("OPENAI_API_KEY")
        #             prompt = f"""Imagine you are an HR Recruiter named BlozumHR. Answer the following questions according to the text below regarding a job candidate (delimited by '''). Answer only "None" if no answer is found in the questions below. Be concise, answer short, and don't give any explanations for your answers.

        # 1. Extract all of the candidate's previous jobs' company names. Please exclude university/college names and include only company (startup/organization names).
        # 2. Which colleges (exact university/institute name) has the candidate graduated from?
        # Give different institutions separated by ";". For example, "IIT Delhi; IIM Ahmedabad; Harvard" should be the only output.

        # '''{text}'''
        # """

        # completion = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}],
        # )
        # print(completion)
        #     os.remove(pdf_path)

        #     print("Request successful!")
        # else:
        #     print("Request failed with status code:", response.json())

        ########################################################################

    #  return render(request, "base.html", context)

    else:
        form = UploadResumeModelForm()
        return render(request, "base.html", {"form": form, "uid_val": uid12})
    return render(request, "base.html", context)


def homepage(request, *args):
    form = UploadResumeModelForm()
    uid12 = request.GET.get("uid") or request.POST.get("uid")
    for arg in args:
        uid12 = arg
    if request.method == "POST":
        Resume.objects.all().delete()
        file_form = UploadResumeModelForm(request.POST, request.FILES)
        files = request.FILES.getlist("resume")
        if len(files) != 0:
            ref = db.collection("Users").document(uid12)
            credits = ref.get().to_dict()["credits"]
            if credits < len(files):
                messages.warning(
                    request, "You have lesser number of credits left. Please recharge!"
                )
            if credits >= len(files):
                credits -= len(files)
                ref.update(
                    {
                        "credits": credits,
                    }
                )

        # resumes_data = []
        if file_form.is_valid():
            # tagger2 = SequenceTagger.load(
            #     "/Users/tanmayjuneja/Documents/blozumhr/BlozumHR/resume_parser/parser_app/flairner/pytorch_model.bin"
            # )
            for file in files:
                try:
                    # saving the file
                    resume = Resume(resume=file)
                    resume.save()

                    # extracting resume entities
                    parser = ResumeParser(
                        os.path.join(settings.MEDIA_ROOT, resume.resume.name),
                        loc12.get_loc(),
                        job_skills12.get_skills(),
                    )
                    data = parser.get_extracted_data()
                    resume_score = parser.get_score()
                    domain_comp = domain.get_domain_companies()
                    title = job_title.get_title()
                    degree = coll_rank.get_college_tier()
                    start = time.time()
                    # abcdef = parser.get_resume_text()
                    # sentences = Sentence(abcdef)
                    # tagger2.predict(sentences)

                    openai.api_key = os.getenv("OPENAI_API_KEY")
                    ## Enter ChatGPT
                    prompt = f"""Imagine you are an HR Recruiter named BlozumHR. Answer the following questions according to the text below regarding a job candidate. Answer only "None" if no answer is found in the questions below. Be concise, answer short, and don't give any explanations for your answers.

1. What is the name of the candidate? Answer in the form of 'John Doe'. 
2. What are all the skills and competencies of the candidate? 
3. Is the candidate's profile related to the role of "{title}"? Answer only in Yes/No.
4. Extract all of the candidate's previous jobs' company names.
5. Which colleges (exact university/institute name) has the candidate graduated from? 
Give different institutions separated by ";". For example, "IIT Delhi; IIM Ahmedabad; Harvard" should be the only output.
6. Does the candidate have a degree in {degree} or related field? Answer only Yes/No according to your judgement.
7. Extract and give the contact details of the candidate. Do not include the candidate's address here. 
8. Answer in Yes/No/Maybe : Are any of the candidate's previous job/internship designations related to the role of "{title}"? 
9. If Yes/Maybe : Is the role of "{title}" higher than the candidate's last job designation (first job designation found in text) in terms of hierarchy in an organization? Answer in only Yes/No.





"""

                    text = parser.get_resume_text()
                    prompt += text

                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                    )

                    end = time.time()
                    data = completion.choices[0].message.content
                    data = str(data)
                    print(f'{completion["usage"]["total_tokens"]} prompt tokens used.')
                    print(completion)

                    ## Extract from ChatGPT outputs.
                    point = data.split("\n")
                    print(" Time taken for BlozumGPT is ", end - start)
                    df = pd.read_csv(
                        "/Users/tanmayjuneja/Documents/blozumhr/BlozumHR/resume_parser/parser_app/List_of_companies_in_India.csv"
                    )

                    # 4. (Org names) ITC, HUL
                    # Candidate's last company score.
                    str_comp = point[3][3:]
                    chatgpt_companies = str_comp.split(",")
                    chatgpt_companies_final = []
                    for company_name in chatgpt_companies:
                        chatgpt_companies_final.append(company_name.strip())

                    ## Sab companies ke liye nikaalne padhenge tags. Peheli company ke liye rating dedo.
                    # Baaki ke tags compare karlo.
                    arr = []
                    for i in range(len(chatgpt_companies_final)):
                        comp_name = chatgpt_companies_final[i]
                        comp_name = comp_name.split(" ")
                        if chatgpt_companies_final[i].lower() in df["name"].tolist():
                            df3 = df[df["name"] == chatgpt_companies_final[i].lower()]
                            ## last work experience ka score
                            if i == 0:
                                resume_score["Last Company Rating"] += int(
                                    df3.iloc[0].rating.item() * 100
                                )
                            # Extracting unique tags from all the candidate's companies.
                            for i in df3.tags:
                                arr2 = str(i).split(",")
                                for k in arr2:
                                    arr.append(k.strip())
                            continue
                        df2 = df[df["name"].str.startswith(comp_name[0].lower())]
                        if not df2.empty:
                            if df2.shape[0] == 1:
                                ## last work experience ka score
                                if i == 0:
                                    resume_score["Last Company Rating"] += int(
                                        df2.iloc[0].rating.item() * 100
                                    )
                                for i in df2.tags:
                                    arr2 = str(i).split(",")
                                    for k in arr2:
                                        arr.append(k.strip())
                                continue
                            if df2.shape[0] > 1:
                                final_df = df2[
                                    df2["name"].apply(
                                        lambda x: len(x.split()) > 1
                                        and x.split()[1] == comp_name[1].lower()
                                    )
                                ]
                                if not final_df.empty:
                                    ## last work experience ka score
                                    if i == 0:
                                        resume_score["Last Company Rating"] += int(
                                            final_df.iloc[0].rating.item() * 100
                                        )
                                    for i in final_df.iloc[0].tags:
                                        arr2 = str(i).split(",")
                                        for k in arr2:
                                            arr.append(k.strip())
                                    continue
                                if i == 0:
                                    resume_score["Last Company Rating"] += int(
                                        df2.iloc[0].rating.item() * 100
                                    )
                                for i in df2.iloc[0].tags:
                                    arr2 = str(i).split(",")
                                    for k in arr2:
                                        arr.append(k.strip())

                        # Intersection between the tags of candidate's companies and JD input tags.
                        candidate_company_tags = set(arr)
                        company_tags = comp_tags.get_company_type()
                        common_values = 0
                        for i in candidate_company_tags:
                            for j in company_tags:
                                if i.split() == j.split():
                                    common_values += 1

                        resume_score["Previous Company Domains"] += (
                            float((common_values / len(company_tags))) * 100
                        )

                    ## Check competitors and add to the score.
                    for i in range(len(domain_comp)):
                        competitor = domain_comp[i]
                        for k in chatgpt_companies_final:
                            if k.strip().lower() == competitor.strip().lower():
                                print(competitor)
                                resume_score["Your Competitors"] += 200

                    # 5. (College names) Indian Institute of Technology, Kharagpur, Sri Chaitanya Junior College, Sri Chaitanya Techno School
                    ## College name and rating

                    str123 = point[4][3:]
                    college_names = str123.split(";")

                    for college_name in college_names:
                        college_name = college_name.replace(",", "")
                        if college_name in df["name"].tolist():
                            resume_score["College Rank"] += 300 - int(
                                df.loc[df["name"] == college_name].rating.item()
                            )

                    # 6. Yes/No/None (Is it relevant to JD college degree?)
                    if "Yes" in point[5][3:]:
                        resume_score["College Degree Relevance"] += 100

                    # 3. (Yes/No/Maybe/None) None
                    # 8. (related?) Yes/Maybe
                    # 9. (JD role higher or not?) Maybe

                    if "Yes" in point[2][3:]:
                        resume_score["Skill Relevance to Job"] += 100
                        if "Yes" or "Maybe" in point[7][3:]:
                            resume_score["Skill Relevance to Job"] += 50
                            if "Yes" or "Maybe" in point[8][3:]:
                                resume_score["Skill Relevance to Job"] += 20
                            if "No" or "None" in point[8][3:]:
                                resume_score["Skill Relevance to Job"] += 50
                    else:
                        if "Yes" or "Maybe" in point[7][3:]:
                            resume_score["Skill Relevance to Job"] += 20

                    ## Compare skills
                    # 2. (skills) Product design/launch, consumer immersions, user journey mapping, requirements gathering, UX design, PRD preparation, digital transformation evaluation, product ownership, ideation, pricing strategy
                    skills_from_jd = job_skills12.get_skills()
                    skills_from_gpt = point[1][3:].lower()
                    for skill in skills_from_jd:
                        skill = skill.strip()
                        if skill in skills_from_gpt:
                            resume_score["Required JD Skills"] += 20

                    # Add company and college scores to the resume score and save it accordingly.
                    resume.score = resume_score
                    resume.score1 = -1 * sum(resume_score.values())
                    resume.name = point[0][3:]
                    resume.contact = point[6][3:]
                    resume.email = extract_email(point[6][3:])
                    resume.college = point[4][3:]
                    resume.companies = point[3][3:]
                    # resume.experience = data.get("experience")
                    resume.summary = point[1][3:]
                    resume.save()
                except IntegrityError:
                    messages.warning(request, "Duplicate resume found:", file.name)
                    return redirect("homepage")

            resumes = Resume.objects.all().order_by("score1")
            messages.success(
                request,
                "Resumes uploaded! Please don't refresh the page, as it will restart the process.",
            )
            resumes_list = []
            for resume in resumes:
                resumes_list.append(
                    {
                        "name": str(resume.name),
                        "companies": str(resume.companies),
                        "college": str(resume.college),
                        "summary": str(resume.summary),
                        "experience": str(resume.experience),
                        "score": resume.score,
                        "resume_url": str(resume.resume.url),
                        "email": str(resume.email),
                    }
                )

            resumes_json = json.dumps(resumes_list)
            context = {
                "resumes": resumes,
                "uid_val": uid12,
                "resumes_json": resumes_json,
            }
            return render(request, "base.html", context)
    else:
        form = UploadResumeModelForm()
    messages.success(
        request,
        "You've signed in. Welcome! ✨",
    )
    return render(request, "base.html", {"form": form, "uid_val": uid12})
